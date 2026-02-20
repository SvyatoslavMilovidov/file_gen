"""
GET /api/v1/html/{article_id} — получение метаданных HTML-статьи.

## Бизнес-контекст
Возвращает метаданные статьи по ID (URL, тип, дата создания).
Не возвращает содержимое — для этого используется public_url.

## Входные данные
- article_id: ID статьи (path parameter)

## Выходные данные
- ArticleResponseSchema с метаданными
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from core.exceptions import ArticleNotFoundError
from schema.article.article_schema import ArticleResponseSchema
from service.article.article_service import ArticleService
from service.s3_storage_service import S3StorageService
from service.gpt_formatter_service import GPTFormatterService
from repository.article_repository import ArticleRepository

router = APIRouter()

# Инициализация зависимостей
_s3_service = S3StorageService()
_gpt_service = GPTFormatterService()
_article_repo = ArticleRepository()
_article_service = ArticleService(_s3_service, _gpt_service, _article_repo)


@router.get(
    "/{article_id}",
    response_model=ArticleResponseSchema,
    summary="Получить метаданные HTML-статьи",
    description="Возвращает метаданные статьи по ID (URL, тип, дата создания).",
)
async def get_html_article(
    article_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> ArticleResponseSchema:
    """Получить метаданные HTML-статьи по ID."""
    article = await _article_service.get_article(article_id=article_id, session=session)

    if not article:
        raise ArticleNotFoundError(article_id)

    return ArticleResponseSchema(
        id=article.id,
        public_url=article.public_url,
        article_type=article.article_type.value,
        format_type=article.format_type.value,
        created_at=article.created_at,
    )
