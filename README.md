# Склад с pub/sub

Тестовое задание: два асинхронных сервиса для складских операций.

## Структура

```bash
test_services/
├── docker-compose.yml      # Docker Compose конфигурация
├── pyproject.toml          # Зависимости и метаданные проекта
├── README.md               # Документация
├── Dockerfile.api          # Docker образ для API
├── Dockerfile.worker       # Docker образ для Worker
├── Dockerfile.migrations   # Docker образ для миграций 
│
├── inventory_api/          # API сервис
│   ├── __init__.py
│   ├── app.py              # Точка входа
│   ├── handlers.py         # HTTP-обработчики
│   ├── redis_pub           # Redis
│   ├── repositories/       # Репозитории
│   └── services/           # Бизнес-логика и репозитории
│
├── analytics_worker/       # Worker сервис
│   ├── __init__.py
│   ├── worker.py           # Точка входа
│   ├── redis_pub           # Redis
│   ├── repositories/       # Репозитории
│   └── services/           # Бизнес-логика
│
├── migrations/             # Миграции Alembic
│   ├── __init__.py
│   └── versions/
│       └── 2d6a3c518e6a_initial.py
│
├── tests/                  # Интеграционные тесты
│   ├── __init__.py
│   └── test_integration.py
│
└── shared/                 # Общие модули 
    ├── __init__.py
    ├── config.py           # Конфигурация (Pydantic)
    ├── database.py         # Подключение к БД и движок
    ├── models.py           # Общие модели SQLAlchemy
    ├── schemas.py          # Общие Pydantic схемы
    └── logger.py           # Настройка логирования

```

### 🏗️ Архитектура

- **inventory_api** — REST API для приёма операций и получения остатков
- **analytics_worker** — фоновый воркер для агрегации данных
- **PostgreSQL** — основное хранилище
- **Redis** — брокер сообщений (pub/sub)

### 🚀 Возможности

- 📦 Приём операций прихода/расхода
- 📊 Актуальные остатки по складам
- 📈 Агрегированная статистика (группировка по складам, топ-sku)
- ⚡ Асинхронная обработка всех операций
- 🔄 Обновление агрегатов в реальном времени через pub/sub

**Поток данных:**
1. Клиент → `POST /receipts` или `/issues`
2. API записывает операцию в `stock_events`
3. API публикует событие в Redis
4. Worker получает событие
5. Worker обновляет `stock_agg`
6. Клиент → `GET /stock` или `/stock/summary`

---

## 🛠️ Технологии

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Язык | Python | 3.10+ |
| Веб-фреймворк | aiohttp | 3.8+ |
| Работа с БД | SQLAlchemy Core | 1.4+ |
| Драйвер БД | asyncpg | 0.27+ |
| Брокер сообщений | Redis + aioredis | 7.x + 2.0+ |
| Контейнеризация | Docker + Docker Compose | 20.10+ |
| Тестирование | pytest + pytest-asyncio | 7.0+ + 0.20+ |

---

## 📦 Требования

- **Docker** и **Docker Compose** (рекомендуемый способ)
- Или **Python 3.10+** и **PostgreSQL 14+** и **Redis 7+** (для локального запуска)

---

## 🚀 Быстрый старт

### Способ 1: Docker Compose (рекомендуемый)

```bash
# 1. Клонируем репозиторий
git clone <repository-url>
cd project

# 2. Запускаем все сервисы
docker-compose up --build

# 3. Для фонового запуска
docker-compose up -d

# 4. Проверяем, что всё работает
curl http://localhost:8080/stock?warehouse=MAIN
```

### После запуска будут доступны:

- API: http://localhost:8080
- PostgreSQL: localhost:5432 (логин: postgres, пароль: postgres, БД: inventory)
- Redis: localhost:6379

### Способ 2: Локальный запуск
```bash
# 1. Устанавливаем зависимости из pyproject.toml
pip install -e .

# 2. Настраиваем переменные окружения
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/inventory
export REDIS_URL=redis://localhost:6379

# 3. Запускаем API (в первом терминале)
python -m inventory_api.app

# 4. Запускаем Worker (во втором терминале)
python -m analytics_worker.worker
```

### Способ 3: Установка из wheel
```bash
# 1. Установить пакет
pip install dist/inventory_services-1.0.0-py3-none-any.whl

# 2. Запустить API
inventory-api

# 3. Запустить Worker (в другом терминале)
analytics-worker
```

### API запросы
```bash
# Приход товара
curl -X POST http://localhost:8080/receipts \
  -H "Content-Type: application/json" \
  -d '{"sku":"A-100","qty":50,"warehouse":"WH-1"}'

# Расход товара
curl -X POST http://localhost:8080/issues \
  -H "Content-Type: application/json" \
  -d '{"sku":"A-100","qty":20,"warehouse":"WH-1"}'

# Остатки
curl "http://localhost:8080/stock?warehouse=WH-1&sku=A-100"

# Сводка
curl "http://localhost:8080/stock/summary?top_n=5"
```

## 🧪 Тестирование

```bash
# Установить зависимости для тестов (если не установлены)
pip install -e .[test]

# Запустить интеграционные тесты с отчётом о покрытии
pytest tests/test_integration.py -v --cov=./
```
### 🗄️ Миграции

Автоматическое создание таблиц
При запуске через Docker или локально таблицы создаются автоматически при первом запуске API.

```bash
# Установить Alembic
pip install alembic

# Создать новую миграцию
alembic revision --autogenerate -m "create tables"

# Применить миграции
alembic upgrade head

# Откатить миграции
alembic downgrade -1

# Просмотр истории
alembic history
```
