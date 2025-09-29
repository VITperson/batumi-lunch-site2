# QA Checklist

## Smoke-тесты
- [ ] GET /api/v1/healthz и /readyz возвращают 200
- [ ] GET /api/v1/menu/week возвращает текущую неделю
- [ ] POST /api/v1/orders/calc с 1-2 днями возвращает сводку и total > 0
- [ ] POST /api/v1/orders/checkout (mode=single) создаёт заказ в БД
- [ ] Гостевой вход: /auth/guest/start → /auth/guest/confirm
- [ ] Frontend planner отображает сетку дней и summary

## Негативные сценарии
- [ ] orders/calc с неверным днём → 400
- [ ] orders/calc с недоступной неделей → has_menu=false
- [ ] orders/checkout при sold-out днях → 409
- [ ] guest/confirm с неверным кодом → 400

## Регрессия backend
- [ ] Alembic миграции выполняются на чистой БД
- [ ] seed_menu.py идемпотентен (повторный запуск не дублирует данные)

## Регрессия frontend
- [ ] Planner отправляет запрос к API и отрабатывает ошибки
- [ ] SummarySidebar показывает дефолтные значения и предупреждение о TODO
