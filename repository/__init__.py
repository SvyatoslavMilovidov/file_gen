"""
Repository — слой доступа к данным.

Экспортирует все репозитории для удобного импорта:
    from repository import BaseRepository, ArticleRepository
"""

from .base_repository import BaseRepository
from .article_repository import ArticleRepository

__all__ = [
    "BaseRepository",
    "ArticleRepository",
]
