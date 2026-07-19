"""LLM Provider Implementations.

This module contains concrete implementations of the LLMProvider interface
for various LLM providers.
"""

from typing import Any

from .base import LLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider


def get_provider(provider_name: str, api_key: str, **kwargs: Any) -> LLMProvider:
    """Factory function to get an LLM provider instance.

    Args:
        provider_name: Name of the provider ("openai", "anthropic", "mock")
        api_key: API key for the provider
        **kwargs: Additional provider-specific configuration

    Returns:
        LLMProvider: An instance of the requested provider

    Raises:
        ValueError: If the provider name is not supported
    """
    provider_name = provider_name.lower()
    if provider_name == "openai":
        return OpenAIProvider(api_key, **kwargs)
    elif provider_name == "anthropic":
        return AnthropicProvider(api_key, **kwargs)
    elif provider_name == "mock":
        from visionforgeai.providers.llm_mock import get_provider as get_mock_provider

        return get_mock_provider(provider_name, api_key, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


__all__ = ["LLMProvider", "OpenAIProvider", "AnthropicProvider", "get_provider"]
