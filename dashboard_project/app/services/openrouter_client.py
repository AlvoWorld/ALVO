"""
OpenRouter API Client with Rate-Limit Retry Handling.

Provides async HTTP client for OpenRouter API with:
- Automatic exponential backoff on 429 (Rate Limit)
- Retry on 5xx server errors
- Retry on connection errors/timeouts
- Concurrent request limiting via semaphore
- Statistics tracking

Author: Backend Developer (ALVO Platform)
Date: 2026-03-29
"""

import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

# ============================================================================
# Exceptions
# ============================================================================


class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors."""
    pass


class RateLimitError(OpenRouterError):
    """Raised when rate limit is exceeded after all retries."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[float] = None):
        self.retry_after = retry_after
        super().__init__(message)


class AuthenticationError(OpenRouterError):
    """Raised on 401 Unauthorized."""
    pass


class ModelNotFoundError(OpenRouterError):
    """Raised on 404 - model not found."""
    pass


class ServerError(OpenRouterError):
    """Raised on 5xx server errors."""

    def __init__(self, message: str = "Server error", status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)


class MaxRetriesExceededError(OpenRouterError):
    """Raised when max retries are exhausted."""

    def __init__(self, message: str = "Max retries exceeded", attempts: int = 0):
        self.attempts = attempts
        super().__init__(message)


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter client."""

    api_key: str = ""
    base_url: str = OPENROUTER_API_URL
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    concurrency_limit: int = 10
    timeout: float = 60.0
    default_model: str = "openai/gpt-3.5-turbo"

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("OPENROUTER_API_KEY", "")


# ============================================================================
# Helper Functions
# ============================================================================


def parse_retry_after(headers: Dict[str, str]) -> Optional[float]:
    """
    Parse Retry-After header value.

    Supports:
    - Integer seconds: "30"
    - Float seconds: "1.5"

    Returns None if header is missing or unparseable.
    """
    # Case-insensitive header lookup
    value = None
    for key, val in headers.items():
        if key.lower() == "retry-after":
            value = val
            break

    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def calculate_backoff_delay(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retry_after: Optional[float] = None,
) -> float:
    """
    Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap in seconds
        jitter: Add random jitter to prevent thundering herd
        retry_after: Server-specified Retry-After value (overrides calculation)

    Returns:
        Delay in seconds
    """
    # If server provided Retry-After, use it (capped by max_delay)
    if retry_after is not None:
        return min(retry_after, max_delay)

    # Exponential backoff: base_delay * 2^attempt
    delay = base_delay * (2 ** attempt)

    # Cap at max_delay
    delay = min(delay, max_delay)

    # Add jitter: random value between [delay, delay * 1.5]
    if jitter:
        delay = delay * (1 + random.random() * 0.5)

    return delay


# ============================================================================
# OpenRouter Client
# ============================================================================


class OpenRouterClient:
    """
    Async OpenRouter API client with rate-limit retry handling.

    Features:
    - Automatic retry with exponential backoff on 429
    - Retry on 5xx server errors
    - Retry on connection errors/timeouts
    - Semaphore-based concurrency limiting
    - Request/retry statistics tracking

    Usage:
        config = OpenRouterConfig(api_key="sk-...")
        async with OpenRouterClient(config) as client:
            response = await client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model="openai/gpt-3.5-turbo",
            )
    """

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.config = config or OpenRouterConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(self.config.concurrency_limit)

        # Statistics
        self._total_requests: int = 0
        self._total_retries: int = 0
        self._rate_limit_hits: int = 0

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_client(self):
        """Ensure httpx client is created."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://alvo-platform.com",
                    "X-Title": "ALVO Platform Dashboard",
                },
                timeout=self.config.timeout,
            )

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_stats(self) -> Dict[str, int]:
        """Get client statistics."""
        return {
            "total_requests": self._total_requests,
            "total_retries": self._total_retries,
            "rate_limit_hits": self._rate_limit_hits,
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a chat completion with automatic retry on rate limits.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (e.g., "openai/gpt-3.5-turbo")
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters passed to the API

        Returns:
            API response dict with 'id', 'choices', 'usage', etc.

        Raises:
            RateLimitError: If rate limited after all retries
            AuthenticationError: On invalid API key
            ModelNotFoundError: If model doesn't exist
            MaxRetriesExceededError: If all retries exhausted
            OpenRouterError: On other API errors
        """
        await self._ensure_client()

        payload = {
            "model": model or self.config.default_model,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        async with self._semaphore:
            return await self._request_with_retry("POST", "/chat/completions", json=payload)

    async def list_models(self) -> Dict[str, Any]:
        """List available models on OpenRouter."""
        await self._ensure_client()
        async with self._semaphore:
            return await self._request_with_retry("GET", "/models")

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with automatic retry on transient errors.

        Retries on:
        - 429 (Rate Limit) with exponential backoff
        - 5xx (Server Errors) with exponential backoff
        - Connection errors and timeouts
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                self._total_requests += 1

                response = await self._client.request(method, path, **kwargs)

                # Success
                if response.status_code == 200:
                    return response.json()

                # Handle errors - determine if retryable
                if response.status_code == 429:
                    retry_after = parse_retry_after(dict(response.headers))
                    delay = calculate_backoff_delay(
                        attempt=attempt,
                        base_delay=self.config.base_delay,
                        max_delay=self.config.max_delay,
                        jitter=self.config.jitter,
                        retry_after=retry_after,
                    )
                    self._total_retries += 1
                    self._rate_limit_hits += 1
                    logger.warning(
                        f"Rate limit hit (429). Attempt {attempt + 1}/{self.config.max_retries + 1}. "
                        f"Retrying in {delay:.2f}s (Retry-After: {retry_after})"
                    )
                    await asyncio.sleep(delay)
                    continue

                # Authentication error - no retry
                if response.status_code == 401:
                    raise AuthenticationError(
                        f"Authentication failed: {response.text}"
                    )

                # Not found - no retry
                if response.status_code == 404:
                    raise ModelNotFoundError(
                        f"Model or endpoint not found: {response.text}"
                    )

                # Server errors - retry
                if response.status_code >= 500:
                    delay = calculate_backoff_delay(
                        attempt=attempt,
                        base_delay=self.config.base_delay,
                        max_delay=self.config.max_delay,
                        jitter=self.config.jitter,
                    )
                    self._total_retries += 1
                    logger.warning(
                        f"Server error ({response.status_code}). Attempt {attempt + 1}/{self.config.max_retries + 1}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                    continue

                # Other client errors - raise immediately
                raise OpenRouterError(
                    f"API error {response.status_code}: {response.text}"
                )

            except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadTimeout) as e:
                last_exception = e
                delay = calculate_backoff_delay(
                    attempt=attempt,
                    base_delay=self.config.base_delay,
                    max_delay=self.config.max_delay,
                    jitter=self.config.jitter,
                )
                self._total_retries += 1
                logger.warning(
                    f"Connection error: {e}. Attempt {attempt + 1}/{self.config.max_retries + 1}. "
                    f"Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)
                continue

            except (AuthenticationError, ModelNotFoundError, OpenRouterError):
                # Don't retry non-retryable errors
                raise

        # All retries exhausted
        if last_exception:
            raise MaxRetriesExceededError(
                f"Failed after {self.config.max_retries + 1} attempts: {last_exception}",
                attempts=self.config.max_retries + 1,
            )

        raise RateLimitError(
            f"Rate limit exceeded after {self.config.max_retries + 1} attempts",
            retry_after=self.config.max_delay,
        )


# ============================================================================
# Convenience Functions
# ============================================================================


async def create_chat_completion(
    messages: List[Dict[str, str]],
    model: str = "openai/gpt-3.5-turbo",
    api_key: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function for one-off chat completion.

    Creates a client, makes the request, and closes the client.
    """
    config = OpenRouterConfig(api_key=api_key or "")
    async with OpenRouterClient(config) as client:
        return await client.chat_completion(messages, model=model, **kwargs)


def sync_chat_completion(
    messages: List[Dict[str, str]],
    model: str = "openai/gpt-3.5-turbo",
    api_key: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Synchronous wrapper for chat completion.

    For use in non-async contexts.
    """
    return asyncio.run(create_chat_completion(messages, model, api_key, **kwargs))
