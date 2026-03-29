"""
OSYA Agents — Per-Agent Configuration API
Control model, provider, limits, and schedules for each agent individually.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, List
from pydantic import BaseModel
import yaml
import json
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api/agent-config", tags=["agent-config"])

CONFIG_FILE = Path("agent_config.json")


class AgentConfig(BaseModel):
    agent_name: str
    model: Optional[str] = None
    provider: Optional[str] = None
    daily_limit_tokens: Optional[int] = None
    daily_limit_cost_usd: Optional[float] = None
    schedule_cron: Optional[str] = None  # e.g. "*/30 * * * *" for every 30 min
    schedule_active_hours: Optional[Dict] = None  # {"start": "09:00", "end": "18:00"}
    enabled: Optional[bool] = None
    priority: Optional[int] = None  # 1=high, 2=medium, 3=low


def load_agent_configs() -> Dict:
    """Load agent configurations from JSON file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_agent_configs(configs: Dict):
    """Save agent configurations to JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(configs, f, indent=2, default=str)


@router.get("/")
async def get_all_configs():
    """Получить конфигурации всех агентов."""
    configs = load_agent_configs()
    
    # Also load from config.yaml for defaults
    config_path = Path("config.yaml")
    yaml_agents = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            for agent in config.get("agents", []):
                yaml_agents[agent["name"]] = {
                    "model": agent.get("model"),
                    "provider": agent.get("provider"),
                    "heartbeat_sec": agent.get("heartbeat_sec"),
                }
    
    # Merge configs
    result = []
    for name, yaml_config in yaml_agents.items():
        custom = configs.get(name, {})
        result.append({
            "name": name,
            "model": custom.get("model") or yaml_config.get("model"),
            "provider": custom.get("provider") or yaml_config.get("provider"),
            "heartbeat_sec": yaml_config.get("heartbeat_sec"),
            "daily_limit_tokens": custom.get("daily_limit_tokens"),
            "daily_limit_cost_usd": custom.get("daily_limit_cost_usd"),
            "schedule_cron": custom.get("schedule_cron"),
            "schedule_active_hours": custom.get("schedule_active_hours"),
            "enabled": custom.get("enabled", True),
            "priority": custom.get("priority", 2),
            "tokens_used_today": custom.get("tokens_used_today", 0),
            "cost_used_today": custom.get("cost_used_today", 0.0),
        })
    
    return {"agents": result}


@router.get("/{agent_name}")
async def get_agent_config(agent_name: str):
    """Получить конфигурацию конкретного агента."""
    configs = load_agent_configs()
    
    # Load defaults from config.yaml
    config_path = Path("config.yaml")
    yaml_config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            for agent in config.get("agents", []):
                if agent["name"] == agent_name:
                    yaml_config = agent
                    break
    
    if not yaml_config and agent_name not in configs:
        raise HTTPException(404, f"Agent {agent_name} not found")
    
    custom = configs.get(agent_name, {})
    
    return {
        "name": agent_name,
        "model": custom.get("model") or yaml_config.get("model"),
        "provider": custom.get("provider") or yaml_config.get("provider"),
        "heartbeat_sec": yaml_config.get("heartbeat_sec"),
        "daily_limit_tokens": custom.get("daily_limit_tokens"),
        "daily_limit_cost_usd": custom.get("daily_limit_cost_usd"),
        "schedule_cron": custom.get("schedule_cron"),
        "schedule_active_hours": custom.get("schedule_active_hours"),
        "enabled": custom.get("enabled", True),
        "priority": custom.get("priority", 2),
        "tokens_used_today": custom.get("tokens_used_today", 0),
        "cost_used_today": custom.get("cost_used_today", 0.0),
    }


@router.put("/{agent_name}")
async def update_agent_config(agent_name: str, config: AgentConfig):
    """Обновить конфигурацию агента."""
    configs = load_agent_configs()
    
    if agent_name not in configs:
        configs[agent_name] = {}
    
    # Update only provided fields
    if config.model is not None:
        configs[agent_name]["model"] = config.model
    if config.provider is not None:
        configs[agent_name]["provider"] = config.provider
    if config.daily_limit_tokens is not None:
        configs[agent_name]["daily_limit_tokens"] = config.daily_limit_tokens
    if config.daily_limit_cost_usd is not None:
        configs[agent_name]["daily_limit_cost_usd"] = config.daily_limit_cost_usd
    if config.schedule_cron is not None:
        configs[agent_name]["schedule_cron"] = config.schedule_cron
    if config.schedule_active_hours is not None:
        configs[agent_name]["schedule_active_hours"] = config.schedule_active_hours
    if config.enabled is not None:
        configs[agent_name]["enabled"] = config.enabled
    if config.priority is not None:
        configs[agent_name]["priority"] = config.priority
    
    configs[agent_name]["updated_at"] = datetime.now().isoformat()
    
    save_agent_configs(configs)
    
    # Also update config.yaml if model/provider changed
    if config.model or config.provider:
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f)
            
            for agent in yaml_config.get("agents", []):
                if agent["name"] == agent_name:
                    if config.model:
                        agent["model"] = config.model
                    if config.provider:
                        agent["provider"] = config.provider
                    break
            
            with open(config_path, "w") as f:
                yaml.dump(yaml_config, f, default_flow_style=False)
    
    return {"status": "ok", "agent": agent_name, "config": configs[agent_name]}


@router.post("/bulk-model")
async def bulk_set_model(agent_names: List[str], model: str, provider: str = "openrouter"):
    """Установить модель для нескольких агентов сразу."""
    configs = load_agent_configs()
    
    for name in agent_names:
        if name not in configs:
            configs[name] = {}
        configs[name]["model"] = model
        configs[name]["provider"] = provider
        configs[name]["updated_at"] = datetime.now().isoformat()
    
    save_agent_configs(configs)
    
    # Update config.yaml
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)
        
        for agent in yaml_config.get("agents", []):
            if agent["name"] in agent_names:
                agent["model"] = model
                agent["provider"] = provider
        
        with open(config_path, "w") as f:
            yaml.dump(yaml_config, f, default_flow_style=False)
    
    return {"status": "ok", "updated": agent_names, "model": model}


@router.get("/limits/status")
async def get_limits_status():
    """Получить статус лимитов всех агентов."""
    configs = load_agent_configs()
    
    result = []
    for name, config in configs.items():
        result.append({
            "agent": name,
            "daily_limit_tokens": config.get("daily_limit_tokens"),
            "tokens_used": config.get("tokens_used_today", 0),
            "daily_limit_cost_usd": config.get("daily_limit_cost_usd"),
            "cost_used": config.get("cost_used_today", 0.0),
            "limit_reached": (
                (config.get("daily_limit_tokens") and 
                 config.get("tokens_used_today", 0) >= config.get("daily_limit_tokens")) or
                (config.get("daily_limit_cost_usd") and 
                 config.get("cost_used_today", 0) >= config.get("daily_limit_cost_usd"))
            )
        })
    
    return {"limits": result}


@router.post("/limits/reset")
async def reset_daily_limits():
    """Сбросить дневные лимиты (вызывать в полночь)."""
    configs = load_agent_configs()
    
    for name in configs:
        configs[name]["tokens_used_today"] = 0
        configs[name]["cost_used_today"] = 0.0
    
    save_agent_configs(configs)
    
    return {"status": "ok", "message": "Daily limits reset"}


@router.post("/limits/update")
async def update_usage(agent_name: str, tokens: int, cost: float = 0.0):
    """Обновить использование агента (вызывать после каждого запроса)."""
    configs = load_agent_configs()
    
    if agent_name not in configs:
        configs[agent_name] = {}
    
    configs[agent_name]["tokens_used_today"] = configs[agent_name].get("tokens_used_today", 0) + tokens
    configs[agent_name]["cost_used_today"] = configs[agent_name].get("cost_used_today", 0.0) + cost
    
    # Check if limit reached
    limit_reached = False
    if configs[agent_name].get("daily_limit_tokens"):
        if configs[agent_name]["tokens_used_today"] >= configs[agent_name]["daily_limit_tokens"]:
            limit_reached = True
    if configs[agent_name].get("daily_limit_cost_usd"):
        if configs[agent_name]["cost_used_today"] >= configs[agent_name]["daily_limit_cost_usd"]:
            limit_reached = True
    
    save_agent_configs(configs)
    
    return {
        "status": "ok",
        "agent": agent_name,
        "tokens_used_today": configs[agent_name]["tokens_used_today"],
        "cost_used_today": configs[agent_name]["cost_used_today"],
        "limit_reached": limit_reached
    }
