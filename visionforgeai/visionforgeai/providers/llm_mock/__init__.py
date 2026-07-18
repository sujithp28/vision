"""Mock LLM Provider Implementations."""

from .mock import MockLLMProvider, LLMResponse

def get_provider(provider_name: str, api_key: str, **kwargs):
    """Factory function to get a mock LLM provider instance.

    Args:
        provider_name: Name of the provider (should be "mock")
        api_key: API key (ignored for mock)
        **kwargs: Additional provider-specific configuration

    Returns:
        LLMProvider: An instance of the mock provider

    Raises:
        ValueError: If the provider name is not supported
    """
    provider_name = provider_name.lower()
    if provider_name == "mock":
        return MockLLMProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")

__all__ = [
    "LLMResponse",
    "MockLLMProvider",
    "get_provider"
]
