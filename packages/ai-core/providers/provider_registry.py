'''
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

This module is the production-grade upgrade of the registry. It preserves
the existing LLMProvider interface and the original public method
signatures of ProviderRegistry while adding:

* A typed error hierarchy (ProviderRegistryError and friends).
* A shared normalize_provider_name helper so every lookup is
  case-insensitive and consistent.
* An opt-in replace flag on register.
* A richer RegistryHealthReport returned alongside the legacy
  Dict[str, bool] health snapshot for full async-safety.
* Module-level convenience helpers mirroring the singleton.
'''

from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from .base import LLMProvider


# ---------------------------------------------------------------------- #
# Errors                                                                 #
# ---------------------------------------------------------------------- #


class ProviderRegistryError(Exception):
    """Base class for all registry-level errors."""


class ProviderNotFoundError(ProviderRegistryError, KeyError):
    """Raised when a requested provider is not registered.

    Inherits from KeyError so legacy ``except KeyError`` blocks
    continue to catch this error.
    """


class ProviderAlreadyRegisteredError(ProviderRegistryError, ValueError):
    """Raised when attempting to register a provider under a duplicate name.

    Inherits from ValueError so legacy ``except ValueError`` blocks
    continue to catch this error.
    """


class InvalidProviderError(ProviderRegistryError, TypeError):
    """Raised when a non-LLMProvider object is passed to the registry."""


# ---------------------------------------------------------------------- #
# Helpers                                                                #
# ---------------------------------------------------------------------- #


def normalize_provider_name(name):
    """Return the canonical (lowercased, stripped) form of a provider name.

    Args:
        name: The raw provider name.

    Returns:
        The normalized name.

    Raises:
        TypeError: If name is not a string.
        ValueError: If name is empty or whitespace-only.
    """
    if not isinstance(name, str):
        raise TypeError(
            "provider name must be a str, got " + type(name).__name__
        )
    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("provider name must not be empty")
    return normalized


def _utcnow_iso():
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(tz=UTC).isoformat()


async def _invoke_health_check(provider, name):
    """Invoke provider.health_check() and normalize the outcome.

    Handles both sync and async health_check implementations. Returns
    a (healthy, detail) tuple. Any exception is converted into
    (False, "ExcType: message") so it never propagates.
    """
    try:
        result = provider.health_check()
        if inspect.isawaitable(result):
            result = await result
        return bool(result), None
    except Exception as exc:
        message = str(exc) or type(exc).__name__
        if not message:
            return False, type(exc).__name__
        return False, type(exc).__name__ + ": " + message


# ---------------------------------------------------------------------- #
# Health report                                                          #
# ---------------------------------------------------------------------- #


@dataclass(frozen=True)
class HealthStatus:
    """Health snapshot for a single provider."""

    name: str
    healthy: bool
    detail: Optional[str] = None

    def to_dict(self):
        return {"name": self.name, "healthy": self.healthy, "detail": self.detail}


@dataclass(frozen=True)
class RegistryHealthReport:
    """Aggregate health report for a ProviderRegistry."""

    statuses: Dict[str, HealthStatus] = field(default_factory=dict)
    checked_at: str = ""

    @property
    def healthy(self):
        return all(status.healthy for status in self.statuses.values())

    @property
    def unhealthy(self):
        return [name for name, status in self.statuses.items() if not status.healthy]

    def to_dict(self):
        return {
            "checked_at": self.checked_at,
            "healthy": self.healthy,
            "providers": {
                name: status.to_dict() for name, status in self.statuses.items()
            },
        }


# ---------------------------------------------------------------------- #
# Registry                                                               #
# ---------------------------------------------------------------------- #


class ProviderRegistry:
    """Central registry for AI providers.

    The registry is the single source of truth for which providers are
    available to the rest of the application. Providers are looked up by
    name, normalized to lowercase.

    Design notes:
        * SRP -- the registry only manages identity, lookup, and
          lifecycle; generation and streaming are delegated to the
          provider itself.
        * OCP -- new providers can be added without modifying this class.
        * LSP -- any object satisfying the LLMProvider contract is
          accepted.
        * DIP -- callers depend on LLMProvider, not concrete
          implementations.

    Backward compatibility:
        All previously-existing public methods keep their original
        signatures and return-type contracts. New behavior is opt-in
        (e.g. register(..., replace=True)).
    """

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}

    # ----- Registration lifecycle ----- #

    def register(self, name, provider, *, replace=False):
        """Register provider under name.

        Args:
            name: The provider lookup name (case-insensitive).
            provider: The LLMProvider instance to register.
            replace: If True, replace an existing provider registered
                under the same name instead of raising. Defaults to False
                (preserves the original behavior).

        Returns:
            The registered provider instance.

        Raises:
            InvalidProviderError: If provider is not an LLMProvider
                instance.
            ValueError: If name is empty or not a string.
            ProviderAlreadyRegisteredError: If a provider is already
                registered under name and replace is False.
        """
        if not isinstance(provider, LLMProvider):
            raise InvalidProviderError(
                "expected LLMProvider instance, got " + type(provider).__name__
            )
        key = normalize_provider_name(name)
        if key in self._providers and not replace:
            raise ProviderAlreadyRegisteredError(
                "Provider '" + name + "' is already registered."
            )
        self._providers[key] = provider
        return provider

    def unregister(self, name):
        """Remove a provider by name.

        Args:
            name: The provider lookup name (case-insensitive).

        Returns:
            The removed LLMProvider or None if no provider was registered
            under that name.

        Note:
            The original implementation returned None unconditionally.
            The return type is now Optional[LLMProvider]; existing
            callers that ignore the return value are unaffected.
        """
        if not isinstance(name, str):
            return None
        normalized = name.strip().lower()
        if not normalized:
            return None
        return self._providers.pop(normalized, None)

    # ----- Lookups ----- #

    def get(self, name):
        """Return the provider registered under name.

        Raises:
            ProviderNotFoundError: If no provider is registered under
                name (also a KeyError, so legacy except KeyError still
                works).
        """
        key = normalize_provider_name(name)
        if key not in self._providers:
            available = ", ".join(self.list()) or "None"
            raise ProviderNotFoundError(
                "Provider '"
                + name
                + "' not found. Available providers: "
                + available
            )
        return self._providers[key]

    def exists(self, name):
        """Return whether a provider is registered under name."""
        if not isinstance(name, str):
            return False
        key = name.strip().lower()
        if not key:
            return False
        return key in self._providers

    def list(self):
        """Return a sorted list of registered provider names."""
        return sorted(self._providers.keys())

    def all(self):
        """Return a snapshot list of the currently registered providers."""
        return list(self._providers.values())

    # ----- Health ----- #

    async def health(self):
        """Run health checks on all providers.

        Returns a Dict[str, bool] identical in shape to the original
        implementation, so existing callers continue to work unchanged.

        For richer per-provider detail (status, error message, timestamp),
        use health_report.
        """
        report = await self.health_report()
        return {name: status.healthy for name, status in report.statuses.items()}

    async def health_report(self):
        """Run health checks and return a rich RegistryHealthReport.

        Failures in individual providers are isolated: one misbehaving
        provider cannot prevent the report from being produced.
        """
        providers = list(self._providers.items())
        if providers:
            coros = [
                _invoke_health_check(provider, name)
                for name, provider in providers
            ]
            results = await asyncio.gather(*coros)
        else:
            results = []

        statuses: Dict[str, HealthStatus] = {}
        for (name, _provider), (healthy, detail) in zip(providers, results):
            statuses[name] = HealthStatus(
                name=name, healthy=healthy, detail=detail
            )

        return RegistryHealthReport(
            statuses=statuses, checked_at=_utcnow_iso()
        )

    # ----- Bulk operations ----- #

    def clear(self):
        """Remove all registered providers."""
        self._providers.clear()

    # ----- Dunder / container protocol ----- #

    def __len__(self):
        return len(self._providers)

    def __contains__(self, name):
        return isinstance(name, str) and self.exists(name)

    def __repr__(self):
        return "<ProviderRegistry providers=" + repr(self.list()) + ">"


# ---------------------------------------------------------------------- #
# Module-level singleton + convenience helpers                          #
# ---------------------------------------------------------------------- #


provider_registry = ProviderRegistry()
"""Process-wide default ProviderRegistry instance.

Preserved at the same import path so existing imports keep working.
"""


def register(name, provider, *, replace=False):
    """Register provider on the default provider_registry."""
    return provider_registry.register(name, provider, replace=replace)


def unregister(name):
    """Unregister a provider on the default provider_registry."""
    return provider_registry.unregister(name)


def get(name):
    """Get a provider from the default provider_registry by name."""
    return provider_registry.get(name)


def exists(name):
    """Return whether the default provider_registry has name."""
    return provider_registry.exists(name)


def list_providers():
    """Return the sorted list of provider names on the default registry."""
    return provider_registry.list()


async def health():
    """Run health checks on the default provider_registry."""
    return await provider_registry.health()


async def health_report():
    """Return a rich RegistryHealthReport from the default registry."""
    return await provider_registry.health_report()


def clear():
    """Remove all providers from the default provider_registry."""
    provider_registry.clear()


__all__ = [
    "ProviderRegistry",
    "provider_registry",
    "ProviderRegistryError",
    "ProviderNotFoundError",
    "ProviderAlreadyRegisteredError",
    "InvalidProviderError",
    "HealthStatus",
    "RegistryHealthReport",
    "normalize_provider_name",
    "register",
    "unregister",
    "get",
    "exists",
    "list_providers",
    "health",
    "health_report",
    "clear",
]