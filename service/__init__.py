"""
Service — бизнес-логика приложения.

Экспортирует все сервисы для удобного импорта:
    from service import HealthService, ArticleService
"""

from .health.health_service import HealthService
from .article.article_service import ArticleService
from .s3_storage_service import S3StorageService
from .gpt_formatter_service import GPTFormatterService

__all__ = [
    "HealthService",
    "ArticleService",
    "S3StorageService",
    "GPTFormatterService",
]
