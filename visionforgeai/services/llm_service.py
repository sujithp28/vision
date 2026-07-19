"""LLM Service Layer.

This service provides a high-level interface for working with LLMs,
abstracting away the provider-specific details and providing common
functionality like prompt templating, caching, and error handling.
"""

import logging
from typing import Optional, AsyncGenerator

from ..config.settings import get_settings
from ..providers.llm import get_provider, LLMProvider

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LLM provider interactions."""

    def __init__(self) -> None:
        """Initialize the LLM service."""
        self.settings = get_settings()
        self._provider: Optional[LLMProvider] = None
        self._provider_name: Optional[str] = None

    def _get_provider(self) -> LLMProvider:
        """Get or create the LLM provider instance.

        Returns:
            LLMProvider: The configured LLM provider

        Raises:
            RuntimeError: If no valid API key is found for the selected provider
        """
        # Return cached provider if it exists and hasn't changed
        if self._provider and self._provider_name == self.settings.llm_provider:
            return self._provider

        # Determine which API key to use
        api_key = None
        partner_name = self.settings.llm_provider.lower()

        if partner_name == "openai":
            api_key = self.settings.openai_api_key or self.settings.llm_api_key
        elif partner_name == "anthropic":
            api_key = self.settings.anthropic_api_key or self.settings.llm_api_key
        else:
            # For other providers or generic API key
            api_key = self.settings.llm_api_key

        if not api_key:
            raise RuntimeError(
                f"No API key found for provider '{partner_name}'. "
                f"Please set the appropriate API key in your environment variables."
            )

        # Create the provider instance
        try:
            self._provider = get_provider(
                provider_name=partner_name,
                api_key=api_key,
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )
            self._provider_name = partner_name
            logger.info(f"Initialized LLM provider: {partner_name}")
            return self._provider
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider {partner_name}: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate (overrides config)
            temperature: Sampling temperature (0.0-1.0, overrides config)
            **kwargs: Additional provider-specific parameters

        Returns:
            str: The generated text

        Raises:
            RuntimeError: If generation fails
        """
        try:
            provider = self._get_provider()
            result = await provider.generate(
                prompt=prompt,
                max_tokens=max_tokens or self.settings.llm_max_tokens,
                temperature=temperature or self.settings.llm_temperature,
                **kwargs,
            )
            return result.content
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise RuntimeError(f"Failed to generate text: {str(e)}") from e

    async def generate_text_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate text as a stream from a prompt.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate (overrides config)
            temperature: Sampling temperature (0.0-1.0, overrides config)
            **kwargs: Additional provider-specific parameters

        Yields:
            str: Chunks of generated text

        Raises:
            RuntimeError: If streaming fails
        """
        try:
            provider = self._get_provider()
            async for chunk in provider.generate_stream(
                prompt=prompt,
                max_tokens=max_tokens or self.settings.llm_max_tokens,
                temperature=temperature or self.settings.llm_temperature,
                **kwargs,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Text generation streaming failed: {e}")
            raise RuntimeError(f"Failed to generate text stream: {str(e)}") from e

    async def get_available_models(self) -> list[str]:
        """Get list of available models from the current provider.

        Returns:
            list[str]: List of available model identifiers
        """
        try:
            provider = self._get_provider()
            return await provider.get_available_models()
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            # Return a fallback list based on common models
            if self.settings.llm_provider.lower() == "openai":
                return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
            elif self.settings.llm_provider.lower() == "anthropic":
                return ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
            return []

    async def health_check(self) -> bool:
        """Check if the LLM service is healthy.

        Returns:
            bool: True if the service is healthy, False otherwise
        """
        try:
            provider = self._get_provider()
            return await provider.health_check()
        except Exception as e:
            logger.warning(f"LLM service health check failed: {e}")
            return False

    def get_provider_info(self) -> dict:
        """Get information about the currently configured provider.

        Returns:
            dict: Provider information including name and configuration
        """
        if not self._provider:
            return {"provider": None, "status": "not_initialized"}

        return {
            "provider": self._provider_name,
            "model": getattr(self._provider, 'default_model', 'unknown'),
            "status": "initialized",
        }


# Global service instance (singleton pattern)
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service instance (singleton).

    Returns:
        LLMService: The LLM service instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
