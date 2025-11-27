#!/bin/sh

# Установить токен, если он еще не установлен
CURRENT_TOKEN=$(/clo get token 2>/dev/null || echo "")

if [ -z "$CURRENT_TOKEN" ] || [ "$CURRENT_TOKEN" = "null" ]; then
    if [ -n "$KEY" ]; then
        echo "Устанавливаю токен авторизации..."
        /clo set token "$KEY"
    else
        echo "Ошибка: переменная KEY не установлена!"
        exit 1
    fi
else
    echo "Токен уже установлен"
fi

# Запустить публикацию
echo "Запускаю публикацию..."
exec /clo "$@"