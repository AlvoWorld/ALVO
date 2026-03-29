"""
OSYA Agents — Web API
FastAPI-based REST API for agent management.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import yaml
import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Database
from core.runner import AgentRunner
from core.scheduler import Scheduler


app = FastAPI(title="OSYA Agents", version="1.0.0")

# Global instances (set by main.py)
db: Database = None
runner: AgentRunner = None
scheduler: Scheduler = None


class AgentCreate(BaseModel):
    name: str
    provider: str = "openrouter"
    model: str = "xiaomi/mimo-v2-pro"
    instructions: str = ""
    heartbeat_sec: int = 0
    reports_to: Optional[str] = None
    tools: List[str] = ["bash", "read", "write", "web_search"]
    max_turns: int = 100


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    instructions: Optional[str] = None
    heartbeat_sec: Optional[int] = None
    reports_to: Optional[str] = None
    tools: Optional[List[str]] = None
    max_turns: Optional[int] = None


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "normal"
    assignee_name: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_name: Optional[str] = None


class RunRequest(BaseModel):
    message: Optional[str] = None
    task_id: Optional[str] = None


class CommentCreate(BaseModel):
    author: str
    content: str


class SettingsUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    heartbeat_sec: Optional[int] = None


class BulkModelUpdate(BaseModel):
    model: str
    provider: str = "openrouter"
    agent_names: Optional[List[str]] = None  # None = all agents


# Agent endpoints
@app.get("/api/agents")
def list_agents():
    return db.list_agents()


@app.post("/api/agents")
def create_agent(data: AgentCreate):
    # Resolve reports_to
    reports_to_id = None
    if data.reports_to:
        parent = db.get_agent(name=data.reports_to)
        if parent:
            reports_to_id = parent['id']
    
    agent_id = db.create_agent(
        name=data.name,
        provider=data.provider,
        model=data.model,
        instructions=data.instructions,
        heartbeat_sec=data.heartbeat_sec,
        reports_to=reports_to_id,
        tools=data.tools,
        max_turns=data.max_turns,
    )
    return {"id": agent_id, "name": data.name}


@app.get("/api/agents/{agent_id}")
def get_agent(agent_id: str):
    agent = db.get_agent(agent_id=agent_id)
    if not agent:
        agent = db.get_agent(name=agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@app.patch("/api/agents/{agent_id}")
def update_agent(agent_id: str, data: AgentUpdate):
    updates = {k: v for k, v in data.dict().items() if v is not None}
    
    if 'reports_to' in updates:
        parent = db.get_agent(name=updates['reports_to'])
        updates['reports_to'] = parent['id'] if parent else None
    
    if not db.update_agent(agent_id, **updates):
        raise HTTPException(400, "No updates provided")
    return {"ok": True}


@app.delete("/api/agents/{agent_id}")
def delete_agent(agent_id: str):
    db.delete_agent(agent_id)
    return {"ok": True}


@app.post("/api/agents/{agent_id}/run")
def run_agent(agent_id: str, data: RunRequest):
    agent = db.get_agent(agent_id=agent_id)
    if not agent:
        agent = db.get_agent(name=agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    result = runner.run(agent['name'], message=data.message, task_id=data.task_id)
    return result


# Task endpoints
@app.get("/api/tasks")
def list_tasks(status: str = None, assignee: str = None):
    assignee_id = None
    if assignee:
        a = db.get_agent(name=assignee)
        assignee_id = a['id'] if a else assignee
    return db.list_tasks(status=status, assignee_id=assignee_id)


@app.post("/api/tasks")
def create_task(data: TaskCreate):
    assignee_id = None
    if data.assignee_name:
        a = db.get_agent(name=data.assignee_name)
        if a:
            assignee_id = a['id']
    
    task_id = db.create_task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        assignee_id=assignee_id,
    )
    return {"id": task_id}


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: str, data: TaskUpdate):
    updates = {k: v for k, v in data.dict().items() if v is not None}
    
    if 'assignee_name' in updates:
        a = db.get_agent(name=updates.pop('assignee_name'))
        updates['assignee_id'] = a['id'] if a else None
    
    if not db.update_task(task_id, **updates):
        raise HTTPException(400, "No updates provided")
    return {"ok": True}


@app.post("/api/tasks/{task_id}/comments")
def add_comment(task_id: str, data: CommentCreate):
    comment_id = db.add_comment(task_id, data.author, data.content)
    return {"id": comment_id}


@app.get("/api/tasks/{task_id}/comments")
def get_comments(task_id: str):
    return db.get_comments(task_id)


# Run endpoints
@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = db.get_task(run_id)  # Note: should be get_run but we use task table
    messages = db.get_messages(run_id)
    return {"messages": messages}


# Settings endpoints
@app.get("/api/settings")
def get_settings():
    """Get current platform settings."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    providers = config.get("providers", {})
    # Hide full API keys, show only last 4 chars
    safe_providers = {}
    for name, p in providers.items():
        safe_providers[name] = {
            "base_url": p.get("base_url", ""),
            "api_key_hint": f"...{p.get('api_key', '')[-4:]}" if p.get('api_key') else "",
        }
    
    return {
        "providers": safe_providers,
        "server": config.get("server", {}),
        "database": config.get("database", {}),
        "telegram_configured": bool(config.get("telegram", {}).get("bot_token")),
        "workdir": config.get("workdir", "/tmp"),
        "tool_timeout": config.get("tool_timeout", 30),
    }


@app.get("/api/settings/models")
def list_models(provider: str = "openrouter"):
    """List available models from a provider."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    provider_config = config.get("providers", {}).get(provider, {})
    api_key = provider_config.get("api_key", "")
    base_url = provider_config.get("base_url", "https://openrouter.ai/api/v1")
    
    if not api_key:
        raise HTTPException(400, f"No API key for provider '{provider}'")
    
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            resp.raise_for_status()
            data = resp.json()
            
            models = []
            for m in data.get("data", []):
                models.append({
                    "id": m["id"],
                    "name": m.get("name", m["id"]),
                    "context_length": m.get("context_length"),
                    "pricing": m.get("pricing", {}),
                })
            
            return {"models": models, "count": len(models)}
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch models: {e}")


@app.post("/api/settings/model/bulk")
def bulk_update_model(data: BulkModelUpdate):
    """Change model for all agents or specific agents."""
    if data.agent_names:
        agents = [db.get_agent(name=n) for n in data.agent_names]
        agents = [a for a in agents if a]
    else:
        agents = db.list_agents()
    
    updated = []
    for agent in agents:
        db.update_agent(agent["id"], provider=data.provider, model=data.model)
        updated.append(agent["name"])
    
    return {"updated": updated, "count": len(updated)}


@app.post("/api/settings/provider")
def update_provider_settings(data: SettingsUpdate):
    """Update provider settings in config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    if data.provider:
        if "providers" not in config:
            config["providers"] = {}
        if data.provider not in config["providers"]:
            config["providers"][data.provider] = {}
        
        if data.api_key:
            config["providers"][data.provider]["api_key"] = data.api_key
        if data.base_url:
            config["providers"][data.provider]["base_url"] = data.base_url
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"ok": True, "message": "Config updated. Restart server to apply."}


# Health check
@app.get("/api/health")
def health():
    agents = db.list_agents()
    running = sum(1 for a in agents if a.get('status') == 'running')
    return {
        "status": "ok",
        "agents_total": len(agents),
        "agents_running": running,
        "scheduler_active": scheduler.running if scheduler else False,
    }


# Dashboard
@app.get("/", response_class=HTMLResponse)
def dashboard():
    from pathlib import Path
    web_dir = Path(__file__).parent.parent / "web"
    index_file = web_dir / "index.html"
    if index_file.exists():
        return index_file.read_text()
    return "<h1>OSYA Agents</h1><p>Web UI not found</p>"


def setup(database: Database, agent_runner: AgentRunner, sched: Scheduler):
    """Set up the API with dependencies."""
    global db, runner, scheduler
    db = database
    runner = agent_runner
    scheduler = sched

# Import and register models router
from api.models import router as models_router
app.include_router(models_router)

# Import and register keys router
from api.keys import router as keys_router
app.include_router(keys_router)

# Free models list
from core.free_models import FREE_MODELS, get_best_free_model

@app.get("/api/free-models")
async def list_free_models(provider: str = None):
    """List all free models available."""
    if provider:
        return {"models": FREE_MODELS.get(provider, [])}
    return FREE_MODELS

@app.get("/api/best-free-model")
async def best_free_model():
    """Get the best free model available."""
    return get_best_free_model()
