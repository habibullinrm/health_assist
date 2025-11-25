# API Structure Documentation

## Структура проекта

```
api/
├── alembic/                      # Миграции БД
│   ├── versions/                 # История миграций
│   ├── env.py                   # Конфигурация Alembic
│   └── script.py.mako           # Шаблон миграций
│
├── app/                         # Основное приложение
│   ├── models/                  # SQLAlchemy модели (ORM)
│   │   ├── __init__.py
│   │   ├── base.py             # Base класс
│   │   └── user.py             # Модели User, Role (пример)
│   │
│   ├── schemas/                 # Pydantic схемы (API)
│   │   ├── __init__.py
│   │   └── user.py             # Схемы для User
│   │
│   ├── api/                     # API endpoints
│   │   ├── deps.py             # Зависимости (get_db)
│   │   └── v1/                 # API v1
│   │       ├── __init__.py
│   │       └── users.py        # Endpoints для users
│   │
│   ├── crud/                    # CRUD операции
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый CRUD класс
│   │   └── user.py             # CRUD для User
│   │
│   ├── services/                # Бизнес-логика
│   │   └── __init__.py
│   │
│   ├── core/                    # Конфигурация
│   │   ├── __init__.py
│   │   ├── config.py           # Настройки из .env
│   │   └── database.py         # Database connection
│   │
│   └── main.py                  # Точка входа FastAPI
│
├── tests/                       # Тесты
│   └── __init__.py
│
├── main.py                      # Старый main.py (можно удалить)
├── requirements.txt
├── alembic.ini
└── .env
```

## Описание модулей

### 1. app/models/ - SQLAlchemy модели

Описывают структуру таблиц БД.

**Пример:**
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    full_name = Column(String)
```

**Важно:**
- Все модели импортируются в `app/models/__init__.py` для Alembic autogenerate
- Наследуются от `Base` из `app/models/base.py`

### 2. app/schemas/ - Pydantic схемы

Валидация и сериализация данных для API.

**Пример:**
```python
# app/schemas/user.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    full_name: str

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str

    model_config = {"from_attributes": True}
```

**Типы схем:**
- `*Create` - для создания объекта (POST)
- `*Update` - для обновления (PATCH/PUT)
- `*Read` - для ответа API (GET)
- `*Base` - базовые поля

### 3. app/crud/ - CRUD операции

Работа с БД (Create, Read, Update, Delete).

**Пример:**
```python
# app/crud/user.py
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

user = CRUDUser(User)
```

### 4. app/api/v1/ - API endpoints

FastAPI роуты для обработки HTTP запросов.

**Пример:**
```python
# app/api/v1/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.api.deps import get_db

router = APIRouter()

@router.get("/users", response_model=List[schemas.UserRead])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await crud.user.get_multi(db)
```

### 5. app/core/ - Конфигурация

#### config.py
Настройки из `.env` файла:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    # ...

    class Config:
        env_file = ".env"

settings = Settings()
```

#### database.py
Подключение к БД:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with async_session_maker() as session:
        yield session
```

### 6. app/services/ - Бизнес-логика

Сложная логика, которая не относится к CRUD.

**Примеры:**
- Интеграция с GigaChat
- Отправка уведомлений
- Сложные вычисления
- Интеграция с внешними API

## Работа с миграциями Alembic

### Создание миграции

После изменения моделей в `app/models/`:

```bash
# Внутри контейнера
alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Применить конкретную миграцию
alembic upgrade <revision_id>

# Откатить последнюю миграцию
alembic downgrade -1
```

### История миграций

```bash
# Посмотреть текущую версию
alembic current

# Посмотреть историю
alembic history
```

## Как добавить новую сущность

Пример: добавить модель Plan

### 1. Создать модель

```python
# app/models/plan.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
```

### 2. Импортировать в models/__init__.py

```python
# app/models/__init__.py
from app.models.plan import Plan

__all__ = ["Base", "User", "Plan"]
```

### 3. Создать Pydantic схемы

```python
# app/schemas/plan.py
class PlanCreate(BaseModel):
    title: str
    user_id: int

class PlanRead(PlanCreate):
    id: int
```

### 4. Создать CRUD

```python
# app/crud/plan.py
from app.crud.base import CRUDBase
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate

plan = CRUDBase(Plan, PlanCreate, PlanUpdate)
```

### 5. Создать API endpoints

```python
# app/api/v1/plans.py
router = APIRouter()

@router.get("/plans", response_model=List[schemas.PlanRead])
async def get_plans(db: AsyncSession = Depends(get_db)):
    return await crud.plan.get_multi(db)
```

### 6. Подключить роутер в main.py

```python
# app/main.py
from app.api.v1 import plans

app.include_router(plans.router, prefix="/api/v1", tags=["plans"])
```

### 7. Создать миграцию

```bash
alembic revision --autogenerate -m "add plans table"
alembic upgrade head
```

## Запуск приложения

### Через Docker

```bash
docker compose up -d --build api
```

### Локально (для разработки)

```bash
cd api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Тестирование API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Best Practices

1. **Async везде** - используйте async/await для всех DB операций
2. **Dependency Injection** - используйте `Depends()` для зависимостей
3. **Типизация** - всегда указывайте типы (mypy, pylance)
4. **Валидация** - используйте Pydantic для валидации входных данных
5. **Транзакции** - один endpoint = одна транзакция (get_db делает commit/rollback)
6. **Индексы** - добавляйте индексы по необходимости через миграции
7. **Тесты** - пишите тесты для критичной логики

## Полезные команды

```bash
# Проверка типов
mypy app/

# Форматирование кода
black app/
isort app/

# Линтер
ruff check app/

# Запуск тестов
pytest tests/
```