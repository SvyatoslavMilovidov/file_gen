"""
Enums — перечисления для всех моделей.

## Бизнес-контекст
Централизованное хранение всех статусов и типов,
используемых в моделях данных.
"""

from enum import Enum


class ArticleTypeEnum(str, Enum):
    """Тип статьи — определяет бизнес-контекст."""

    VACANCY = "vacancy"
    ASSESSMENT = "assessment"
    EMAIL = "email"
    TEST_RESULTS = "test_results"
    CUSTOM = "custom"


class ContentModeEnum(str, Enum):
    """Режим контента — определяет способ обработки."""

    FORMATTED = "formatted"  # Готовый HTML, без обработки GPT
    RAW = "raw"              # Сырой текст, требуется GPT-форматирование


class FormatTypeEnum(str, Enum):
    """Тип выходного формата — определяет группу эндпоинтов и S3-префикс."""

    HTML = "html"
    # Будущие форматы:
    # NOTION = "notion"
    # PDF = "pdf"
