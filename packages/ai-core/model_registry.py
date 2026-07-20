"""
VisionForge AI Model Registry

Central registry for AI models across all providers.

A model is described by a :class:`ModelInfo` dataclass that captures the
model's identity, its owning provider, and a set of capability flags
(streaming, tools, vision, audio, embeddings, reasoning, JSON mode,
images) plus operational metadata (context window, max output tokens,
default-ness, deprecation).

The registry is intentionally **independent** from
:mod:`packages.ai_core.provider_registry` -- it does not import or call
it. A consumer that needs to wire a model to its provider can do so
explicitly, which keeps the responsibilities cleanly separated and
avoids a circular dependency between the two registries.

Capabilities
------------
* Register a model
* Remove a model
* Retrieve a model by name
* List all models
* Check whether a model exists
* Group models by provider
* Support aliases (alternative names that resolve to the same model)
* Support a default model per provider
* Prevent duplicate registrations
* Normalize model names (case-insensitive)
* Provide typed exceptions

Backwards compatibility
-----------------------
This module is additive. It introduces no new public types in
:mod:`packages.ai_core.providers.base` and does not require
:mod:`packages.ai_core.providers.mock` to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Dict, Iterable, List, Optional, Tuple


# ---------------------------------------------------------------------- #
# Errors                                                                 #
# ---------------------------------------------------------------------- #


class ModelRegistryError(Exception):
    """Base class for all model-registry-level errors."""


class ModelNotFoundError(ModelRegistryError, KeyError):
    """Raised when a requested model is not registered.

    Inherits from :class:`KeyError` so legacy ``except KeyError`` blocks
    continue to catch this error.
    """


class ModelAlreadyRegisteredError(ModelRegistryError, ValueError):
    """Raised when attempting to register a model under a duplicate name.

    Inherits from :class:`ValueError` for backwards-compatible catch
    behavior.
    """


class InvalidModelError(ModelRegistryError, TypeError):
    """Raised when a non-:class:`ModelInfo` object is passed to the registry."""


class AliasConflictError(ModelRegistryError, ValueError):
    """Raised when an alias already resolves to a different model."""


# ---------------------------------------------------------------------- #
# Helpers                                                                #
# ---------------------------------------------------------------------- #


def normalize_model_name(name):
    """Return the canonical (lowercased, stripped) form of a model name.

    Args:
        name: The raw model name or alias.

    Returns:
        The normalized name.

    Raises:
        TypeError: If ``name`` is not a string.
        ValueError: If ``name`` is empty or whitespace-only.
    """

    if not isinstance(name, str):
        raise TypeError(
            "model name must be a str, got " + type(name).__name__
        )
    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("model name must not be empty")
    return normalized


def _utcnow_iso():
    """Return the current UTC time as an ISO-8601 string."""

    return datetime.now(tz=UTC).isoformat()


# ---------------------------------------------------------------------- #
# Model metadata                                                         #
# ---------------------------------------------------------------------- #


@dataclass(frozen=True)
class ModelCapabilities:
    """Immutable set of capability flags for a model.

    Every flag is keyword-only and defaults to ``False`` so adding new
    flags is a non-breaking change.
    """

    streaming: bool = False
    tools: bool = False
    vision: bool = False
    audio: bool = False
    embeddings: bool = False
    reasoning: bool = False
    json_mode: bool = False
    images: bool = False

    def supports(self, capability):
        """Return whether the given capability flag is enabled.

        Accepts a :class:`ModelCapabilities` field name (e.g. ``"streaming"``)
        or another :class:`ModelCapabilities` instance for convenience.
        """

        if isinstance(capability, ModelCapabilities):
            other = capability
            return all(
                getattr(self, name) or not getattr(other, name)
                for name in (
                    "streaming",
                    "tools",
                    "vision",
                    "audio",
                    "embeddings",
                    "reasoning",
                    "json_mode",
                    "images",
                )
            )
        if not isinstance(capability, str):
            raise TypeError(
                "capability must be a str or ModelCapabilities, got "
                + type(capability).__name__
            )
        if not hasattr(self, capability):
            raise AttributeError(
                "ModelCapabilities has no flag named " + repr(capability)
            )
        return bool(getattr(self, capability))


@dataclass(frozen=True)
class ModelInfo:
    """Immutable metadata for a single registered model.

    Attributes:
        model_name: Canonical, lowercased model identifier.
        provider_name: Owning provider's lowercased identifier.
        display_name: Human-friendly display name. Defaults to
            ``model_name`` if not provided.
        context_window: Maximum number of input tokens the model accepts.
            ``None`` if unknown.
        max_output_tokens: Maximum number of output tokens the model can
            produce. ``None`` if unknown.
        capabilities: :class:`ModelCapabilities` describing what the
            model can do.
        is_default: Whether this model is the default for its provider.
        deprecated: Whether the model is marked as deprecated.
        aliases: Lowercased alternative names that resolve to this model.
        created_at: ISO-8601 timestamp of registration.
        extra: Free-form metadata for forward compatibility.
    """

    model_name: str
    provider_name: str
    display_name: Optional[str] = None
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    is_default: bool = False
    deprecated: bool = False
    aliases: Tuple[str, ...] = field(default_factory=tuple)
    created_at: str = field(default_factory=_utcnow_iso)
    extra: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        # ``frozen=True`` forbids assignment, so we normalize via ``object.__setattr__``.
        object.__setattr__(self, "model_name", normalize_model_name(self.model_name))
        object.__setattr__(
            self, "provider_name", normalize_model_name(self.provider_name)
        )
        if self.display_name is None:
            object.__setattr__(self, "display_name", self.model_name)
        if not isinstance(self.capabilities, ModelCapabilities):
            raise InvalidModelError(
                "capabilities must be a ModelCapabilities instance, got "
                + type(self.capabilities).__name__
            )
        if self.context_window is not None and self.context_window < 0:
            raise ValueError("context_window must be non-negative")
        if self.max_output_tokens is not None and self.max_output_tokens < 0:
            raise ValueError("max_output_tokens must be non-negative")
        normalized_aliases = tuple(
            sorted({normalize_model_name(a) for a in self.aliases if a})
        )
        # Aliases must not collide with the canonical name or each other.
        if self.model_name in normalized_aliases:
            raise ValueError(
                "alias '" + self.model_name + "' collides with model_name"
            )
        object.__setattr__(self, "aliases", normalized_aliases)
        if not isinstance(self.extra, dict):
            raise InvalidModelError(
                "extra must be a dict, got " + type(self.extra).__name__
            )

    # ----- Convenience ----- #

    @property
    def all_names(self):
        """Return every name (canonical + aliases) this model is reachable by."""

        return (self.model_name,) + self.aliases

    def supports(self, capability):
        """Forward to :meth:`ModelCapabilities.supports`."""

        return self.capabilities.supports(capability)

    def with_updates(self, **changes):
        """Return a copy of this :class:`ModelInfo` with the given fields updated."""

        return replace(self, **changes)

    def to_dict(self):
        """Return a JSON-serializable dictionary representation."""

        return {
            "model_name": self.model_name,
            "provider_name": self.provider_name,
            "display_name": self.display_name,
            "context_window": self.context_window,
            "max_output_tokens": self.max_output_tokens,
            "capabilities": {
                "streaming": self.capabilities.streaming,
                "tools": self.capabilities.tools,
                "vision": self.capabilities.vision,
                "audio": self.capabilities.audio,
                "embeddings": self.capabilities.embeddings,
                "reasoning": self.capabilities.reasoning,
                "json_mode": self.capabilities.json_mode,
                "images": self.capabilities.images,
            },
            "is_default": self.is_default,
            "deprecated": self.deprecated,
            "aliases": list(self.aliases),
            "created_at": self.created_at,
            "extra": dict(self.extra),
        }


# ---------------------------------------------------------------------- #
# Registry                                                               #
# ---------------------------------------------------------------------- #


class ModelRegistry:
    """Central registry for AI models.

    The registry is the single source of truth for which models are
    available to the rest of the application, independent of the
    :class:`ProviderRegistry`. Both lookups (canonical name and alias)
    are case-insensitive.

    Design notes:
        * **SRP** -- the registry only manages model identity, lookup,
          and metadata. Routing a model to its provider is the caller's
          job, by design.
        * **OCP** -- new metadata fields and capability flags are
          additive; existing callers see no breaking change.
        * **LSP** -- any :class:`ModelInfo` is accepted, regardless of
          which provider it belongs to.
        * **DIP** -- callers depend on :class:`ModelInfo` and
          :class:`ModelCapabilities`, not concrete providers.
    """

    def __init__(self):
        # name -> ModelInfo
        self._models: Dict[str, ModelInfo] = {}
        # alias -> model_name
        self._aliases: Dict[str, str] = {}
        # provider_name -> canonical default model_name
        self._defaults: Dict[str, str] = {}

    # ----- Registration ----- #

    def register(self, model, *, replace=False, set_default_if_none=False):
        """Register ``model`` under :attr:`ModelInfo.model_name`.

        Args:
            model: The :class:`ModelInfo` to register.
            replace: If ``True``, replace an existing model registered
                under the same name (and remove its aliases). Defaults to
                ``False`` (preserves duplicate-prevention behavior).
            set_default_if_none: If ``True`` and the model is not already
                marked as default, mark it as the default for its
                provider when no other default exists. The model's own
                ``is_default`` flag always wins.

        Returns:
            The registered :class:`ModelInfo` (the same instance for
            fluent use).

        Raises:
            InvalidModelError: If ``model`` is not a :class:`ModelInfo`.
            ModelAlreadyRegisteredError: If a model with the same name is
                already registered and ``replace`` is ``False``.
            AliasConflictError: If any of the model's aliases is already
                in use by a different model.
        """

        if not isinstance(model, ModelInfo):
            raise InvalidModelError(
                "expected ModelInfo instance, got " + type(model).__name__
            )

        key = model.model_name

        if key in self._models and not replace:
            raise ModelAlreadyRegisteredError(
                "Model '" + model.model_name + "' is already registered."
            )

        # Validate aliases don't collide with existing aliases belonging
        # to a *different* model.
        for alias in model.aliases:
            if not isinstance(alias, str):
                raise InvalidModelError(
                    "alias must be a str, got " + type(alias).__name__
                )
            existing_target = self._aliases.get(alias)
            if existing_target is not None and existing_target != key:
                raise AliasConflictError(
                    "alias '"
                    + alias
                    + "' is already used by model '"
                    + existing_target
                    + "'"
                )

        # If replacing, drop old alias mappings and the old default
        # pointer if it pointed here.
        if key in self._models:
            old = self._models[key]
            for old_alias in old.aliases:
                self._aliases.pop(old_alias, None)
            if self._defaults.get(old.provider_name) == key:
                self._defaults.pop(old.provider_name, None)

        self._models[key] = model
        for alias in model.aliases:
            self._aliases[alias] = key

        # Determine the effective is_default flag.
        if model.is_default:
            # Marking a model default clears any other default for the provider.
            prior_default = self._defaults.get(model.provider_name)
            if prior_default is not None and prior_default != key:
                self._models[prior_default] = self._models[prior_default].with_updates(
                    is_default=False
                )
            self._defaults[model.provider_name] = key
        elif set_default_if_none and model.provider_name not in self._defaults:
            promoted = model.with_updates(is_default=True)
            self._models[key] = promoted
            self._defaults[model.provider_name] = key

        return model

    def unregister(self, name):
        """Remove a model by name or alias.

        Args:
            name: A canonical model name or an alias (case-insensitive).

        Returns:
            The removed :class:`ModelInfo` or ``None`` if not found.
        """

        try:
            normalized = normalize_model_name(name)
        except (TypeError, ValueError):
            return None

        model = self._resolve(normalized)
        if model is None:
            return None
        return self._remove_model(model.model_name)

    def _remove_model(self, key):
        model = self._models.pop(key, None)
        if model is None:
            return None
        for alias in model.aliases:
            self._aliases.pop(alias, None)
        if self._defaults.get(model.provider_name) == key:
            self._defaults.pop(model.provider_name, None)
        return model

    # ----- Lookups ----- #

    def get(self, name):
        """Return the model registered under ``name`` or one of its aliases.

        Raises:
            ModelNotFoundError: If no model matches ``name``.
        """

        model = self._resolve_raw(name)
        if model is None:
            raise ModelNotFoundError(
                "No model registered under name '" + str(name) + "'"
            )
        return model

    def try_get(self, name):
        """Return the model registered under ``name`` or ``None``."""

        return self._resolve_raw(name)

    def _resolve(self, normalized):
        """Return the :class:`ModelInfo` for a normalized name, or ``None``."""

        if normalized in self._models:
            return self._models[normalized]
        target = self._aliases.get(normalized)
        if target is not None:
            return self._models.get(target)
        return None

    def _resolve_raw(self, name):
        """Look up a model by raw (non-normalized) name or alias."""

        try:
            normalized = normalize_model_name(name)
        except (TypeError, ValueError):
            return None
        return self._resolve(normalized)

    def exists(self, name):
        """Return whether a model is registered under ``name`` or one of its aliases."""

        return self._resolve_raw(name) is not None

    def list(self):
        """Return a sorted list of registered model names."""

        return sorted(self._models)

    def list_all(self):
        """Return a sorted list of all reachable names (canonical + aliases)."""

        names = set(self._models)
        names.update(self._aliases)
        return sorted(names)

    def list_by_provider(self, provider_name):
        """Return the registered models for the given provider.

        Args:
            provider_name: The provider name (case-insensitive).

        Returns:
            A list of :class:`ModelInfo` sorted by ``model_name``.
        """

        try:
            normalized = normalize_model_name(provider_name)
        except (TypeError, ValueError):
            return []
        return sorted(
            (m for m in self._models.values() if m.provider_name == normalized),
            key=lambda m: m.model_name,
        )

    def providers(self):
        """Return a sorted list of distinct provider names that have models."""

        return sorted({m.provider_name for m in self._models.values()})

    def group_by_provider(self):
        """Return a ``{provider_name: [ModelInfo, ...]}`` mapping.

        Provider names are sorted; the model list per provider is sorted
        by ``model_name``.
        """

        groups: Dict[str, List[ModelInfo]] = {}
        for model in self._models.values():
            groups.setdefault(model.provider_name, []).append(model)
        for provider_models in groups.values():
            provider_models.sort(key=lambda m: m.model_name)
        return dict(sorted(groups.items()))

    def aliases_of(self, name):
        """Return the aliases for the model identified by ``name``.

        Returns an empty tuple if the model is not found.
        """

        model = self._resolve_raw(name)
        if model is None:
            return ()
        return model.aliases

    def resolve_alias(self, alias):
        """Return the canonical :class:`ModelInfo` for ``alias``.

        Returns ``None`` if the alias is not registered.
        """

        return self._resolve_raw(alias)

    # ----- Defaults ----- #

    def set_default(self, provider_name, model_name):
        """Mark ``model_name`` as the default for ``provider_name``.

        Raises:
            ModelNotFoundError: If either provider or model is unknown.
        """

        try:
            provider = normalize_model_name(provider_name)
            target = normalize_model_name(model_name)
        except (TypeError, ValueError) as exc:
            raise ModelNotFoundError(str(exc)) from exc

        model = self._models.get(target)
        if model is None or model.provider_name != provider:
            raise ModelNotFoundError(
                "model '"
                + target
                + "' is not registered for provider '"
                + provider
                + "'"
            )
        prior = self._defaults.get(provider)
        if prior is not None and prior != target:
            self._models[prior] = self._models[prior].with_updates(is_default=False)
        self._models[target] = model.with_updates(is_default=True)
        self._defaults[provider] = target

    def get_default(self, provider_name):
        """Return the default :class:`ModelInfo` for ``provider_name``.

        Returns ``None`` if no default is set.
        """

        try:
            provider = normalize_model_name(provider_name)
        except (TypeError, ValueError):
            return None
        target = self._defaults.get(provider)
        if target is None:
            return None
        return self._models.get(target)

    # ----- Bulk operations ----- #

    def clear(self):
        """Remove all registered models."""

        self._models.clear()
        self._aliases.clear()
        self._defaults.clear()

    # ----- Dunder / container protocol ----- #

    def __len__(self):
        return len(self._models)

    def __contains__(self, name):
        return self.exists(name)

    def __iter__(self):
        return iter(sorted(self._models))

    def __repr__(self):
        return "<ModelRegistry models=" + repr(self.list()) + ">"


# ---------------------------------------------------------------------- #
# Module-level singleton + convenience helpers                          #
# ---------------------------------------------------------------------- #


model_registry = ModelRegistry()
"""Process-wide default :class:`ModelRegistry` instance."""


def register(model, *, replace=False, set_default_if_none=False):
    """Register ``model`` on the default :data:`model_registry`."""

    return model_registry.register(
        model, replace=replace, set_default_if_none=set_default_if_none
    )


def unregister(name):
    """Unregister the model identified by ``name`` on the default registry."""

    return model_registry.unregister(name)


def get(name):
    """Get a model from the default :data:`model_registry` by name or alias."""

    return model_registry.get(name)


def try_get(name):
    """Try to get a model from the default :data:`model_registry`."""

    return model_registry.try_get(name)


def exists(name):
    """Return whether the default :data:`model_registry` has ``name``."""

    return model_registry.exists(name)


def list_models():
    """Return the sorted list of model names on the default registry."""

    return model_registry.list()


def list_by_provider(provider_name):
    """Return models for ``provider_name`` on the default registry."""

    return model_registry.list_by_provider(provider_name)


def providers():
    """Return the sorted list of provider names on the default registry."""

    return model_registry.providers()


def group_by_provider():
    """Return a ``{provider_name: [ModelInfo, ...]}`` mapping."""

    return model_registry.group_by_provider()


def set_default(provider_name, model_name):
    """Set the default model for ``provider_name`` on the default registry."""

    return model_registry.set_default(provider_name, model_name)


def get_default(provider_name):
    """Return the default model for ``provider_name`` on the default registry."""

    return model_registry.get_default(provider_name)


def resolve_alias(alias):
    """Resolve an alias to its canonical :class:`ModelInfo` on the default registry."""

    return model_registry.resolve_alias(alias)


def clear():
    """Remove all models from the default :data:`model_registry`."""

    model_registry.clear()


__all__ = [
    "ModelRegistry",
    "model_registry",
    "ModelInfo",
    "ModelCapabilities",
    "ModelRegistryError",
    "ModelNotFoundError",
    "ModelAlreadyRegisteredError",
    "InvalidModelError",
    "AliasConflictError",
    "normalize_model_name",
    "register",
    "unregister",
    "get",
    "try_get",
    "exists",
    "list_models",
    "list_by_provider",
    "providers",
    "group_by_provider",
    "set_default",
    "get_default",
    "resolve_alias",
    "clear",
]