"""
OSYA Agents — Database Module
Simple SQLite-based storage for agents, tasks, and runs.
"""
import sqlite3
import json
import uuid
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class Database:
    def __init__(self, db_path: str = "osya.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent read/write performance
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.lock = threading.Lock()
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                instructions TEXT DEFAULT '',
                heartbeat_sec INTEGER DEFAULT 0,
                reports_to TEXT,
                tools TEXT DEFAULT '["bash","read","write","web_search"]',
                max_turns INTEGER DEFAULT 100,
                status TEXT DEFAULT 'idle',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (reports_to) REFERENCES agents(id)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'todo',
                priority TEXT DEFAULT 'normal',
                assignee_id TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                completed_at TEXT,
                FOREIGN KEY (assignee_id) REFERENCES agents(id)
            );

            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                task_id TEXT,
                status TEXT DEFAULT 'running',
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                error TEXT,
                started_at TEXT DEFAULT (datetime('now')),
                finished_at TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_name TEXT,
                tool_input TEXT,
                tool_output TEXT,
                seq INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
        """)
        self.conn.commit()

    def create_agent(self, name: str, provider: str, model: str, 
                     instructions: str = "", heartbeat_sec: int = 0,
                     reports_to: str = None, tools: list = None,
                     max_turns: int = 100) -> str:
        agent_id = str(uuid.uuid4())
        tools_json = json.dumps(tools or ["bash", "read", "write", "web_search"])
        with self.lock:
            self.conn.execute("""
                INSERT INTO agents (id, name, provider, model, instructions, 
                                  heartbeat_sec, reports_to, tools, max_turns)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (agent_id, name, provider, model, instructions, 
                  heartbeat_sec, reports_to, tools_json, max_turns))
            self.conn.commit()
        return agent_id

    def get_agent(self, agent_id: str = None, name: str = None) -> Optional[dict]:
        if agent_id:
            row = self.conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
        elif name:
            row = self.conn.execute("SELECT * FROM agents WHERE name = ?", (name,)).fetchone()
        else:
            return None
        if row:
            d = dict(row)
            d['tools'] = json.loads(d['tools'])
            return d
        return None

    def list_agents(self) -> List[dict]:
        rows = self.conn.execute("SELECT * FROM agents ORDER BY name").fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d['tools'] = json.loads(d['tools'])
            result.append(d)
        return result

    def update_agent(self, agent_id: str, **kwargs) -> bool:
        allowed = {'name', 'provider', 'model', 'instructions', 'heartbeat_sec',
                   'reports_to', 'tools', 'max_turns', 'status'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if 'tools' in updates:
            updates['tools'] = json.dumps(updates['tools'])
        if not updates:
            return False
        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f'{k} = ?' for k in updates)
        values = list(updates.values()) + [agent_id]
        with self.lock:
            self.conn.execute(f"UPDATE agents SET {set_clause} WHERE id = ?", values)
            self.conn.commit()
        return True

    def delete_agent(self, agent_id: str) -> bool:
        with self.lock:
            self.conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
            self.conn.commit()
        return True

    # Tasks
    def create_task(self, title: str, description: str = "", 
                    priority: str = "normal", assignee_id: str = None) -> str:
        task_id = str(uuid.uuid4())
        with self.lock:
            self.conn.execute("""
                INSERT INTO tasks (id, title, description, priority, assignee_id)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, title, description, priority, assignee_id))
            self.conn.commit()
        return task_id

    def get_task(self, task_id: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def list_tasks(self, status: str = None, assignee_id: str = None) -> List[dict]:
        query = "SELECT t.*, a.name as assignee_name FROM tasks t LEFT JOIN agents a ON t.assigned_to = a.id WHERE 1=1"
        params = []
        if status:
            query += " AND t.status = ?"
            params.append(status)
        if assignee_id:
            query += " AND t.assigned_to = ?"
            params.append(assignee_id)
        query += " ORDER BY t.created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_task(self, task_id: str, **kwargs) -> bool:
        allowed = {'title', 'description', 'status', 'priority', 'assignee_id', 'completed_at'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        updates['updated_at'] = datetime.now().isoformat()
        if 'status' in updates and updates['status'] == 'done':
            updates['completed_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f'{k} = ?' for k in updates)
        values = list(updates.values()) + [task_id]
        with self.lock:
            self.conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
            self.conn.commit()
        return True

    # Runs
    def create_run(self, agent_id: str, task_id: str = None) -> str:
        run_id = str(uuid.uuid4())
        with self.lock:
            self.conn.execute("""
                INSERT INTO runs (id, agent_id, task_id) VALUES (?, ?, ?)
            """, (run_id, agent_id, task_id))
            self.conn.commit()
        return run_id

    def update_run(self, run_id: str, **kwargs) -> bool:
        allowed = {'status', 'input_tokens', 'output_tokens', 'cost_usd', 'error', 'finished_at'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        set_clause = ', '.join(f'{k} = ?' for k in updates)
        values = list(updates.values()) + [run_id]
        with self.lock:
            self.conn.execute(f"UPDATE runs SET {set_clause} WHERE id = ?", values)
            self.conn.commit()
        return True

    def add_message(self, run_id: str, role: str, content: str, 
                    tool_name: str = None, tool_input: str = None, 
                    tool_output: str = None) -> str:
        msg_id = str(uuid.uuid4())
        with self.lock:
            seq = self.conn.execute(
                "SELECT COALESCE(MAX(seq), 0) + 1 FROM messages WHERE run_id = ?", 
                (run_id,)
            ).fetchone()[0]
            self.conn.execute("""
                INSERT INTO messages (id, run_id, role, content, tool_name, 
                                    tool_input, tool_output, seq)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, run_id, role, content, tool_name, 
                  json.dumps(tool_input) if tool_input else None,
                  tool_output, seq))
            self.conn.commit()
        return msg_id

    def get_messages(self, run_id: str) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM messages WHERE run_id = ? ORDER BY seq", (run_id,)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            if d['tool_input']:
                d['tool_input'] = json.loads(d['tool_input'])
            result.append(d)
        return result

    # Comments
    def add_comment(self, task_id: str, author: str, content: str) -> str:
        comment_id = str(uuid.uuid4())
        with self.lock:
            self.conn.execute("""
                INSERT INTO comments (id, task_id, author, content) VALUES (?, ?, ?, ?)
            """, (comment_id, task_id, author, content))
            self.conn.commit()
        return comment_id

    def get_comments(self, task_id: str) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM comments WHERE task_id = ? ORDER BY created_at", (task_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def list_runs(self, limit: int = 50) -> list:
        """List recent runs with agent names."""
        cursor = self.conn.execute("""
            SELECT r.*, a.name as agent_name 
            FROM runs r LEFT JOIN agents a ON r.agent_id = a.id 
            ORDER BY r.started_at DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_run_stats(self) -> dict:
        """Get aggregated run statistics."""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
                COALESCE(SUM(cost_usd), 0) as total_cost,
                COALESCE(SUM(input_tokens), 0) as tokens_in,
                COALESCE(SUM(output_tokens), 0) as tokens_out
            FROM runs
        """)
        row = cursor.fetchone()
        total = row[0] or 0
        completed = row[1] or 0
        return {
            "total": total,
            "completed": completed,
            "failed": row[2] or 0,
            "success_rate": round(completed / max(total, 1) * 100, 1),
            "total_cost": round(row[3] or 0, 4),
            "tokens_in": row[4] or 0,
            "tokens_out": row[5] or 0,
        }

    def close(self):
        """Close database connection."""
        self.conn.close()
