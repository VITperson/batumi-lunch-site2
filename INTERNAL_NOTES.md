# Internal Notes

## Mapping: Telegram Bot → Web Pages & Endpoints

| Bot command / intent | Web page | Backend endpoint(s) | Notes |
| --- | --- | --- | --- |
| `/start`, `🔄 В начало` | `/` (landing) | `GET /menu/week`, `GET /menu/presets` | Показ актуальной недели, CTA на планировщик. |
| `Показать меню на неделю` | `/menu` | `GET /menu/week`, `GET /menu/weeks` | Требует поддержку фото и fallback при отсутствии меню. |
| `Заказать обед` (wizard: день → количество → адрес → подтверждение) | `/planner` (неделя) и `/checkout` | `POST /orders/calc`, `POST /orders/checkout`, `GET /addresses`, `POST /addresses`, `POST /auth/guest/*` | Планировщик недели объединяет выбор дня/порций; checkout обрабатывает адрес и оплату. |
| Дубликат заказа (`resolve_duplicate_order`) | `/planner` (диалог), `/account/orders/{id}` | `POST /orders/calc` (валидация), `PATCH /orders/{id}`, `POST /orders/{id}/cancel` | Нужно сравнить существующий заказ и новый, предложить увеличить или заменить. |
| `Мои заказы` (`list_active_orders`) | `/account/orders` | `GET /orders?mine=1`, `PATCH /orders/{id}`, `POST /orders/{id}/cancel` | Статусы и действия как в боте. |
| `/order <ID>` | `/orders/{id}` | `GET /orders/{id}` | Просмотр деталей заказа, проверка роли. |
| `/cancel <ID>` или inline отмена | `/orders/{id}` | `POST /orders/{id}/cancel` | Статусы `cancelled_by_user` или `cancelled` (админ). |
| Админ меню (`admin_manage_menu`) | `/admin/menu` | `PUT /admin/menu/week`, `PUT /admin/menu/{day}`, `POST /admin/menu/photo` | CRUD недель и блюд, загрузка фото. |
| Админ отчёты (`admin_report_*`) | `/admin/reports` | `GET /orders?week=...`, `GET /menu/week` | Дашборд по неделям/дням. |
| `/sms` рассылка | `/admin/broadcast` | `POST /admin/broadcasts` | Массовая рассылка по активным пользователям. |
| Профиль (`my_profile`) | `/account/profile` (часть ЛК) | `GET /addresses`, `GET /orders` | Отображение сохранённого адреса/телефона. |
| Контакты оператора (`contact_operator`) | `/support` (модалка/секция) | Статический контент | Отображаем телефон/Instagram. |

## Business Rules & Validation (из `bot.py`)

- **Меню и недели**
  - Меню хранится по неделям (`menu.json`): ключ `week` + карта `день → блюда`. Фото для каждого дня по фиксированным путям `DishPhotos/<Day>.png`.
  - Окно заказов задаётся `order_window.json`: поля `next_week_enabled` и `week_start` (ISO). Если окно закрыто, доступна только текущая неделя.
  - `_is_day_available_for_order(day)` проверяет:
    - День должен существовать в меню.
    - Если день уже прошёл для текущей недели, но следующая неделя открыта и `week_start` в будущем → разрешаем как заказ на следующую неделю.
    - Для текущего дня действует дедлайн `ORDER_CUTOFF_HOUR = 10` (по местному времени).
    - Возвращает флаги `is_next_week` и ISO даты для расчётов.

- **Лимиты и антиспам**
  - Доступные порции: фиксированный набор `1-4` (строки "1 обед" ... "4 обеда"); пользователь может вводить цифры `1-4`.
  - Антиспам: нельзя оформлять новый заказ чаще чем раз в 10 секунд (`last_order_ts`).

- **Профиль пользователя**
  - `users.json` хранит `address`, `phone`. При первом заказе профиль создаётся, далее данные автоподставляются.
  - Валидация адреса — текст свободной формы; бот просит адрес в одном сообщении с подсказками.
  - Телефон может быть пустым; при подтверждении отображается подсказка «можно добавить».

- **Заказы**
  - `orders.json` хранит `user_id`, `day`, `count`, `menu`, `address`, `phone`, `status`, `created_at`, `delivery_week_start`, `next_week`.
  - ID заказа формируется как `BLB-<ts36>-<uid36>-<rnd>`.
  - Создание заказа:
    - После выбора дня/порций выполняется проверка на дубликат через `find_user_order_same_day(uid, day, week_start)`.
    - Если дубликат найден, предлагаются действия: увеличить количество, перезаписать, отменить (см. `resolve_duplicate_order`).
    - При подтверждении сохраняется заказ со статусом `new`, рассчитывается стоимость = `count * PRICE_LARI (15)`.
    - Админу отправляется уведомление с деталями заказа.
  - Отмена: `set_order_status(order_id, new_status)` обновляет поле `status`. Бот использует статусы `cancelled_by_user`, `cancelled`.
  - Изменение количества: поток `update_order_count_choice` позволяет поменять `count` с проверкой лимитов.

- **Админ-потоки**
  - Управление меню: CRUD по дням/неделе, загрузка фото, переключение окна следующей недели.
  - Отчёты: агрегация заказов по дням недели и статусам.
  - Рассылки: `/sms <HTML>` отправляет сообщение всем пользователям (кроме админа) из объединённого множества `users.json` и `orders.json`.

- **Прочее**
  - Логи ведутся через `TimedRotatingFileHandler` и консоль.
  - Используется `PicklePersistence` для хранения FSM состояний (`bot_state.pickle`).
  - Контакты оператора (телефон, Instagram, username) берутся из `config_secret.py` с запасными значениями.

## UX соответствия из roadmap

- Планировщик недели должен поддерживать состояния дней: доступен, sold-out, закрыт по дедлайну. Надо расширить API `DayOffer` полями `status`, `portion_limit`, `allergy_tags`.
- Sticky summary: показывает выбранные дни, применённый пресет, промокод, итоговую стоимость.
- Гостевой чек-аут: телефон + SMS код → `/auth/guest/start` и `/auth/guest/confirm`.
- Многонедельный заказ: счётчик недель 1–8, повторение выбранных дней (`OrderTemplate`, `WeekSelection`).
- Подписки: сущности `Subscription`, `SubscriptionWeek`, `PaymentIntent`, `PaymentToken`; управление пропусками и паузами.
- Личный кабинет: вкладки «Заказы», «Адреса», «Подписки», кнопка повторного заказа.
- Админка: управление меню, пресетами, лимитами, зонами доставки, отчётами.

## Доменные TODO для Web

- Точное соответствие бизнес-правилу cutoff/next_week при расчёте корзины (`/orders/calc`).
- Реализация дедупликации в API (409 + рекомендации), сохранение черновика заказа.
- Валидация адресов/телефонов на стороне сервера (формат, зоны доставки).
- Реализация статусов заказов (`new`, `cancelled_by_user`, `cancelled`, будущие `confirmed`, `delivered`).
- Расширяемые лимиты порций/дней через таблицы конфигураций.

