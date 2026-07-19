"""Base LLM Provider Interface.

This module defines the abstract base class that all LLM providers must implement.
It ensures a consistent interface for interacting with different LLM services
(OpenAI, Anthropic, Ollama, etc.) without coupling the application to a specific provider.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Standard response format for LLM providers."""

    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for Large Language Model providers.

    All LLM providers must implement this interface to ensure compatibility
    with the LLMService and the rest of the application.
    """

    def __init__(self, api_key: str, **kwargs: Any):
        """Initialize the LLM provider.

        Args:
            api_key: The API key for the provider service
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self.default_model: str = kwargs.get("model", "unknown")

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text completion from a prompt.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse: The generated text and metadata
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Generate text completion as a stream from a prompt.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Yields:
            str: Chunks of generated text as they become available
        """
        # This is an abstract method that must be implemented by subclasses
        # Yielding an empty string to satisfy the generator protocol
        if False:  # pragma: no cover
            yield ""

    @abstractmethod
    async def get_available_models(self) -> list[str]:
        """Get list of available models for this provider.

        Returns:
            list[str]: List of available model identifiers
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider service is available and healthy.

        Returns:
            bool: True if the service is healthy, False otherwise
        """
        pass
