"""
Main — точка входа приложения.

## Бизнес-контекст
Запускает FastAPI сервер article_service с настроенным приложением.
При старте инициализирует S3-бакет для хранения статей.
"""

from api import app
from core.config import configs
from service.s3_storage_service import S3StorageService
import uvicorn


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте: создание S3-бакета."""
    s3_service = S3StorageService()
    await s3_service.ensure_bucket()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=configs.ARTICLE_SERVICE_PORT)
