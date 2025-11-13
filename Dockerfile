FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Обновление pip
RUN pip install --no-cache-dir --upgrade pip

# Создание рабочей директории
WORKDIR /app

# По умолчанию используем bash
CMD ["/bin/bash"]