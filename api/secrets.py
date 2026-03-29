"""
OSYA Agents — Secrets API
Manage API keys securely.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from core.secrets import get_api_keys, set_api_keys, add_api_key, remove_api_key

router = APIRouter(prefix="/api/secrets", tags=["secrets"])


class KeysRequest(BaseModel):
    provider: str = "openrouter"
    api_keys: List[str]


class SingleKeyRequest(BaseModel):
    provider: str = "openrouter"
    api_key: str


@router.get("/{provider}")
async def get_keys(provider: str = "openrouter"):
    """Get masked API keys for a provider."""
    keys = get_api_keys(provider)
    return {
        "provider": provider,
        "count": len(keys),
        "keys": [f"...{k[-4:]}" if len(k) > 4 else "***" for k in keys]
    }


@router.post("/{provider}")
async def set_keys(provider: str, request: KeysRequest):
    """Set API keys for a provider."""
    set_api_keys(provider, request.api_keys)
    return {"status": "ok", "count": len(request.api_keys)}


@router.post("/{provider}/add")
async def add_key(provider: str, request: SingleKeyRequest):
    """Add a single API key."""
    success = add_api_key(provider, request.api_key)
    if success:
        return {"status": "ok", "message": "Key added"}
    return {"status": "exists", "message": "Key already exists"}


@router.delete("/{provider}/remove")
async def remove_key(provider: str, request: SingleKeyRequest):
    """Remove an API key."""
    success = remove_api_key(provider, request.api_key)
    if success:
        return {"status": "ok", "message": "Key removed"}
    raise HTTPException(404, "Key not found")
