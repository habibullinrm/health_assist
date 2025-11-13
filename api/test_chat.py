#!/usr/bin/env python3
"""
Консольный чат с GigaChat
Тестовый скрипт для проверки работы с GigaChat API
"""
import os
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# Загружаем переменные окружения
load_dotenv()

# Получаем креды из переменных окружения
GC_AUTH_KEY = os.getenv('GC_AUTH_KEY')
GC_SCOPE = os.getenv('GC_SCOPE', 'GIGACHAT_API_CORP')


def main():
    """Основная функция консольного чата"""

    if not GC_AUTH_KEY:
        print("❌ Ошибка: GC_AUTH_KEY не найден в переменных окружения!")
        return

    print("🤖 Консольный чат с GigaChat")
    print("=" * 50)
    print("Команды:")
    print("  - 'exit' или 'quit' - выход из чата")
    print("  - 'clear' - очистить историю")
    print("=" * 50)
    print()

    # Инициализация клиента GigaChat
    try:
        with GigaChat(
            credentials=GC_AUTH_KEY,
            scope=GC_SCOPE,
            verify_ssl_certs=False
        ) as giga:
            print("✅ Подключено к GigaChat")
            print()

            # История сообщений
            messages = []

            while True:
                # Получаем ввод от пользователя
                user_input = input("Вы: ").strip()

                if not user_input:
                    continue

                # Команды
                if user_input.lower() in ['exit', 'quit', 'выход']:
                    print("\n👋 До свидания!")
                    break

                if user_input.lower() == 'clear':
                    messages = []
                    print("\n🧹 История очищена\n")
                    continue

                # Добавляем сообщение пользователя в историю
                messages = [
                    Messages(role=MessagesRole.USER, content=user_input),
                ]

                try:
                    # Отправляем запрос к GigaChat
                    response = giga.chat(Chat(messages=messages))

                    # Получаем ответ
                    assistant_message = response.choices[0].message.content

                    # Добавляем ответ ассистента в историю
                    messages.append(Messages(
                        role=MessagesRole.ASSISTANT,
                        content=assistant_message
                    ))

                    # Выводим ответ
                    print(f"\n🤖 GigaChat: {assistant_message}\n")

                except Exception as e:
                    print(f"\n❌ Ошибка при обращении к API: {e}\n")

    except Exception as e:
        print(f"❌ Ошибка инициализации GigaChat: {e}")


if __name__ == "__main__":
    main()