"""
Configs — конфигурация приложения.

## Бизнес-контекст
Централизованное хранение всех настроек article_service.
Загружает значения из переменных окружения с fallback на значения по умолчанию.

## Входные данные
- Переменные окружения (DB_*, S3_*, OPENAI_*, ARTICLE_SERVICE_*)

## Обработка
- Загрузка через python-dotenv
- Приведение типов

## Выходные данные
- Singleton объект configs с типизированными настройками
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Configs:
    # Debug mode
    MODE_DEBUG: bool = os.getenv("MODE_DEBUG", "False") == "True"

    # Database
    DB_ENGINE: str = os.getenv("DB_ENGINE", "postgresql")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # S3 / MinIO
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://minio:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "hr-articles")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_PUBLIC_URL: str = os.getenv("S3_PUBLIC_URL", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Service
    ARTICLE_SERVICE_PORT: int = int(os.getenv("ARTICLE_SERVICE_PORT", "8020"))

    @property
    def database_url(self) -> str:
        """URL для асинхронного подключения к БД."""
        return (
            f"{self.DB_ENGINE}+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        """URL для синхронного подключения (Alembic)."""
        return (
            f"{self.DB_ENGINE}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


configs = Configs()
