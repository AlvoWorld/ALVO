"""
OSYA Agents — LLM Provider Module
Supports OpenRouter, Anthropic, Google, and any OpenAI-compatible API.
"""
import json
import httpx
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]]
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str


class LLMProvider:
    """Universal LLM provider supporting OpenAI-compatible APIs."""
    
    PROVIDERS = {
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "api_key_env": "OPENROUTER_API_KEY",
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1",
            "api_key_env": "ANTHROPIC_API_KEY",
        },
        "google": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "api_key_env": "GOOGLE_API_KEY",
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
        },
    }

    def __init__(self, provider: str, model: str, api_key: str = None, 
                 base_url: str = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or self.PROVIDERS.get(provider, {}).get("base_url")
        
        if not self.api_key:
            import os
            env_key = self.PROVIDERS.get(provider, {}).get("api_key_env")
            if env_key:
                self.api_key = os.getenv(env_key)
        
        if not self.api_key:
            raise ValueError(f"No API key for provider '{provider}'. Set {self.PROVIDERS.get(provider, {}).get('api_key_env')}")

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/sds333/osya-agents"
            headers["X-Title"] = "OSYA Agents"
        return headers

    def _build_tools(self, tools: List[str]) -> List[Dict]:
        """Convert tool names to OpenAI function definitions."""
        tool_defs = {
            "bash": {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "Execute a bash command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The bash command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            "read": {
                "type": "function",
                "function": {
                    "name": "read",
                    "description": "Read a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path to read"}
                        },
                        "required": ["path"]
                    }
                }
            },
            "write": {
                "type": "function",
                "function": {
                    "name": "write",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path to write"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            "web_search": {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            "web_fetch": {
                "type": "function",
                "function": {
                    "name": "web_fetch",
                    "description": "Fetch a web page and return its content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"}
                        },
                        "required": ["url"]
                    }
                }
            },
        }
        return [tool_defs[t] for t in tools if t in tool_defs]

    def chat(self, messages: List[Dict[str, str]], tools: List[str] = None,
             max_tokens: int = 4096, temperature: float = 0.7) -> LLMResponse:
        """Send a chat completion request."""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if tools:
            payload["tools"] = self._build_tools(tools)
            payload["tool_choice"] = "auto"
        
        headers = self._get_headers()
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        choice = data["choices"][0]["message"]
        usage = data.get("usage", {})
        
        tool_calls = []
        if choice.get("tool_calls"):
            for tc in choice["tool_calls"]:
                tool_calls.append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "input": json.loads(tc["function"]["arguments"])
                })
        
        return LLMResponse(
            content=choice.get("content", "") or "",
            tool_calls=tool_calls,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            cost_usd=data.get("usage", {}).get("cost", 0),
            model=data.get("model", self.model),
        )

    def chat_stream(self, messages: List[Dict[str, str]], tools: List[str] = None,
                    max_tokens: int = 4096, temperature: float = 0.7) -> Generator[str, None, None]:
        """Stream a chat completion response."""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        
        if tools:
            payload["tools"] = self._build_tools(tools)
            payload["tool_choice"] = "auto"
        
        headers = self._get_headers()
        
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
