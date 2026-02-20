"""
API — HTTP endpoints приложения.

Экспортирует app для использования в main.py
"""

from core import app
from .v1 import include_router  # noqa: F401 — подключает роутеры

__all__ = [
    "app",
]
