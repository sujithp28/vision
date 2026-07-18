"""VisionForge AI - AI Workflow Engine.

This package implements a production-ready AI Workflow Platform capable of
generating various types of content including text, images, video, audio, and more.

The architecture follows Clean Architecture principles with:
- Provider abstraction layer (swap AI providers without changing business logic)
- Service layer (business logic)
- Repository layer (data persistence)
- API layer (FastAPI endpoints)
- Workflow orchestration
"""

__version__ = "0.1.0"
__author__ = "VisionForge AI Team"
__email__ = "dev@visionforge.ai"
__description__ = "AI Workflow Engine for generating multimodal content"

# Make key components easily accessible
from .main import app
from .config.settings import get_settings, Settings
from .services.llm_service import get_llm_service, LLMService

__all__ = [
    "app",
    "get_settings",
    "Settings",
    "get_llm_service",
    "LLMService",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]