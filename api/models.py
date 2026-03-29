"""
OSYA Agents — Free Models & Multi-Provider API
Search free models, manage providers, bypass rate limits.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
import httpx
import yaml
from pathlib import Path

router = APIRouter(prefix="/api/models", tags=["models"])

# Known free model providers
FREE_PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "free_suffix": ":free",
        "description": "Мульти-провайдер, много бесплатных моделей"
    },
    "huggingface": {
        "name": "Hugging Face",
        "base_url": "https://api-inference.huggingface.co/models",
        "free_suffix": "",
        "description": "Бесплатный inference API для open-source моделей"
    },
    "together": {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "free_suffix": "",
        "description": "Бесплатные credits при регистрации"
    },
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "free_suffix": "",
        "description": "Быстрые бесплатные модели (Llama, Mixtral)"
    }
}


@router.get("/free")
async def get_free_models(provider: Optional[str] = None):
    """Получить список бесплатных моделей."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    providers = config.get("providers", {})
    all_free_models = []
    
    for prov_id, prov_config in providers.items():
        if provider and prov_id != provider:
            continue
            
        api_key = prov_config.get("api_key")
        base_url = prov_config.get("base_url")
        
        if not api_key or not base_url:
            continue
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                )
                
                if resp.status_code == 200:
                    models = resp.json().get("data", [])
                    for m in models:
                        model_id = m.get("id", "")
                        pricing = m.get("pricing", {})
                        
                        # Check if free
                        is_free = (
                            ":free" in model_id or
                            (pricing.get("prompt", "0") == "0" and 
                             pricing.get("completion", "0") == "0")
                        )
                        
                        if is_free:
                            all_free_models.append({
                                "id": model_id,
                                "name": m.get("name", model_id),
                                "provider": prov_id,
                                "context_length": m.get("context_length", 0),
                                "pricing": pricing
                            })
        except Exception as e:
            continue
    
    return {
        "count": len(all_free_models),
        "models": sorted(all_free_models, key=lambda x: x["id"])
    }


@router.get("/providers")
async def get_providers():
    """Получить список всех провайдеров."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    providers = config.get("providers", {})
    result = []
    
    for prov_id, prov_config in providers.items():
        info = FREE_PROVIDERS.get(prov_id, {})
        result.append({
            "id": prov_id,
            "name": info.get("name", prov_id),
            "base_url": prov_config.get("base_url"),
            "description": info.get("description", ""),
            "has_key": bool(prov_config.get("api_key")),
            "free_suffix": info.get("free_suffix", ":free")
        })
    
    return {"providers": result}


@router.post("/providers")
async def add_provider(provider_id: str, api_key: str, base_url: str):
    """Добавить нового провайдера."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    if "providers" not in config:
        config["providers"] = {}
    
    config["providers"][provider_id] = {
        "api_key": api_key,
        "base_url": base_url
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return {"status": "ok", "provider": provider_id}


@router.post("/switch-provider")
async def switch_provider(agent_id: str, provider_id: str, model_id: str):
    """Переключить агента на другой провайдер/модель."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    for agent in config.get("agents", []):
        if agent.get("name") == agent_id:
            agent["provider"] = provider_id
            agent["model"] = model_id
            break
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return {"status": "ok", "agent": agent_id, "model": model_id}


@router.post("/rotate-provider")
async def rotate_provider_on_limit():
    """
    Автоматически переключить агентов на другой провайдер при лимите.
    Это позволяет обходить rate limits.
    """
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    providers = list(config.get("providers", {}).keys())
    if len(providers) < 2:
        raise HTTPException(400, "Need at least 2 providers for rotation")
    
    # Get current provider
    agents = config.get("agents", [])
    if not agents:
        return {"status": "no_agents"}
    
    current_provider = agents[0].get("provider", providers[0])
    
    # Find next provider
    try:
        current_idx = providers.index(current_provider)
        next_idx = (current_idx + 1) % len(providers)
        next_provider = providers[next_idx]
    except ValueError:
        next_provider = providers[0]
    
    # Switch all agents
    switched = 0
    for agent in agents:
        agent["provider"] = next_provider
        switched += 1
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return {
        "status": "ok",
        "switched_from": current_provider,
        "switched_to": next_provider,
        "agents_switched": switched
    }
