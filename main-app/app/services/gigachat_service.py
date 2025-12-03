"""
Сервис для работы с GigaChat API
"""
import os
import logging
from typing import Dict, List, Optional

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


logger = logging.getLogger(__name__)


class GigaChatService:
    """Базовый сервис для работы с GigaChat API"""

    def __init__(
        self,
        credentials: Optional[str] = None,
        scope: Optional[str] = None,
        verify_ssl_certs: bool = False
    ):
        """
        Инициализация сервиса GigaChat

        Args:
            credentials: API ключ для GigaChat (если None, берется из переменной окружения GC_AUTH_KEY)
            scope: Scope для API (если None, берется из GC_SCOPE или используется GIGACHAT_API_CORP)
            verify_ssl_certs: Проверять ли SSL сертификаты
        """
        self.credentials = credentials or os.getenv('GC_AUTH_KEY')
        self.scope = scope or os.getenv('GC_SCOPE', 'GIGACHAT_API_CORP')
        self.verify_ssl_certs = verify_ssl_certs
        self._client = None

        if not self.credentials:
            raise ValueError("GigaChat credentials not provided. Set GC_AUTH_KEY environment variable.")

    def __enter__(self):
        """Вход в контекстный менеджер"""
        self._client = GigaChat(
            credentials=self.credentials,
            scope=self.scope,
            verify_ssl_certs=self.verify_ssl_certs
        )
        self._client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        if self._client:
            self._client.__exit__(exc_type, exc_val, exc_tb)
            self._client = None

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.95
    ) -> str:
        """
        Отправить сообщения в чат и получить ответ

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
                     Поддерживаемые роли: "system", "user", "assistant"
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов в ответе
            top_p: Top-p сэмплирование

        Returns:
            Ответ от GigaChat

        Raises:
            RuntimeError: Если клиент не инициализирован
            Exception: При ошибке API

        Example:
            >>> with GigaChatService() as giga:
            ...     response = giga.chat([
            ...         {"role": "system", "content": "Ты - помощник"},
            ...         {"role": "user", "content": "Привет!"}
            ...     ])
        """
        if not self._client:
            raise RuntimeError("GigaChat client not initialized. Use 'with' statement.")

        try:
            # Конвертируем словари в Messages объекты
            gigachat_messages = []
            for msg in messages:
                role_map = {
                    "user": MessagesRole.USER,
                    "system": MessagesRole.SYSTEM,
                    "assistant": MessagesRole.ASSISTANT
                }
                role = role_map.get(msg["role"], MessagesRole.USER)
                gigachat_messages.append(Messages(role=role, content=msg["content"]))

            # Создаем чат
            chat = Chat(
                messages=gigachat_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )

            # Отправляем запрос
            response = self._client.chat(chat)

            # Возвращаем ответ
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling GigaChat API: {e}")
            raise

    def simple_chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Простой чат с одним сообщением

        Args:
            prompt: Пользовательский запрос
            system_prompt: Системный промпт (опционально)

        Returns:
            Ответ от GigaChat

        Example:
            >>> with GigaChatService() as giga:
            ...     response = giga.simple_chat("Как дела?", system_prompt="Ты - дружелюбный помощник")
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat(messages)


def get_gigachat_service() -> GigaChatService:
    """
    Получить экземпляр сервиса GigaChat

    Returns:
        Экземпляр GigaChatService

    Example:
        >>> with get_gigachat_service() as giga:
        ...     response = giga.simple_chat("Привет!")
    """
    return GigaChatService()