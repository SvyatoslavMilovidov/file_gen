"""
ArticleRepository — репозиторий для работы с метаданными статей.

## Бизнес-контекст
CRUD операции над таблицей article.articles.
Расширяет базовый репозиторий методами поиска
по связанной сущности (вакансия, кандидат и т.д.).
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.base_repository import BaseRepository
from model.article_model import ArticleModel


class ArticleRepository(BaseRepository[ArticleModel]):
    """Репозиторий для ArticleModel."""

    def __init__(self):
        super().__init__(ArticleModel)

    async def get_by_source_entity(
        self,
        source_entity_id: int,
        session: AsyncSession,
        format_type: Optional[str] = None,
    ) -> List[ArticleModel]:
        """
        Получить статьи по ID исходной сущности.

        ## Входные данные
        - source_entity_id: ID связанной сущности (вакансия, кандидат и т.д.)
        - session: сессия БД
        - format_type: фильтр по формату (html, notion и т.д.), опционально

        ## Выходные данные
        - Список ArticleModel, отсортированный по дате создания (новые первые)
        """
        query = select(self.model).where(
            self.model.source_entity_id == source_entity_id
        )
        if format_type:
            query = query.where(self.model.format_type == format_type)

        query = query.order_by(self.model.created_at.desc())
        result = await session.execute(query)
        return list(result.scalars().all())
