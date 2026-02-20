"""
POST /api/v1/html/generate — генерация HTML-статьи.

## Бизнес-контекст
Принимает запрос на генерацию HTML-статьи в одном из двух режимов:
- formatted: готовый HTML оборачивается в шаблон и сохраняется в S3
- raw: сырой текст форматируется через GPT, оборачивается в шаблон, сохраняется в S3

## Входные данные
- HtmlGenerateSchema (JSON body)

## Выходные данные
- ArticleResponseSchema с public_url и метаданными
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.article.article_schema import HtmlGenerateSchema, ArticleResponseSchema
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


@router.post(
    "/generate",
    response_model=ArticleResponseSchema,
    summary="Сгенерировать HTML-статью",
    description="Создаёт HTML-статью, сохраняет в S3 и возвращает публичный URL.",
)
async def generate_html_article(
    data: HtmlGenerateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> ArticleResponseSchema:
    """
    Сгенерировать HTML-статью и сохранить в S3.

    ## Режимы
    - **formatted**: передайте готовый HTML в `html_content`
    - **raw**: передайте текст в `raw_text` и опционально `formatting_rules`
    """
    return await _article_service.generate_html(data=data, session=session)
