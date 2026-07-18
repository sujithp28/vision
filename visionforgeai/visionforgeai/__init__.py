"""VisionForge AI Package Initialization.

This is the main package for VisionForge AI - an AI Workflow Engine.
"""

import os
import sys
from pathlib import Path

# Package metadata
__title__ = "VisionForge AI"
__description__ = "AI Workflow Engine for generating videos, images, text, and more"
__version__ = "0.1.0"
__author__ = "VisionForge AI Team"
__author_email__ = "dev@visionforge.ai"
__license__ = "MIT"
__copyright__ = "Copyright 2026 VisionForge AI"

# Ensure the package directory is in Python path
PACKAGE_DIR = Path(__file__).parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

# Export public interface
__all__ = [
    "__title__",
    "__description__",
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__"
]