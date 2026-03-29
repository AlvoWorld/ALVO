"""
Agent Factory — создание новых агентов по запросу.
Только с одобрения CEO.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import uuid

router = APIRouter(prefix="/api/agents", tags=["agents"])
DB_PATH = "osya.db"


class CreateAgentRequest(BaseModel):
    name: str
    role: str  # Описание роли
    instructions: str
    model: str = "nvidia/nemotron-3-super-120b-a12b:free"
    provider: str = "openrouter"
    reports_to: Optional[str] = None  # ID родителя
    tools: List[str] = ["bash", "read", "write", "web_search", "web_fetch"]
    max_turns: int = 150
    heartbeat_sec: int = 7200
    approved_by_ceo: bool = False  # Требуется одобрение CEO


@router.post("/create")
async def create_agent(req: CreateAgentRequest):
    """Создать нового агента (требуется одобрение CEO)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Проверяем что имя уникально
    c.execute("SELECT id FROM agents WHERE name=?", (req.name,))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, f"Агент '{req.name}' уже существует")
    
    # Проверяем что reports_to существует
    if req.reports_to:
        c.execute("SELECT id FROM agents WHERE id=?", (req.reports_to,))
        if not c.fetchone():
            conn.close()
            raise HTTPException(400, f"Родительский агент не найден")
    
    agent_id = str(uuid.uuid4())
    
    c.execute("""
        INSERT INTO agents (id, name, provider, model, instructions, 
                           heartbeat_sec, reports_to, tools, max_turns, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'created')
    """, (agent_id, req.name, req.provider, req.model, req.instructions,
          req.heartbeat_sec, req.reports_to, str(req.tools), req.max_turns))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "created",
        "agent_id": agent_id,
        "name": req.name,
        "reports_to": req.reports_to,
        "message": f"Агент '{req.name}' создан и назначен в команду."
    }


@router.post("/{agent_id}/request-subordinate")
async def request_subordinate(agent_id: str, req: CreateAgentRequest):
    """Запрос на создание подчинённого (для рассмотрения CEO)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Проверяем агента
    c.execute("SELECT name FROM agents WHERE id=?", (agent_id,))
    agent = c.fetchone()
    if not agent:
        conn.close()
        raise HTTPException(404, "Агент не найден")
    
    # Создаём задачу для CEO
    task_id = str(uuid.uuid4())
    c.execute("SELECT id FROM agents WHERE name='CEO'")
    ceo_id = c.fetchone()[0]
    
    c.execute("""
        INSERT INTO tasks (id, title, description, status, assigned_to, created_by)
        VALUES (?, ?, ?, 'pending', ?, ?)
    """, (task_id, 
          f"Запрос на нового агента: {req.name}",
          f"Агент '{agent[0]}' запрашивает создание подчинённого:\n"
          f"Имя: {req.name}\nРоль: {req.role}\nИнструкции: {req.instructions}\n"
          f"Подчиняется: {agent[0]}",
          ceo_id, agent_id))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "requested",
        "task_id": task_id,
        "message": f"Запрос отправлен CEO на рассмотрение."
    }


@router.post("/{task_id}/approve-subordinate")
async def approve_subordinate(task_id: str):
    """CEO одобряет создание агента."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Получаем задачу
    c.execute("SELECT title, description, created_by FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    if not task:
        conn.close()
        raise HTTPException(404, "Задача не найдена")
    
    # Парсим информацию из описания
    desc = task[1]
    lines = desc.split('\n')
    name = lines[0].split(': ')[1] if len(lines) > 0 else "Unknown"
    
    # Создаём агента
    agent_id = str(uuid.uuid4())
    instructions = '\n'.join(lines[2:]).replace('Инструкции: ', '') if len(lines) > 2 else ""
    
    c.execute("""
        INSERT INTO agents (id, name, provider, model, instructions, 
                           heartbeat_sec, reports_to, tools, max_turns, status)
        VALUES (?, ?, 'openrouter', 'nvidia/nemotron-3-super-120b-a12b:free', ?, 
                7200, ?, '["bash","read","write","web_search","web_fetch"]', 150, 'active')
    """, (agent_id, name, instructions, task[2]))
    
    # Обновляем задачу
    c.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "approved",
        "agent_id": agent_id,
        "name": name,
        "message": f"Агент '{name}' создан CEO."
    }


class DepartmentRequest(BaseModel):
    """Создать целый отдел под руководителем."""
    department_name: str  # Название отдела
    leader_name: str  # Имя руководителя отдела
    leader_instructions: str
    leader_model: str = "nvidia/nemotron-3-super-120b-a12b:free"
    reports_to: Optional[str] = None  # Кому подчиняется руководитель
    members: List[dict] = []  # [{"name": "...", "role": "...", "instructions": "..."}]
    tools: List[str] = ["bash", "read", "write", "web_search", "web_fetch"]


@router.post("/create-department")
async def create_department(req: DepartmentRequest):
    """Создать целый отдел с руководителем и подчинёнными."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    created = []
    
    # 1. Создаём руководителя
    leader_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO agents (id, name, provider, model, instructions, 
                           heartbeat_sec, reports_to, tools, max_turns, status)
        VALUES (?, ?, 'openrouter', ?, ?, 7200, ?, ?, 200, 'active')
    """, (leader_id, req.leader_name, req.leader_model, 
          req.leader_instructions, req.reports_to, str(req.tools)))
    created.append({"name": req.leader_name, "id": leader_id, "role": "leader"})
    
    # 2. Создаём подчинённых
    for member in req.members:
        member_id = str(uuid.uuid4())
        member_name = member.get("name", "Unnamed")
        member_instructions = member.get("instructions", "")
        member_model = member.get("model", "nvidia/nemotron-3-super-120b-a12b:free")
        member_tools = member.get("tools", req.tools)
        member_max_turns = member.get("max_turns", 150)
        
        c.execute("""
            INSERT INTO agents (id, name, provider, model, instructions, 
                               heartbeat_sec, reports_to, tools, max_turns, status)
            VALUES (?, ?, 'openrouter', ?, ?, 7200, ?, ?, ?, 'active')
        """, (member_id, member_name, member_model, member_instructions,
              leader_id, str(member_tools), member_max_turns))
        created.append({"name": member_name, "id": member_id, "role": "member"})
    
    conn.commit()
    conn.close()
    
    return {
        "status": "created",
        "department": req.department_name,
        "leader": req.leader_name,
        "members_created": len(created) - 1,
        "total": len(created),
        "agents": created,
        "message": f"Отдел '{req.department_name}' создан: {req.leader_name} + {len(req.members)} подчинённых."
    }
