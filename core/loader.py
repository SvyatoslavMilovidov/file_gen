"""
Loader — инициализация FastAPI приложения.

## Бизнес-контекст
Создаёт и настраивает экземпляр FastAPI с метаданными,
инициализирует подключение к БД.

## Выходные данные
- app: экземпляр FastAPI
- db_connect: менеджер подключения к БД
"""

from fastapi import FastAPI

from .database import DatabaseConnection
from .config import configs

# Metadata
TITLE = "Article Service"
DESCRIPTION = "Сервис генерации HTML-статей с хранением в S3"
VERSION = "1.0.0"

# FastAPI app
app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    debug=configs.MODE_DEBUG,
)

# Database connection
db_connect = DatabaseConnection()
