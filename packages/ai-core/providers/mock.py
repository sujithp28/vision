"""Mock provider for testing - returns deterministic responses"""

from typing import List, AsyncGenerator
from .base import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for testing without external dependencies"""
    
    def __init__(self):
        self.name = "mock"
        self.models = ["mock-model-1", "mock-model-2"]
    
    async def generate(self, prompt: str) -> str:
        """Generate mock response"""
        return f"Mock response to: {prompt[:50]}..."
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate mock streaming response"""
        response = f"Mock response to: {prompt[:50]}..."
        for chunk in response.split():
            yield chunk + " "
    
    async def health_check(self) -> bool:
        """Mock always healthy"""
        return True
    
    def get_available_models(self) -> List[str]:
        """Return mock models"""
        return self.models
