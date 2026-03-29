"""
OSYA Agents — Multi-API Key Manager
Rotate between multiple API keys to bypass rate limits.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
import yaml
import time
from pathlib import Path

router = APIRouter(prefix="/api/keys", tags=["api-keys"])

# In-memory key rotation state
_key_state: Dict[str, Dict] = {}


@router.get("/")
async def get_api_keys():
    """Получить все API ключи (без показа самих ключей)."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    providers = config.get("providers", {})
    result = []
    
    for prov_id, prov_config in providers.items():
        api_key = prov_config.get("api_key", "")
        # Show only last 4 chars
        masked = f"...{api_key[-4:]}" if len(api_key) > 4 else "***"
        
        # Check if it's a list of keys
        if isinstance(api_key, list):
            result.append({
                "provider": prov_id,
                "keys_count": len(api_key),
                "keys": [f"...{k[-4:]}" if len(k) > 4 else "***" for k in api_key],
                "base_url": prov_config.get("base_url")
            })
        else:
            result.append({
                "provider": prov_id,
                "keys_count": 1,
                "keys": [masked],
                "base_url": prov_config.get("base_url")
            })
    
    return {"keys": result}


@router.post("/add")
async def add_api_key(provider: str, api_key: str):
    """Добавить дополнительный API ключ к провайдеру."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    if provider not in config.get("providers", {}):
        raise HTTPException(404, f"Provider {provider} not found")
    
    current_key = config["providers"][provider].get("api_key")
    
    # Convert to list if needed
    if isinstance(current_key, list):
        if api_key not in current_key:
            current_key.append(api_key)
    else:
        if current_key != api_key:
            current_key = [current_key, api_key]
    
    config["providers"][provider]["api_key"] = current_key
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return {
        "status": "ok",
        "provider": provider,
        "keys_count": len(current_key) if isinstance(current_key, list) else 1
    }


@router.post("/rotate")
async def rotate_key(provider: str):
    """Переключиться на следующий API ключ."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    if provider not in config.get("providers", {}):
        raise HTTPException(404, f"Provider {provider} not found")
    
    api_key = config["providers"][provider].get("api_key")
    
    if not isinstance(api_key, list) or len(api_key) < 2:
        raise HTTPException(400, "Need at least 2 keys for rotation")
    
    # Initialize state
    if provider not in _key_state:
        _key_state[provider] = {"current_index": 0}
    
    # Rotate
    current_idx = _key_state[provider]["current_index"]
    next_idx = (current_idx + 1) % len(api_key)
    _key_state[provider]["current_index"] = next_idx
    
    # Update config with current key
    config["providers"][provider]["api_key"] = api_key[next_idx]
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return {
        "status": "ok",
        "provider": provider,
        "switched_to_key": f"...{api_key[next_idx][-4:]}",
        "key_index": next_idx
    }


@router.get("/usage")
async def get_key_usage():
    """Получить статистику использования ключей."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    providers = config.get("providers", {})
    result = []
    
    for prov_id, prov_config in providers.items():
        api_key = prov_config.get("api_key")
        
        if isinstance(api_key, list):
            keys_info = []
            for i, k in enumerate(api_key):
                state = _key_state.get(prov_id, {})
                is_current = state.get("current_index", 0) == i
                keys_info.append({
                    "index": i,
                    "masked": f"...{k[-4:]}",
                    "is_current": is_current,
                    "rate_limited": state.get(f"key_{i}_limited", False)
                })
            
            result.append({
                "provider": prov_id,
                "keys": keys_info,
                "rotation_enabled": True
            })
        else:
            result.append({
                "provider": prov_id,
                "keys": [{
                    "index": 0,
                    "masked": f"...{api_key[-4:]}",
                    "is_current": True,
                    "rate_limited": False
                }],
                "rotation_enabled": False
            })
    
    return {"usage": result}
