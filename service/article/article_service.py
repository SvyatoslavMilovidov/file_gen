"""
ArticleService — основной сервис генерации статей.

## Бизнес-контекст
Центральная точка генерации HTML-статей. Поддерживает два режима:
1. formatted — принимает готовый HTML, оборачивает в шаблон, сохраняет в S3
2. raw — принимает сырой текст, форматирует через GPT, оборачивает в шаблон, сохраняет в S3

## Поток данных
1. Валидация входных данных (на уровне Pydantic-схемы)
2. Получение/генерация HTML-контента
3. Оборачивание в базовый HTML-шаблон (Jinja2)
4. Сохранение в S3 (html/{article_type}/{uuid}.html)
5. Запись метаданных в БД (schema: article)
6. Возврат public_url

## Ключевые правила
- Временные файлы не создаются — контент передаётся в S3 как bytes напрямую
- S3-ключ формируется как: {format_type}/{article_type}/{uuid}.html
"""

import uuid
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from model.enums import ContentModeEnum, FormatTypeEnum
from model.article_model import ArticleModel
from repository.article_repository import ArticleRepository
from schema.article.article_schema import HtmlGenerateSchema, ArticleResponseSchema
from service.s3_storage_service import S3StorageService
from service.gpt_formatter_service import GPTFormatterService

logger = logging.getLogger(__name__)

# Jinja2 шаблоны
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)


class ArticleService:
    """Основной сервис генерации статей."""

    def __init__(
        self,
        s3_service: S3StorageService,
        gpt_service: GPTFormatterService,
        article_repo: ArticleRepository,
    ):
        self._s3 = s3_service
        self._gpt = gpt_service
        self._repo = article_repo

    async def generate_html(
        self,
        data: HtmlGenerateSchema,
        session: AsyncSession,
    ) -> ArticleResponseSchema:
        """
        Сгенерировать HTML-статью и сохранить в S3.

        ## Входные данные
        - data: валидированная схема запроса
        - session: сессия БД

        ## Обработка
        1. Определить HTML-контент (готовый или через GPT)
        2. Обернуть в базовый шаблон
        3. Загрузить в S3
        4. Сохранить метаданные в БД

        ## Выходные данные
        - ArticleResponseSchema с public_url и метаданными
        """
        # 1. Получить HTML-контент
        if data.content_mode == ContentModeEnum.FORMATTED:
            html_body = data.html_content
        else:
            html_body = await self._gpt.format_text(
                raw_text=data.raw_text,
                formatting_rules=data.formatting_rules,
                lang=data.lang,
            )

        # 2. Обернуть в базовый шаблон
        full_html = self._wrap_in_template(
            title=data.title,
            body_content=html_body,
            lang=data.lang,
        )

        # 3. Сформировать S3 key и загрузить
        file_id = uuid.uuid4().hex
        s3_key = f"html/{data.article_type.value}/{file_id}.html"

        html_bytes = full_html.encode("utf-8")
        public_url = await self._s3.upload_file(
            s3_key=s3_key,
            content=html_bytes,
            content_type="text/html; charset=utf-8",
        )

        # 4. Сохранить метаданные в БД
        article = await self._repo.create(
            session=session,
            title=data.title,
            article_type=data.article_type,
            content_mode=data.content_mode,
            format_type=FormatTypeEnum.HTML,
            s3_key=s3_key,
            public_url=public_url,
            source_entity_id=data.source_entity_id,
            lang=data.lang,
        )

        logger.info(
            "HTML-статья создана: id=%s, type=%s, url=%s",
            article.id,
            data.article_type.value,
            public_url,
        )

        return ArticleResponseSchema(
            id=article.id,
            public_url=article.public_url,
            article_type=article.article_type.value,
            format_type=article.format_type.value,
            created_at=article.created_at,
        )

    async def get_article(
        self,
        article_id: int,
        session: AsyncSession,
    ) -> ArticleModel | None:
        """
        Получить метаданные статьи по ID.

        ## Входные данные
        - article_id: ID статьи
        - session: сессия БД

        ## Выходные данные
        - ArticleModel или None если не найдена
        """
        return await self._repo.get_by_id(article_id, session)

    @staticmethod
    def _wrap_in_template(
        title: str,
        body_content: str,
        lang: str = "ru",
    ) -> str:
        """
        Обернуть HTML-контент в базовый шаблон.

        ## Входные данные
        - title: заголовок страницы (<title>)
        - body_content: HTML-контент для <body>
        - lang: язык документа

        ## Выходные данные
        - Полный HTML-документ (doctype, head, body, CSS)
        """
        template = jinja_env.get_template("base.html")
        return template.render(
            title=title,
            body_content=body_content,
            lang=lang,
        )
