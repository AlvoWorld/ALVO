"""
OSYA Agents — Secure Secrets Manager
Never store secrets in files that go to GitHub.
Use environment variables or encrypted storage.
"""
import os
import json
from pathlib import Path
from typing import Optional, List

SECRETS_FILE = Path.home() / ".osya" / "secrets.json"


def ensure_secrets_dir():
    """Create secrets directory if not exists."""
    SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Set restrictive permissions
    os.chmod(SECRETS_FILE.parent, 0o700)


def load_secrets() -> dict:
    """Load secrets from encrypted file."""
    ensure_secrets_dir()
    if SECRETS_FILE.exists():
        with open(SECRETS_FILE) as f:
            return json.load(f)
    return {}


def save_secrets(secrets: dict):
    """Save secrets to encrypted file."""
    ensure_secrets_dir()
    with open(SECRETS_FILE, "w") as f:
        json.dump(secrets, f, indent=2)
    # Set restrictive permissions
    os.chmod(SECRETS_FILE, 0o600)


def get_api_keys(provider: str = "openrouter") -> List[str]:
    """
    Get API keys for a provider.
    Priority:
    1. Environment variable (comma-separated)
    2. Secrets file
    """
    # Try environment variable first
    env_var = f"{provider.upper()}_API_KEYS"
    env_keys = os.environ.get(env_var, "")
    if env_keys:
        return [k.strip() for k in env_keys.split(",") if k.strip()]
    
    # Try secrets file
    secrets = load_secrets()
    keys = secrets.get(provider, {}).get("api_keys", [])
    return keys if isinstance(keys, list) else [keys] if keys else []


def set_api_keys(provider: str, api_keys: List[str]):
    """Save API keys to secrets file."""
    secrets = load_secrets()
    if provider not in secrets:
        secrets[provider] = {}
    secrets[provider]["api_keys"] = api_keys
    save_secrets(secrets)


def add_api_key(provider: str, api_key: str) -> bool:
    """Add a single API key."""
    keys = get_api_keys(provider)
    if api_key in keys:
        return False
    keys.append(api_key)
    set_api_keys(provider, keys)
    return True


def remove_api_key(provider: str, api_key: str) -> bool:
    """Remove an API key."""
    keys = get_api_keys(provider)
    if api_key in keys:
        keys.remove(api_key)
        set_api_keys(provider, keys)
        return True
    return False


def get_config_value(key: str, default: str = "") -> str:
    """
    Get configuration value.
    Priority:
    1. Environment variable
    2. Secrets file
    3. Default value
    """
    # Try environment variable
    value = os.environ.get(key.upper(), "")
    if value:
        return value
    
    # Try secrets file
    secrets = load_secrets()
    return secrets.get("config", {}).get(key, default)


def set_config_value(key: str, value: str):
    """Save configuration value."""
    secrets = load_secrets()
    if "config" not in secrets:
        secrets["config"] = {}
    secrets["config"][key] = value
    save_secrets(secrets)
