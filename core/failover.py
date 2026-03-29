"""
OSYA Agents — Sequential API Key Failover
Use one key at a time. If it fails (rate limit), switch to the next one.
"""
import time
import yaml
import json
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class APIKey:
    """Single API key with state."""
    key: str
    index: int
    is_active: bool = False
    is_rate_limited: bool = False
    rate_limit_reset: Optional[float] = None
    requests_today: int = 0
    errors_today: int = 0
    last_used: float = 0
    
    @property
    def masked(self) -> str:
        return f"...{self.key[-4:]}" if len(self.key) > 4 else "***"
    
    @property
    def is_available(self) -> bool:
        if not self.is_rate_limited:
            return True
        # Check if rate limit has expired
        if self.rate_limit_reset and time.time() > self.rate_limit_reset:
            self.is_rate_limited = False
            return True
        return False


class SequentialFailover:
    """
    Sequential API key failover.
    - Use one key at a time
    - If rate limited → switch to next
    - When limit resets → can reuse old key
    """
    
    def __init__(self):
        self.keys: List[APIKey] = []
        self.current_index: int = 0
        self.provider: str = "openrouter"
        self._config_path: str = "config.yaml"
    
    def load_from_config(self, config_path: str = "config.yaml"):
        """Load keys from config file."""
        self._config_path = config_path
        path = Path(config_path)
        
        if not path.exists():
            return
        
        with open(path) as f:
            config = yaml.safe_load(f)
        
        prov_config = config.get("providers", {}).get(self.provider, {})
        api_keys = prov_config.get("api_key", [])
        
        if isinstance(api_keys, str):
            api_keys = [api_keys]
        
        self.keys = [
            APIKey(key=k, index=i) 
            for i, k in enumerate(api_keys) 
            if k
        ]
        
        # Mark first as active
        if self.keys:
            self.keys[0].is_active = True
            self.current_index = 0
    
    @property
    def current_key(self) -> Optional[APIKey]:
        """Get the currently active key."""
        if not self.keys:
            return None
        return self.keys[self.current_index]
    
    def get_key(self) -> Optional[str]:
        """Get the current API key to use."""
        key = self.current_key
        if key and key.is_available:
            key.last_used = time.time()
            key.requests_today += 1
            return key.key
        return None
    
    def report_success(self):
        """Report a successful request."""
        key = self.current_key
        if key:
            key.errors_today = max(0, key.errors_today - 1)
    
    def report_rate_limit(self, reset_after: float = 60):
        """Report rate limit hit. Switch to next key."""
        key = self.current_key
        if key:
            key.is_rate_limited = True
            key.rate_limit_reset = time.time() + reset_after
            key.errors_today += 1
        
        # Switch to next available key
        self._switch_to_next()
    
    def report_error(self):
        """Report an error. If too many, switch key."""
        key = self.current_key
        if key:
            key.errors_today += 1
            # Switch after 3 consecutive errors
            if key.errors_today >= 3:
                self._switch_to_next()
    
    def _switch_to_next(self):
        """Switch to the next available key."""
        # Deactivate current
        if self.keys:
            self.keys[self.current_index].is_active = False
        
        # Find next available key
        for i in range(len(self.keys)):
            next_index = (self.current_index + 1 + i) % len(self.keys)
            if self.keys[next_index].is_available:
                self.current_index = next_index
                self.keys[next_index].is_active = True
                print(f"🔄 Switched to key {self.keys[next_index].masked}")
                return
        
        # All keys rate limited - use the one that resets soonest
        soonest = min(self.keys, key=lambda k: k.rate_limit_reset or float('inf'))
        self.current_index = soonest.index
        soonest.is_active = True
        print(f"⚠️ All keys limited. Using {soonest.masked} (resets soonest)")
    
    def add_key(self, api_key: str) -> bool:
        """Add a new API key."""
        # Check if exists
        for k in self.keys:
            if k.key == api_key:
                return False
        
        new_index = len(self.keys)
        self.keys.append(APIKey(key=api_key, index=new_index))
        
        # Save to config
        self._save_to_config()
        return True
    
    def remove_key(self, api_key: str) -> bool:
        """Remove an API key."""
        original_len = len(self.keys)
        self.keys = [k for k in self.keys if k.key != api_key]
        
        if len(self.keys) < original_len:
            # Re-index
            for i, k in enumerate(self.keys):
                k.index = i
            
            # Adjust current index
            if self.current_index >= len(self.keys):
                self.current_index = 0
            
            self._save_to_config()
            return True
        return False
    
    def _save_to_config(self):
        """Save keys back to config file."""
        path = Path(self._config_path)
        if not path.exists():
            return
        
        with open(path) as f:
            config = yaml.safe_load(f)
        
        config["providers"][self.provider]["api_key"] = [k.key for k in self.keys]
        
        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def get_stats(self) -> Dict:
        """Get statistics."""
        return {
            "provider": self.provider,
            "total_keys": len(self.keys),
            "current_key": self.current_key.masked if self.current_key else None,
            "current_index": self.current_index,
            "keys": [
                {
                    "index": k.index,
                    "masked": k.masked,
                    "is_active": k.is_active,
                    "is_available": k.is_available,
                    "requests_today": k.requests_today,
                    "errors_today": k.errors_today,
                    "is_rate_limited": k.is_rate_limited,
                    "rate_limit_reset_in": max(0, (k.rate_limit_reset or 0) - time.time()) if k.is_rate_limited else 0
                }
                for k in self.keys
            ]
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics."""
        for k in self.keys:
            k.requests_today = 0
            k.errors_today = 0
            k.is_rate_limited = False
            k.rate_limit_reset = None


# Global instance
failover = SequentialFailover()
