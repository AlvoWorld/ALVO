"""
OSYA Agents — Load Balancer API
Manage API key rotation and load balancing.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import yaml
from pathlib import Path

from core.load_balancer import load_balancer

router = APIRouter(prefix="/api/load-balancer", tags=["load-balancer"])


class AddKeyRequest(BaseModel):
    provider: str = "openrouter"
    api_key: str


class StrategyRequest(BaseModel):
    strategy: str  # round_robin, random, least_loaded


@router.on_event("startup")
async def startup():
    """Load keys from config on startup."""
    load_balancer.load_from_config("config.yaml")


@router.get("/stats")
async def get_stats():
    """Get load balancer statistics."""
    return load_balancer.get_stats()


@router.get("/best-key/{provider}")
async def get_best_key(provider: str = "openrouter"):
    """Get the best available API key for a provider."""
    key_state = load_balancer.get_best_key(provider)
    if not key_state:
        raise HTTPException(404, f"No keys available for {provider}")
    
    return {
        "provider": provider,
        "masked_key": key_state.masked,
        "is_available": key_state.is_available,
        "load_score": key_state.load_score,
        "requests_today": key_state.requests_today
    }


@router.post("/add-key")
async def add_key(request: AddKeyRequest):
    """Add a new API key dynamically."""
    success = load_balancer.add_key(request.provider, request.api_key)
    
    if success:
        # Also save to config
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            if request.provider not in config.get("providers", {}):
                config["providers"][request.provider] = {}
            
            current_keys = config["providers"][request.provider].get("api_key", [])
            if isinstance(current_keys, str):
                current_keys = [current_keys]
            if request.api_key not in current_keys:
                current_keys.append(request.api_key)
            config["providers"][request.provider]["api_key"] = current_keys
            
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
        
        return {"status": "ok", "message": f"Key added to {request.provider}"}
    else:
        return {"status": "exists", "message": "Key already exists"}


@router.post("/remove-key")
async def remove_key(request: AddKeyRequest):
    """Remove an API key."""
    success = load_balancer.remove_key(request.provider, request.api_key)
    
    if success:
        # Update config
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            if request.provider in config.get("providers", {}):
                current_keys = config["providers"][request.provider].get("api_key", [])
                if isinstance(current_keys, str):
                    current_keys = [current_keys]
                current_keys = [k for k in current_keys if k != request.api_key]
                config["providers"][request.provider]["api_key"] = current_keys
                
                with open(config_path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
        
        return {"status": "ok", "message": f"Key removed from {request.provider}"}
    else:
        return {"status": "not_found", "message": "Key not found"}


@router.post("/strategy")
async def set_strategy(request: StrategyRequest):
    """Set load balancing strategy."""
    load_balancer.set_strategy(request.strategy)
    return {"status": "ok", "strategy": request.strategy}


@router.post("/report-success")
async def report_success(provider: str, key_masked: str, tokens: int = 0, cost: float = 0.0):
    """Report a successful API call."""
    for key_state in load_balancer.keys.get(provider, []):
        if key_state.masked == key_masked:
            load_balancer.report_success(key_state, tokens, cost)
            return {"status": "ok"}
    raise HTTPException(404, "Key not found")


@router.post("/report-rate-limit")
async def report_rate_limit(provider: str, key_masked: str, reset_after: float = 60):
    """Report a rate limit hit."""
    for key_state in load_balancer.keys.get(provider, []):
        if key_state.masked == key_masked:
            load_balancer.report_rate_limit(key_state, reset_after)
            return {"status": "ok"}
    raise HTTPException(404, "Key not found")


@router.post("/reset-daily")
async def reset_daily_stats():
    """Reset daily statistics."""
    load_balancer.reset_daily_stats()
    return {"status": "ok", "message": "Daily stats reset"}
