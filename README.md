# Цифровой ассистент (Health Assist)
Цифровой ассистент для ЗберЗдоровья. Помогает пациентам лучше понимать и выполнять план лечения,
анализирует совместимость лекарств, помогает подготовиться к обследованиям и ничего не забыть.

## Структура проекта

```
health_assist/
├── api/                    # FastAPI сервис основного API
│   └── requirements.txt
├── bot/                    # Telegram бот
│   └── requirements.txt
├── sber_mock/             # Mock-сервис для имитации Sber API
│   └── requirements.txt
├── pgadmin_config/        # Конфигурация pgAdmin
│   ├── servers.json       # Настройки серверов БД
│   ├── pgpass            # Пароли для автоматического подключения
│   └── init.sh           # Скрипт инициализации
├── docker-compose.yml     # Конфигурация Docker Compose
├── Dockerfile            # Общий Dockerfile для Python контейнеров
├── .env                  # Переменные окружения
└── README.md

```

## Структура docker-compose

Проект состоит из 5 контейнеров, объединенных в сеть `health_assist_network`:

### 1. **api** (порт 8000)
- **Описание**: Основной FastAPI сервис для обработки запросов
- **Технологии**: FastAPI, SQLAlchemy, PostgreSQL
- **Рабочая директория**: `/app` (маппинг `./api`)
- **Зависимости**: pgsql

### 2. **bot** (порт 8001)
- **Описание**: Telegram бот для взаимодействия с пользователями
- **Технологии**: python-telegram-bot
- **Рабочая директория**: `/app` (маппинг `./bot`)
- **Зависимости**: pgsql, api

### 3. **sber_mock** (порт 8002)
- **Описание**: Mock-сервис для имитации Sber API
- **Технологии**: FastAPI
- **Рабочая директория**: `/app` (маппинг `./sber_mock`)
- **Зависимости**: отсутствуют

### 4. **pgsql** (порт 5432)
- **Описание**: База данных PostgreSQL
- **Образ**: postgres:15-alpine
- **База данных**: main_db
- **Пользователь**: root
- **Пароль**: password
- **Healthcheck**: проверка доступности БД каждые 10 секунд

### 5. **pgadmin** (порт 5050)
- **Описание**: Web-интерфейс для управления PostgreSQL
- **Образ**: dpage/pgadmin4:latest
- **Автологин**: admin@health-assist.com / admin
- **Автоматическое подключение**: к серверу pgsql

### Volumes
- `postgres_data` - данные PostgreSQL
- `pgadmin_data` - конфигурация pgAdmin

## Инструкция по развертыванию

### Предварительные требования
- Docker
- Docker Compose

### Шаги развертывания

1. **Клонируйте репозиторий и перейдите в директорию проекта**
   ```bash
   cd /path/to/health_assist
   ```

2. **Убедитесь, что файл `.env` содержит необходимые переменные**
   ```env
   APP_NAME=HEALTH_ASSIST
   APP_ENV=local
   APP_DEBUG=true

   DB_CONNECTION=pgsql
   DB_HOST=pgsql
   DB_PORT=5432
   DB_DATABASE=main_db
   DB_USERNAME=root
   DB_PASSWORD=password
   ```

3. **Соберите образы и запустите все контейнеры**
   ```bash
   docker compose up -d --build
   ```

4. **Проверьте статус контейнеров**
   ```bash
   docker compose ps --format "table {{.Name}}\t{{.Service}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
   ```

5. **Просмотр логов**
   ```bash
   # Все контейнеры
   docker compose logs -f

   # Конкретный контейнер
   docker compose logs -f api
   docker compose logs -f bot
   docker compose logs -f sber_mock
   ```

6. **Доступ к сервисам**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Bot: порт 8001
   - Sber Mock: http://localhost:8002
   - Sber Mock Docs: http://localhost:8002/docs
   - pgAdmin: http://localhost:5050

### Остановка и удаление контейнеров

```bash
# Остановить контейнеры
docker compose stop

# Остановить и удалить контейнеры
docker compose down

# Удалить контейнеры и volumes (ВНИМАНИЕ: удалит данные БД)
docker compose down -v
```

### Перезапуск контейнера

```bash
# Перезапустить конкретный контейнер
docker compose restart api

# Пересобрать и перезапустить
docker compose up -d --build api
```

## Работа с pgAdmin

### Автоматическое подключение
При первом входе в pgAdmin (http://localhost:5050) сервер PostgreSQL будет автоматически добавлен:
- **Логин**: admin@health-assist.com
- **Пароль**: admin

Сервер **"Health Assist PostgreSQL"** будет виден в левой панели и автоматически подключится к базе данных.

### Ручное добавление сервера в pgAdmin

Если по каким-то причинам сервер не добавился автоматически:

1. Откройте pgAdmin: http://localhost:5050
2. Войдите с credentials:
   - Email: `admin@health-assist.com`
   - Password: `admin`

3. Нажмите **"Add New Server"** или правой кнопкой мыши на **Servers → Register → Server**

4. **Вкладка General:**
   - Name: `Health Assist PostgreSQL`
   - Server group: `Servers`

5. **Вкладка Connection:**
   - Host name/address: `pgsql`
   - Port: `5432`
   - Maintenance database: `main_db`
   - Username: `root`
   - Password: `password`
   - Save password: ✓ (отметить галочку)

6. **Вкладка Advanced:**
   - DB restriction: `main_db` (опционально, для отображения только нужной БД)

7. Нажмите **Save**

После этого сервер будет доступен в левой панели pgAdmin под именем **"Health Assist PostgreSQL"**.


