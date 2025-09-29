# Summary of Implementation

## Backend
- FastAPI приложение (`backend/app/main.py`) с роутерами `/menu`, `/orders`, `/auth/guest`, `/subscriptions`, `/healthz`.
- Доменный калькулятор заказов (`app/domain/orders/calculator.py`) переносит правила из `bot.py`: лимит 1-4 порций, дедлайн 10:00, статусы sold_out/closed.
- Полная SQLAlchemy модель: Users, Orders, MenuWeek, DayOffer, Preset, OrderTemplate, WeekSelection, Subscription, PaymentIntent/Token, DeliveryZone/Slot, Address, AllergyTag.
- Alembic миграция `0001_initial` создаёт все таблицы и enum-типы.
- Скрипты: `seed_menu.py` (идемпотентный сидинг текущей недели), `migrate_json_to_db.py` (заготовка).
- Unit-тесты покрывают калькулятор заказов.

## Frontend
- Next.js App Router, Tailwind и React Query настроены через `Providers`.
- Маршруты:
  - `/` (из `(site)/page.tsx`) — лендинг с CTA.
  - `/planner` — skeleton планировщика: грид дней, сводка, загрузка меню через API.
- API-клиент `fetchMenuWeek` обращается к `/api/v1/menu/week`.
- Компоненты `PlannerGrid` и `SummarySidebar` задают структуру будущего UI.

## Инфраструктура
- Makefile с целями `install`, `migrate`, `seed`, `serve-api`, `serve-web`, `test`, `lint`, `up`, `down`.
- Docker Compose с сервисами `db`, `redis`, `api`, `web` и Dockerfile для API/WEB.
- `.env.sample` с ключевыми переменными.

## Ограничения и TODO
- Checkout поддерживает только режим `single`, остальные возвращают HTTP 501.
- GuestAuthService хранит коды в памяти и возвращает debug_code (требуется SMS-интеграция и persistence).
- Frontend отображает skeleton без интерактивности (нет хранения состояния корзины, пресетов, SMS-flow, подписок).
- CI/CD pipeline и e2e тесты не реализованы.
