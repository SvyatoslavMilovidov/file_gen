"""
Schema — Pydantic схемы для валидации данных.

Экспортирует все схемы для удобного импорта:
    from schema import HtmlGenerateSchema, ArticleResponseSchema
"""

from .health.health_schema import HealthCheckResponseSchema
from .article.article_schema import HtmlGenerateSchema, ArticleResponseSchema

__all__ = [
    "HealthCheckResponseSchema",
    "HtmlGenerateSchema",
    "ArticleResponseSchema",
]
