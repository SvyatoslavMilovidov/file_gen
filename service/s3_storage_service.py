"""
S3StorageService — сервис для работы с S3/MinIO хранилищем.

## Бизнес-контекст
Управляет загрузкой, удалением и формированием ссылок на файлы
в S3-совместимом хранилище (MinIO).

## Структура бакета
hr-articles/
├── html/vacancy/{uuid}.html
├── html/assessment/{uuid}.html
├── html/email/{uuid}.html
├── html/test_results/{uuid}.html
└── (будущие форматы: notion/, pdf/ и т.д.)

## Ключевые правила
- Файлы загружаются с правильным Content-Type
- Публичный URL формируется через S3_PUBLIC_URL из конфига
- Бакет создаётся автоматически при старте, если не существует
"""

import logging
from typing import Optional

from aiobotocore.session import get_session

from core.config import configs
from core.exceptions import S3UploadError

logger = logging.getLogger(__name__)


class S3StorageService:
    """Сервис для работы с S3/MinIO."""

    def __init__(self):
        self._session = get_session()

    def _get_client_kwargs(self) -> dict:
        """Параметры подключения к S3."""
        return {
            "service_name": "s3",
            "endpoint_url": configs.S3_ENDPOINT,
            "aws_access_key_id": configs.S3_ACCESS_KEY,
            "aws_secret_access_key": configs.S3_SECRET_KEY,
            "region_name": configs.S3_REGION,
        }

    async def ensure_bucket(self) -> None:
        """
        Создать бакет, если он не существует.

        ## Обработка
        Вызывается при старте сервиса.
        Создаёт бакет с именем из S3_BUCKET_NAME и устанавливает
        публичную политику чтения для доступа к статьям по URL.
        """
        async with self._session.create_client(**self._get_client_kwargs()) as client:
            try:
                await client.head_bucket(Bucket=configs.S3_BUCKET_NAME)
                logger.info("Бакет '%s' уже существует", configs.S3_BUCKET_NAME)
            except client.exceptions.ClientError:
                await client.create_bucket(Bucket=configs.S3_BUCKET_NAME)
                logger.info("Бакет '%s' создан", configs.S3_BUCKET_NAME)

                # Устанавливаем публичную политику чтения
                import json

                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [
                                f"arn:aws:s3:::{configs.S3_BUCKET_NAME}/*"
                            ],
                        }
                    ],
                }
                await client.put_bucket_policy(
                    Bucket=configs.S3_BUCKET_NAME,
                    Policy=json.dumps(policy),
                )
                logger.info(
                    "Публичная политика установлена для '%s'",
                    configs.S3_BUCKET_NAME,
                )

    async def upload_file(
        self,
        s3_key: str,
        content: bytes,
        content_type: str = "text/html; charset=utf-8",
    ) -> str:
        """
        Загрузить файл в S3.

        ## Входные данные
        - s3_key: путь в бакете (например, html/vacancy/abc123.html)
        - content: содержимое файла в байтах
        - content_type: MIME-тип файла

        ## Выходные данные
        - Публичный URL загруженного файла

        ## Исключения
        - S3UploadError: при ошибке загрузки
        """
        try:
            async with self._session.create_client(
                **self._get_client_kwargs()
            ) as client:
                await client.put_object(
                    Bucket=configs.S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=content,
                    ContentType=content_type,
                )

            public_url = self.get_public_url(s3_key)
            logger.info("Файл загружен в S3: %s -> %s", s3_key, public_url)
            return public_url

        except Exception as exc:
            logger.error("Ошибка загрузки в S3 (key=%s): %s", s3_key, exc)
            raise S3UploadError(f"Не удалось загрузить файл '{s3_key}': {exc}")

    async def delete_file(self, s3_key: str) -> bool:
        """
        Удалить файл из S3.

        ## Входные данные
        - s3_key: путь в бакете

        ## Выходные данные
        - True если удалено успешно, False при ошибке
        """
        try:
            async with self._session.create_client(
                **self._get_client_kwargs()
            ) as client:
                await client.delete_object(
                    Bucket=configs.S3_BUCKET_NAME,
                    Key=s3_key,
                )
            logger.info("Файл удалён из S3: %s", s3_key)
            return True
        except Exception as exc:
            logger.warning("Ошибка удаления из S3 (key=%s): %s", s3_key, exc)
            return False

    def get_public_url(self, s3_key: str) -> str:
        """
        Сформировать публичный URL для файла в S3.

        ## Входные данные
        - s3_key: путь в бакете

        ## Выходные данные
        - Полный публичный URL

        ## Обработка
        Если S3_PUBLIC_URL задан — используется он.
        Иначе — формируется из S3_ENDPOINT + bucket + key.
        """
        if configs.S3_PUBLIC_URL:
            base = configs.S3_PUBLIC_URL.rstrip("/")
            return f"{base}/{s3_key}"

        endpoint = configs.S3_ENDPOINT.rstrip("/")
        return f"{endpoint}/{configs.S3_BUCKET_NAME}/{s3_key}"
