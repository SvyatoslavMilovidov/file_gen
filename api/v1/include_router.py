"""
Include Router — подключение всех роутеров API v1.

## Бизнес-контекст
Централизованное подключение всех ресурсных роутеров
к основному приложению FastAPI.

## Группировка по формату
Эндпоинты группируются по типу выходного формата:
- /api/v1/html/ — HTML-статьи
- (будущее) /api/v1/notion/ — Notion-страницы
- (будущее) /api/v1/pdf/ — PDF-документы
"""

from core import app
from .endpoints import health_router, html_router
from .exception_handlers import register_exception_handlers

# Health check — без версии в пути (стандарт для k8s/docker)
app.include_router(health_router)

# API v1 endpoints
API_V1_PREFIX = "/api/v1"

app.include_router(html_router, prefix=f"{API_V1_PREFIX}/html", tags=["HTML Articles"])

# Будущие форматы:
# app.include_router(notion_router, prefix=f"{API_V1_PREFIX}/notion", tags=["Notion Pages"])

# Exception handlers
register_exception_handlers(app)
