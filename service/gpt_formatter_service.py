"""
GPTFormatterService — сервис для форматирования текста через OpenAI GPT.

## Бизнес-контекст
Принимает сырой текст и правила оформления,
отправляет в OpenAI API и возвращает оформленный HTML.
Используется в режиме content_mode='raw'.

## Обработка
1. Формирует системный промпт с правилами оформления
2. Отправляет текст как пользовательское сообщение
3. Получает HTML от GPT
4. Очищает от артефактов (markdown-блоки и т.д.)
"""

import re
import logging

from openai import AsyncOpenAI

from core.config import configs
from core.exceptions import GPTFormattingError

logger = logging.getLogger(__name__)

# Системный промпт по умолчанию (если formatting_rules не переданы)
DEFAULT_SYSTEM_PROMPT = """Ты — специалист по вёрстке HTML.
Преобразуй полученный текст в чистый, семантический HTML.

Правила:
- Используй теги: <h3>, <h4>, <p>, <ul>, <ol>, <li>, <strong>, <em>, <blockquote>, <hr>
- НЕ добавляй <!DOCTYPE>, <html>, <head>, <body> — только содержимое для <body>
- НЕ используй inline стили и атрибуты class
- Структурируй текст логически: заголовки, параграфы, списки
- Сохрани весь смысл и содержание исходного текста
- Верни ТОЛЬКО HTML без пояснений и markdown-блоков"""


class GPTFormatterService:
    """Сервис для форматирования текста через GPT."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=configs.OPENAI_API_KEY)

    async def format_text(
        self,
        raw_text: str,
        formatting_rules: str | None = None,
        lang: str = "ru",
    ) -> str:
        """
        Отформатировать сырой текст в HTML через GPT.

        ## Входные данные
        - raw_text: сырой текст для форматирования
        - formatting_rules: пользовательские правила оформления (опционально)
        - lang: язык текста (для контекста GPT)

        ## Выходные данные
        - Чистый HTML-контент (без doctype, head, body)

        ## Исключения
        - GPTFormattingError: при ошибке вызова OpenAI API
        """
        system_prompt = formatting_rules or DEFAULT_SYSTEM_PROMPT

        # Добавляем контекст языка
        if lang == "en":
            system_prompt += "\n\nОтвечай на английском языке."

        try:
            response = await self._client.chat.completions.create(
                model=configs.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text},
                ],
            )

            html_content = response.choices[0].message.content or ""
            html_content = self._clean_gpt_artifacts(html_content)

            if not html_content.strip():
                raise GPTFormattingError("GPT вернул пустой контент")

            logger.info(
                "Текст отформатирован через GPT (модель=%s, длина=%d -> %d)",
                configs.OPENAI_MODEL,
                len(raw_text),
                len(html_content),
            )
            return html_content

        except GPTFormattingError:
            raise
        except Exception as exc:
            logger.error("Ошибка форматирования через GPT: %s", exc)
            raise GPTFormattingError(f"Не удалось отформатировать текст: {exc}")

    @staticmethod
    def _clean_gpt_artifacts(html: str) -> str:
        """
        Очистить HTML от типичных артефактов GPT.

        ## Обработка
        - Удаляет markdown-блоки кода (```html ... ```)
        - Удаляет преамбулы GPT перед HTML
        - Убирает лишние пустые строки
        """
        # Убираем markdown блоки кода
        html = re.sub(r"```html\s*\n?", "", html, flags=re.IGNORECASE)
        html = re.sub(r"```\s*\n?", "", html)

        # Убираем преамбулы (текст до первого HTML-тега)
        lines = html.split("\n")
        clean_lines = []
        started = False

        for line in lines:
            stripped = line.strip()
            if not started:
                if not stripped:
                    continue
                if stripped.startswith("<") or started:
                    started = True
                    clean_lines.append(line)
                continue
            clean_lines.append(line)

        html = "\n".join(clean_lines)

        # Убираем множественные пустые строки
        html = re.sub(r"\n{3,}", "\n\n", html)

        return html.strip()
