"""Mock LLM provider for testing."""

from typing import AsyncGenerator, Dict, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model: str = "mock-model"
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class MockLLMProvider:
    async def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        # Echo back a shortened version of the prompt
        truncated = prompt[:50] + ("..." if len(prompt) > 50 else "")
        return LLMResponse(content=f"[MOCK] {truncated}")

    async def generate_stream(
        self, prompt: str, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        # Yield the mock response in chunks
        response = f"[MOCK] {prompt}"
        for char in response:
            yield char
            # small delay to simulate streaming? Not needed for test.

    async def get_available_models(self) -> list[str]:
        return ["mock-model"]

    async def health_check(self) -> bool:
        return True
