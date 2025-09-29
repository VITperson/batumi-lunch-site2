# Batumi Lunch Web Platform

Полноценный веб-проект, который повторяет доменную логику Telegram-бота `bot.py` и расширяет её согласно `roadmap.md` и `ROADMAP_ORDER_PLANNER.md`.

## Стек

- Backend: FastAPI + SQLAlchemy (async) + Alembic, PostgreSQL, Redis (для будущих очередей/кэша)
- Frontend: Next.js 14 (App Router) + React Query + Zustand (заготовка)
- Инфраструктура: Docker Compose, Makefile, GitHub Actions (TODO), Alembic миграции

## Быстрый старт

```bash
# 1. Склонируйте репозиторий и перейдите в директорию проекта
cp .env.sample .env    # настройте DATABASE_URL, если локальный пользователь Postgres не "postgres"
make install           # установка зависимостей backend/frontend
make migrate           # применение миграций (использует deploy/alembic.ini)
make seed              # сидинг примерного меню
make serve-api         # запуск FastAPI на http://localhost:8000
make serve-web         # запуск Next.js на http://localhost:3000
```

Или через Docker:

```bash
cp .env.sample .env.local
make up
```

## Структура

```
backend/app          # FastAPI приложение, доменные сервисы и модели
backend/tests        # Pytest unit-тесты
frontend/            # Next.js приложение (planner skeleton)
deploy/              # Dockerfile-ы, docker-compose, alembic.ini
scripts/             # seed и заглушка миграции JSON → DB
docs/                # внутренние документы и отчеты
```

## Основные возможности

- **API**: `/api/v1/menu/week`, `/menu/weeks`, `/menu/presets`, `/orders/calc`, `/orders/checkout` (MVP), `/subscriptions`, `/auth/guest/*`, `/healthz`/`/readyz`.
- **Domain**: портированы ключевые бизнес-правила бота — дедлайны, sold-out, проверка недель. Доступны модели Users, Orders, MenuWeek, DayOffer, Preset, OrderTemplate, WeekSelection, Subscription, Payment* и Delivery*.
- **Frontend MVP**: лендинг и заглушка планировщика с React Query, каркас компонентов для сетки дней и сводки заказа.
- **Миграции**: Alembic `0001_initial` создаёт все таблицы/enum-ы.
- **Скрипты**: `seed_menu.py` — безопасный сидинг меню; `migrate_json_to_db.py` — TODO для миграции из JSON.

## Тесты и линтинг

```bash
make test   # PYTHONPATH=backend pytest
make lint   # python -m compileall + next lint
```

## Переменные окружения

См. `.env.sample`. Для локального запуска создайте `.env` или `.env.local` с переопределениями.

- `DATABASE_URL` по умолчанию использует peer-авторизацию (`postgresql+asyncpg:///batumi_lunch`). Если у вас настроен другой
  пользователь/пароль, пропишите их в `.env`.
- `REDIS_URL`, `SECRET_KEY`, `LOG_LEVEL` и другие параметры также можно переопределять через `.env`.

## TODO / Ограничения

- `orders/checkout` реализован для режима `single`; multiweek/subscription оставлены как TODO и помечены HTTP 501.
- SMS-провайдер, токенизация платежей, уведомления и аналитика требуют интеграции.
- Frontend содержит каркас; UI/UX из roadmap предстоит доработать (пресеты, гостевой вход, подписки).
- GitHub Actions workflow и полноценный CI находятся в бэклоге.
