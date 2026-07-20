"""
VisionForge AI Provider Registry

Central registry for all AI providers.

Every provider (Mock, OpenAI, Gemini, Ollama, LiteLLM,
Claude, OpenRouter, etc.) is registered here.

Used by:
- API
- AI Core
- VisionForge MCP
- Agent Runtime
- Plugin System
"""

from __future__ import annotations

from typing import Dict, List

from .providers.base import LLMProvider


class ProviderRegistry:
    """Central registry for AI providers."""

    def __init__(self) -> None:
        self._providers: Dict[str, LLMProvider] = {}

    def register(self, name: str, provider: LLMProvider) -> None:
        """Register a provider."""

        key = name.lower()

        if key in self._providers:
            raise ValueError(f"Provider '{name}' is already registered.")

        self._providers[key] = provider

    def unregister(self, name: str) -> None:
        """Remove a provider."""

        self._providers.pop(name.lower(), None)

    def get(self, name: str) -> LLMProvider:
        """Return a registered provider."""

        key = name.lower()

        if key not in self._providers:
            available = ", ".join(self.list()) or "None"
            raise KeyError(
                f"Provider '{name}' not found. "
                f"Available providers: {available}"
            )

        return self._providers[key]

    def exists(self, name: str) -> bool:
        """Check whether a provider exists."""

        return name.lower() in self._providers

    def list(self) -> List[str]:
        """Return registered provider names."""

        return sorted(self._providers.keys())

    async def health(self) -> Dict[str, bool]:
        """Run health checks on all providers."""

        status: Dict[str, bool] = {}

        for name, provider in self._providers.items():
            try:
                status[name] = await provider.health_check()
            except Exception:
                status[name] = False

        return status

    def clear(self) -> None:
        """Remove all registered providers."""

        self._providers.clear()

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, name: str) -> bool:
        return self.exists(name)

    def __repr__(self) -> str:
        return (
            f"<ProviderRegistry "
            f"providers={self.list()}>"
        )


provider_registry = ProviderRegistry()