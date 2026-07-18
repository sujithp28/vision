"""Anthropic LLM Provider Implementation.

This module provides a concrete implementation of the LLMProvider interface
for Anthropic's Claude models.
"""

import os
from typing import AsyncGenerator, Dict, Any, List, Optional
from anthropic import AsyncAnthropic
from .base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider implementation."""

    def __init__(self, api_key: str, **kwargs):
        """Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = kwargs.get('model', 'claude-3-5-sonnet-20241022')

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text completion from a prompt using Anthropic API.

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
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **{k: v for k, v in kwargs.items() if k not in ['model', 'max_tokens', 'temperature']}
            )

            # Extract content from the first content block
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                } if response.usage else None,
                finish_reason=response.stop_reason
            )
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}") from e

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text completion as a stream from a prompt using Anthropic API.

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
            async with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **{k: v for k, v in kwargs.items() if k not in ['model', 'max_tokens', 'temperature']}
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise RuntimeError(f"Anthropic API streaming error: {str(e)}") from e

    async def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models.

        Returns:
            List[str]: List of available model identifiers
        """
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

    async def health_check(self) -> bool:
        """Check if Anthropic API is accessible.

        Returns:
            bool: True if the API is accessible, False otherwise
        """
        try:
            # Attempt a minimal request to check connectivity
            await self.client.messages.count_tokens(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False