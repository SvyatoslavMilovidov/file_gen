"""
Endpoints — HTTP роутеры для API v1.
"""

from .health import router as health_router
from .html import router as html_router

__all__ = [
    "health_router",
    "html_router",
]
