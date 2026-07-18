"""OpenAI LLM Provider Implementation.

This module provides a concrete implementation of the LLMProvider interface
for OpenAI's GPT models.
"""

import os
from typing import AsyncGenerator, Dict, Any, List, Optional
from openai import AsyncOpenAI
from .base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, api_key: str, **kwargs):
        """Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
            **kwargs: Additional configuration (organization, base_url, etc.)
        """
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=kwargs.get('organization'),
            base_url=kwargs.get('base_url')
        )
        self.default_model = kwargs.get('model', 'gpt-4o-mini')

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text completion from a prompt using OpenAI API.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse: The generated text and metadata
        """
        model = kwargs.get('model', self.default_model)

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k != 'model'}
            )

            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content,
                model=response.model,
                usage=dict(response.usage) if response.usage else None,
                finish_reason=choice.finish_reason
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text completion as a stream from a prompt using OpenAI API.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Yields:
            str: Chunks of generated text as they are generated
        """
        model = kwargs.get('model', self.default_model)

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **{k: v for k, v in kwargs.items() if k != 'model'}
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API streaming error: {str(e)}") from e

    async def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models.

        Returns:
            List[str]: List of available model identifiers
        """
        # Common OpenAI models - in production, this could be fetched from API
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible.

        Returns:
            bool: True if the API is accessible, False otherwise
        """
        try:
            # Attempt a minimal request to check connectivity
            await self.client.models.list()
            return True
        except Exception:
            return False