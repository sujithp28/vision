"""Base abstract class for all LLM providers"""

from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from prompt
        
        Args:
            prompt: User prompt
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text stream from prompt
        
        Args:
            prompt: User prompt
            
        Yields:
            Text chunks as they become available
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy and available
        
        Returns:
            True if provider is operational
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models
        
        Returns:
            List of model names
        """
        pass
