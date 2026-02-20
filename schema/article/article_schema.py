"""
ArticleSchema — Pydantic схемы для API генерации статей.

## Бизнес-контекст
Валидация входных данных при генерации HTML-статей
и формирование ответов API.

## Режимы генерации
- formatted: принимает готовый HTML-контент
- raw: принимает сырой текст + правила оформления для GPT
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from model.enums import ArticleTypeEnum, ContentModeEnum


class HtmlGenerateSchema(BaseModel):
    """
    Схема запроса на генерацию HTML-статьи.

    ## Входные данные
    - article_type: тип статьи (vacancy, assessment, email, test_results, custom)
    - content_mode: режим (formatted — готовый HTML, raw — сырой текст для GPT)
    - html_content: готовый HTML (обязателен при content_mode=formatted)
    - raw_text: сырой текст (обязателен при content_mode=raw)
    - formatting_rules: правила оформления для GPT (опционально, для raw)
    - title: заголовок статьи
    - lang: язык (ru/en)
    - source_entity_id: ID связанной сущности (вакансия, кандидат и т.д.)
    """

    article_type: ArticleTypeEnum
    content_mode: ContentModeEnum

    # Для formatted
    html_content: Optional[str] = None

    # Для raw
    raw_text: Optional[str] = None
    formatting_rules: Optional[str] = None

    # Общие поля
    title: str
    lang: str = "ru"
    source_entity_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_content_fields(self) -> "HtmlGenerateSchema":
        """Проверяет наличие нужных полей в зависимости от content_mode."""
        if self.content_mode == ContentModeEnum.FORMATTED:
            if not self.html_content:
                raise ValueError(
                    "html_content обязателен при content_mode='formatted'"
                )
        elif self.content_mode == ContentModeEnum.RAW:
            if not self.raw_text:
                raise ValueError(
                    "raw_text обязателен при content_mode='raw'"
                )
        return self


class ArticleResponseSchema(BaseModel):
    """
    Схема ответа с метаданными сгенерированной статьи.

    ## Выходные данные
    - id: идентификатор статьи в БД
    - public_url: публичная ссылка на HTML в S3
    - article_type: тип статьи
    - format_type: формат (html)
    - created_at: дата создания
    """

    id: int
    public_url: str
    article_type: str
    format_type: str
    created_at: datetime

    class Config:
        from_attributes = True
