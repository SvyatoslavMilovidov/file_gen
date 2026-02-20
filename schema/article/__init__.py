"""
Article schemas — Pydantic схемы для генерации статей.
"""

from .article_schema import (
    HtmlGenerateSchema,
    ArticleResponseSchema,
)

__all__ = [
    "HtmlGenerateSchema",
    "ArticleResponseSchema",
]
