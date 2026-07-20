"""Local LLM Provider Implementation using llama.cpp.

This module provides a concrete implementation of the LLMProvider interface
for local LLM inference using llama.cpp Python bindings.
"""

import asyncio
import os
from typing import Any, AsyncGenerator, List, Optional

from llama_cpp import Llama

from .base import LLMProvider, LLMResponse


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using llama.cpp."""

    def __init__(self, model_path: str, **kwargs: Any):
        """Initialize the local LLM provider.

        Args:
            model_path: Path to the GGUF model file.
            **kwargs: Additional configuration (n_ctx, n_batch, n_threads, etc.)
        """
        super().__init__(model_path, **kwargs)
        self.model_path = model_path
        # Set default generation parameters
        self.n_ctx = kwargs.get('n_ctx', 2048)
        self.n_batch = kwargs.get('n_batch', 512)
        self.n_threads = kwargs.get('n_threads', os.cpu_count() or 4)
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 1000)
        self.top_p = kwargs.get('top_p', 0.95)
        self.top_k = kwargs.get('top_k', 40)
        self.repeat_penalty = kwargs.get('repeat_penalty', 1.1)
        self.seed = kwargs.get('seed', -1)

        # Initialize the model
        self.model = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_batch=self.n_batch,
            n_threads=self.n_threads,
            seed=self.seed,
            verbose=False,  # Set to True for debugging
        )
        self.default_model_name = os.path.basename(model_path)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text completion from a prompt using local LLM.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse: The generated text and metadata
        """
        # Override instance parameters with kwargs if provided
        temperature = kwargs.get('temperature', temperature)
        max_tokens = kwargs.get('max_tokens', max_tokens)
        top_p = kwargs.get('top_p', self.top_p)
        top_k = kwargs.get('top_k', self.top_k)
        repeat_penalty = kwargs.get('repeat_penalty', self.repeat_penalty)

        try:
            # Wrap synchronous llama.cpp call with asyncio.to_thread to avoid blocking
            response = await asyncio.to_thread(
                self.model,
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                echo=False,  # Don't echo the prompt
            )

            # Extract the generated text
            generated_text = response['choices'][0]['text']

            # Prepare usage information (llama.cpp provides token counts)
            usage = {
                'prompt_tokens': response['usage']['prompt_tokens'],
                'completion_tokens': response['usage']['completion_tokens'],
                'total_tokens': response['usage']['total_tokens'],
            }

            return LLMResponse(
                content=generated_text.strip(),
                model=self.default_model_name,
                usage=usage,
                finish_reason=response['choices'][0]['finish_reason'],
            )
        except Exception as e:
            raise RuntimeError(f"Local LLM generation error: {str(e)}") from e

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Generate text completion as a stream from a prompt using local LLM.

        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Yields:
            str: Chunks of generated text as they are generated
        """
        # Override instance parameters with kwargs if provided
        temperature = kwargs.get('temperature', temperature)
        max_tokens = kwargs.get('max_tokens', max_tokens)
        top_p = kwargs.get('top_p', self.top_p)
        top_k = kwargs.get('top_k', self.top_k)
        repeat_penalty = kwargs.get('repeat_penalty', self.repeat_penalty)

        try:
            # Create a streaming generation
            stream = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stream=True,  # Enable streaming
                echo=False,
            )

            for chunk in stream:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    text = chunk['choices'][0]['text']
                    if text:
                        yield text
        except Exception as e:
            raise RuntimeError(f"Local LLM streaming error: {str(e)}") from e

    async def get_available_models(self) -> List[str]:
        """Get list of available local models.

        Returns:
            List[str]: List of available model identifiers (just the loaded model for now)
        """
        # In a more advanced setup, we could scan a directory for multiple models
        return [self.default_model_name]

    async def health_check(self) -> bool:
        """Check if the local LLM is loaded and ready.

        Returns:
            bool: True if the model is loaded and ready, False otherwise
        """
        try:
            # Try a simple generation to see if the model is responsive
            _ = self.model("Hello", max_tokens=1, temperature=0.0, echo=False)
            return True
        except Exception:
            return False