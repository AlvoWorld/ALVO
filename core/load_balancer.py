"""
OSYA Agents — API Key Load Balancer
Distribute requests across multiple API keys to maximize throughput and bypass limits.
"""
import time
import random
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json


@dataclass
class APIKeyState:
    """State of a single API key."""
    key: str
    provider: str
    requests_today: int = 0
    tokens_today: int = 0
    cost_today: float = 0.0
    last_request_time: float = 0
    is_rate_limited: bool = False
    rate_limit_reset_time: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    
    @property
    def masked(self) -> str:
        return f"...{self.key[-4:]}" if len(self.key) > 4 else "***"
    
    @property
    def is_available(self) -> bool:
        if self.is_rate_limited:
            if self.rate_limit_reset_time and time.time() > self.rate_limit_reset_time:
                self.is_rate_limited = False
                self.error_count = 0
                return True
            return False
        return True
    
    @property
    def load_score(self) -> float:
        """Lower score = less loaded = better to use."""
        if not self.is_available:
            return float('inf')
        # Consider: requests today, error count, time since last request
        score = self.requests_today * 10 + self.error_count * 100
        # Prefer keys that haven't been used recently
        time_since_last = time.time() - self.last_request_time
        score -= min(time_since_last / 60, 10)  # Bonus for idle keys
        return score


class LoadBalancer:
    """Intelligent load balancer for API keys."""
    
    def __init__(self):
        self.keys: Dict[str, List[APIKeyState]] = {}  # provider -> list of keys
        self._lock = threading.Lock()
        self._strategy = "least_loaded"  # round_robin, random, least_loaded
    
    def load_from_config(self, config_path: str = "config.yaml"):
        """Load keys from config file."""
        path = Path(config_path)
        if not path.exists():
            return
        
        with open(path) as f:
            config = yaml.safe_load(f)
        
        for provider, prov_config in config.get("providers", {}).items():
            api_keys = prov_config.get("api_key", [])
            if isinstance(api_keys, str):
                api_keys = [api_keys]
            
            self.keys[provider] = [
                APIKeyState(key=k, provider=provider) for k in api_keys if k
            ]
    
    def add_key(self, provider: str, api_key: str):
        """Add a new API key dynamically."""
        with self._lock:
            if provider not in self.keys:
                self.keys[provider] = []
            
            # Check if key already exists
            for ks in self.keys[provider]:
                if ks.key == api_key:
                    return False
            
            self.keys[provider].append(APIKeyState(key=api_key, provider=provider))
            return True
    
    def remove_key(self, provider: str, api_key: str):
        """Remove an API key."""
        with self._lock:
            if provider not in self.keys:
                return False
            self.keys[provider] = [k for k in self.keys[provider] if k.key != api_key]
            return True
    
    def get_best_key(self, provider: str = "openrouter") -> Optional[APIKeyState]:
        """Get the best available key for a provider."""
        with self._lock:
            keys = self.keys.get(provider, [])
            if not keys:
                return None
            
            available = [k for k in keys if k.is_available]
            if not available:
                # All rate limited - return the one that resets soonest
                return min(keys, key=lambda k: k.rate_limit_reset_time or float('inf'))
            
            if self._strategy == "round_robin":
                # Simple round robin
                return available[self._get_next_index(provider) % len(available)]
            elif self._strategy == "random":
                return random.choice(available)
            else:  # least_loaded
                return min(available, key=lambda k: k.load_score)
    
    def _get_next_index(self, provider: str) -> int:
        """Get next index for round robin."""
        if not hasattr(self, '_round_robin_index'):
            self._round_robin_index = {}
        self._round_robin_index[provider] = self._round_robin_index.get(provider, 0) + 1
        return self._round_robin_index[provider]
    
    def report_success(self, key_state: APIKeyState, tokens: int = 0, cost: float = 0.0):
        """Report a successful request."""
        with self._lock:
            key_state.requests_today += 1
            key_state.tokens_today += tokens
            key_state.cost_today += cost
            key_state.last_request_time = time.time()
            key_state.success_count += 1
            key_state.error_count = max(0, key_state.error_count - 1)
    
    def report_rate_limit(self, key_state: APIKeyState, reset_after: float = 60):
        """Report that a key hit rate limit."""
        with self._lock:
            key_state.is_rate_limited = True
            key_state.rate_limit_reset_time = time.time() + reset_after
            key_state.error_count += 1
    
    def report_error(self, key_state: APIKeyState):
        """Report an error with a key."""
        with self._lock:
            key_state.error_count += 1
    
    def get_stats(self) -> Dict:
        """Get statistics for all keys."""
        with self._lock:
            stats = {}
            for provider, keys in self.keys.items():
                provider_stats = []
                for k in keys:
                    provider_stats.append({
                        "masked": k.masked,
                        "available": k.is_available,
                        "requests_today": k.requests_today,
                        "tokens_today": k.tokens_today,
                        "cost_today": k.cost_today,
                        "success_count": k.success_count,
                        "error_count": k.error_count,
                        "load_score": k.load_score
                    })
                stats[provider] = {
                    "total_keys": len(keys),
                    "available_keys": sum(1 for k in keys if k.is_available),
                    "keys": provider_stats
                }
            return stats
    
    def set_strategy(self, strategy: str):
        """Set load balancing strategy."""
        if strategy in ("round_robin", "random", "least_loaded"):
            self._strategy = strategy
    
    def reset_daily_stats(self):
        """Reset daily statistics for all keys."""
        with self._lock:
            for keys in self.keys.values():
                for k in keys:
                    k.requests_today = 0
                    k.tokens_today = 0
                    k.cost_today = 0
                    k.is_rate_limited = False
                    k.rate_limit_reset_time = None


# Global load balancer instance
load_balancer = LoadBalancer()
