"""
AXIOM Platform — Main Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import sqlite3
import json
import os
from pathlib import Path

app = FastAPI(title="AXIOM", version="1.0.0")

DB_PATH = os.getenv("AXIOM_DB", "osya.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# === Health ===
@app.get("/api/health")
async def health():
    db = get_db()
    agents = db.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    running = db.execute("SELECT COUNT(*) FROM agents WHERE status='running'").fetchone()[0]
    tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = db.execute("SELECT COUNT(*) FROM tasks WHERE status='done'").fetchone()[0]
    db.close()
    return {"status":"ok","agents_total":agents,"agents_running":running,"tasks_total":tasks,"tasks_done":done}

# === Agents ===
@app.get("/api/agents")
async def list_agents():
    db = get_db()
    rows = db.execute("SELECT * FROM agents ORDER BY name").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    db = get_db()
    row = db.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
    db.close()
    if not row:
        raise HTTPException(404, "Agent not found")
    return dict(row)

@app.post("/api/agents/{agent_id}/run")
async def run_agent(agent_id: str, body: dict):
    from core.runner import AgentRunner
    db = get_db()
    agent = db.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
    db.close()
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    runner = AgentRunner(DB_PATH)
    result = runner.run(dict(agent), body.get("task", "Continue work"))
    return result

# === Tasks ===
@app.get("/api/tasks")
async def list_tasks():
    db = get_db()
    rows = db.execute("""
        SELECT t.*, a.name as assigned_to_name 
        FROM tasks t LEFT JOIN agents a ON t.assigned_to=a.id
        ORDER BY t.created_at DESC LIMIT 100
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.post("/api/tasks")
async def create_task(body: dict):
    import uuid
    db = get_db()
    task_id = str(uuid.uuid4())
    db.execute("""
        INSERT INTO tasks (id, title, description, status, assigned_to, created_by)
        VALUES (?, ?, ?, 'pending', ?, ?)
    """, (task_id, body.get("title",""), body.get("description",""), 
          body.get("assigned_to"), body.get("created_by")))
    db.commit()
    db.close()
    return {"id": task_id, "status": "created"}

# === Runs ===
@app.get("/api/runs")
async def list_runs():
    db = get_db()
    rows = db.execute("""
        SELECT r.*, a.name as agent_name
        FROM runs r JOIN agents a ON r.agent_id=a.id
        ORDER BY r.started_at DESC LIMIT 50
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]

# === Failover ===
@app.get("/api/failover/status")
async def failover_status():
    from core.failover import failover
    return failover.get_stats()

@app.get("/api/failover/current-key")
async def failover_current():
    from core.failover import failover
    key = failover.current_key
    if not key:
        raise HTTPException(404, "No keys")
    return {"masked": key.masked, "is_available": key.is_available}

@app.post("/api/failover/add-key")
async def failover_add(body: dict):
    from core.failover import failover
    ok = failover.add_key(body.get("api_key",""))
    return {"status":"ok" if ok else "exists"}

@app.post("/api/failover/remove-key")
async def failover_remove(body: dict):
    from core.failover import failover
    ok = failover.remove_key(body.get("api_key",""))
    if not ok:
        raise HTTPException(404, "Key not found")
    return {"status":"ok"}

@app.post("/api/failover/switch-next")
async def failover_switch():
    from core.failover import failover
    failover._switch_to_next()
    return {"status":"ok","current_key": failover.current_key.masked if failover.current_key else None}

# === Secrets ===
@app.get("/api/secrets/{provider}")
async def get_secrets(provider: str):
    from core.secrets import get_api_keys
    keys = get_api_keys(provider)
    return {"provider":provider,"count":len(keys),"keys":[f"...{k[-4:]}" for k in keys]}

# === Departments ===
@app.post("/api/agents/create-department")
async def create_department(body: dict):
    import uuid
    db = get_db()
    leader_id = str(uuid.uuid4())
    db.execute("""
        INSERT INTO agents (id,name,provider,model,instructions,heartbeat_sec,reports_to,tools,max_turns,status)
        VALUES (?,?,'openrouter','nvidia/nemotron-3-super-120b-a12b:free',?,7200,?,?,'active')
    """, (leader_id, body.get("leader_name","Leader"), body.get("leader_instructions",""),
          body.get("reports_to"), '["bash","read","write","web_search","web_fetch"]'))
    
    members = []
    for m in body.get("members",[]):
        mid = str(uuid.uuid4())
        db.execute("""
            INSERT INTO agents (id,name,provider,model,instructions,heartbeat_sec,reports_to,tools,max_turns,status)
            VALUES (?,?,'openrouter','nvidia/nemotron-3-super-120b-a12b:free',?,7200,?,?,'active')
        """, (mid, m.get("name",""), m.get("instructions",""), leader_id,
              '["bash","read","write","web_search","web_fetch"]'))
        members.append({"name":m.get("name"),"id":mid})
    
    db.commit()
    db.close()
    return {"status":"created","department":body.get("department_name"),"leader":leader_id,"members":members}

# === Dashboard ===
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return FileResponse("/opt/alvo/dashboard.html")

app.mount("/static", StaticFiles(directory="/opt/alvo/axiom/static"), name="static")
