"""
ArticleModel — ORM модель для хранения метаданных статей.

## Бизнес-контекст
Хранит информацию о сгенерированных статьях:
- Тип статьи (вакансия, оценка, письмо, тест)
- Режим генерации (готовый HTML или сырой текст через GPT)
- Путь к файлу в S3 и публичный URL
- Связь с исходной сущностью (вакансия, кандидат и т.д.)

Все данные хранятся в отдельной PostgreSQL-схеме 'article'.
"""

from sqlalchemy import Column, String, Integer, Enum as SQLEnum

from .base_model import Base, BaseModel
from .enums import ArticleTypeEnum, ContentModeEnum, FormatTypeEnum


class ArticleModel(BaseModel, Base):
    """Метаданные сгенерированной статьи."""

    __tablename__ = "articles"
    __table_args__ = {"schema": "article"}

    title = Column(String, nullable=False)
    article_type = Column(
        SQLEnum(
            ArticleTypeEnum,
            schema="article",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    content_mode = Column(
        SQLEnum(
            ContentModeEnum,
            schema="article",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    format_type = Column(
        SQLEnum(
            FormatTypeEnum,
            schema="article",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=FormatTypeEnum.HTML,
    )
    s3_key = Column(String, nullable=False, unique=True)
    public_url = Column(String, nullable=False)
    source_entity_id = Column(Integer, nullable=True, index=True)
    lang = Column(String(5), nullable=False, default="ru")
