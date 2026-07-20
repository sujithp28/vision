"""
VisionForge AI Core

The AI Core is responsible for:

- AI Provider Management
- Model Registry
- Prompt Management
- Streaming
- AI Agent Runtime (future)
- Tool Calling (future)
- Embeddings (future)
- RAG (future)
- VisionForge MCP Integration

This package is the central AI abstraction layer used by the
API, Workers, MCP Server, Plugins, and future AI Agents.
"""

from .provider_registry import (
    ProviderRegistry,
    provider_registry,
)

__version__ = "2.0.0"

__all__ = [
    "ProviderRegistry",
    "provider_registry",
]