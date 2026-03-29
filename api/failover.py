"""
OSYA Agents — Sequential Failover API
Manage sequential API key rotation.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from core.failover import failover

router = APIRouter(prefix="/api/failover", tags=["failover"])


class AddKeyRequest(BaseModel):
    api_key: str


@router.on_event("startup")
async def startup():
    """Load keys on startup."""
    failover.load_from_config("config.yaml")


@router.get("/status")
async def get_status():
    """Get current failover status."""
    return failover.get_stats()


@router.get("/current-key")
async def get_current_key():
    """Get the current active API key (masked)."""
    key = failover.current_key
    if not key:
        raise HTTPException(404, "No keys configured")
    return {
        "masked": key.masked,
        "is_available": key.is_available,
        "requests_today": key.requests_today
    }


@router.post("/add-key")
async def add_key(request: AddKeyRequest):
    """Add a new API key."""
    success = failover.add_key(request.api_key)
    if success:
        return {"status": "ok", "message": "Key added"}
    return {"status": "exists", "message": "Key already exists"}


@router.post("/remove-key")
async def remove_key(request: AddKeyRequest):
    """Remove an API key."""
    success = failover.remove_key(request.api_key)
    if success:
        return {"status": "ok", "message": "Key removed"}
    raise HTTPException(404, "Key not found")


@router.post("/switch-next")
async def switch_to_next():
    """Manually switch to the next key."""
    failover._switch_to_next()
    return {
        "status": "ok",
        "current_key": failover.current_key.masked if failover.current_key else None
    }


@router.post("/report-success")
async def report_success():
    """Report successful API call."""
    failover.report_success()
    return {"status": "ok"}


@router.post("/report-rate-limit")
async def report_rate_limit(reset_after: float = 60):
    """Report rate limit hit."""
    failover.report_rate_limit(reset_after)
    return {
        "status": "ok",
        "switched_to": failover.current_key.masked if failover.current_key else None
    }


@router.post("/report-error")
async def report_error():
    """Report an API error."""
    failover.report_error()
    return {"status": "ok"}


@router.post("/reset")
async def reset_stats():
    """Reset daily statistics."""
    failover.reset_daily_stats()
    return {"status": "ok"}
