"""
HTML endpoints — эндпоинты для генерации HTML-статей.
"""

from .post import router as html_post_router
from .get import router as html_get_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(html_post_router)
router.include_router(html_get_router)

__all__ = [
    "router",
]
