"""AI provider adapter.

Everything that talks to an LLM goes through the ``AIProvider`` interface.
Today this is Fireworks (serving Gemma); tomorrow it could be a local
ROCm/AMD inference server or any other provider. No other module should ever
import an HTTP client directly to call an LLM.
"""
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIProvider(ABC):
    """Abstract interface for any text-generation backend."""

    @abstractmethod
    async def complete(self, prompt: str, *, max_tokens: int = 800, temperature: float = 0.7) -> str:
        """Return a text completion for the given prompt."""
        ...


class FireworksAIProvider(AIProvider):
    """Calls the Fireworks API to run inference against a Gemma model."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def complete(self, prompt: str, *, max_tokens: int = 4096, temperature: float = 0.6) -> str:
        if not self._api_key:
            raise AIProviderError("FIREWORKS_API_KEY is not set.")

        payload = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": None,                 # Explicitly tells the model NOT to stop early unless it's done
            # "completion_window": None,    # Prevents arbitrary structural API timeouts
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/chat/completions", json=payload, headers=headers
                )
                response.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("Fireworks API call failed: %s", exc)
                raise AIProviderError(str(exc)) from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise AIProviderError(f"Unexpected Fireworks response shape: {data}") from exc


class MockAIProvider(AIProvider):
    """Deterministic offline provider used for local dev / demos without an API key."""

    async def complete(self, prompt: str, *, max_tokens: int = 800, temperature: float = 0.7) -> str:
        logger.info("MockAIProvider generating a stubbed response (no live API key set).")
        preview = prompt.strip().splitlines()[-1][:160] if prompt.strip() else ""
        return (
            "[MOCK OUTPUT — set AI_PROVIDER=fireworks and FIREWORKS_API_KEY to get real "
            f"Gemma-generated content]\n\nBased on the request: \"{preview}\"\n\n"
            "This is placeholder content generated locally so the full PersonaStudio AI "
            "pipeline can be demoed end-to-end without live API access."
        )


def get_ai_provider(provider_override: Optional[str] = None) -> AIProvider:
    """Factory returning the configured AIProvider implementation."""
    settings = get_settings()
    provider = provider_override or settings.ai_provider

    if provider == "fireworks":
        return FireworksAIProvider(
            api_key=settings.fireworks_api_key,
            base_url=settings.fireworks_base_url,
            model=settings.gemma_model,
        )
    return MockAIProvider()
