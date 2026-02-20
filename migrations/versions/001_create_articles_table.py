"""Create article schema and articles table.

Revision ID: 001
Revises:
Create Date: 2026-02-13
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создаёт схему article и таблицу articles."""
    # Схема создаётся в env.py перед запуском миграций,
    # но на всякий случай дублируем
    op.execute("CREATE SCHEMA IF NOT EXISTS article")

    # Создаём enum-типы и таблицу
    # Enum-типы создаются автоматически через op.create_table()
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "article_type",
            sa.Enum(
                "vacancy", "assessment", "email", "test_results", "custom",
                name="articletypeenum",
                schema="article",
            ),
            nullable=False,
        ),
        sa.Column(
            "content_mode",
            sa.Enum(
                "formatted", "raw",
                name="contentmodeenum",
                schema="article",
            ),
            nullable=False,
        ),
        sa.Column(
            "format_type",
            sa.Enum(
                "html",
                name="formattypeenum",
                schema="article",
            ),
            nullable=False,
            server_default="html",
        ),
        sa.Column("s3_key", sa.String(), nullable=False, unique=True),
        sa.Column("public_url", sa.String(), nullable=False),
        sa.Column("source_entity_id", sa.Integer(), nullable=True, index=True),
        sa.Column("lang", sa.String(5), nullable=False, server_default="ru"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            onupdate=sa.func.now(),
        ),
        schema="article",
    )


def downgrade() -> None:
    """Удаляет таблицу и схему."""
    op.drop_table("articles", schema="article")

    # Удаляем enum-типы
    sa.Enum(name="formattypeenum", schema="article").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(name="contentmodeenum", schema="article").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(name="articletypeenum", schema="article").drop(
        op.get_bind(), checkfirst=True
    )

    op.execute("DROP SCHEMA IF EXISTS article CASCADE")
