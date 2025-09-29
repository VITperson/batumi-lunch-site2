.PHONY: install install-backend install-frontend migrate seed serve-api serve-web test lint up down format

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

ALEMBIC_INI_HOST := $(abspath deploy/alembic.ini)
ALEMBIC_INI_CONTAINER := deploy/alembic.ini

migrate:
       @if docker compose -f deploy/docker-compose.yml ps --services --filter "status=running" | grep -q "^api$$"; then \
               docker compose -f deploy/docker-compose.yml exec api alembic -c $(ALEMBIC_INI_CONTAINER) upgrade head; \
       else \
               alembic -c "$(ALEMBIC_INI_HOST)" upgrade head; \
       fi

seed:
	python scripts/seed_menu.py

serve-api:
	uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

serve-web:
	cd frontend && npm run dev

lint:
	cd backend && python -m compileall app
	cd frontend && npm run lint

format:
	cd frontend && npx prettier --write .

pytest = PYTHONPATH=backend pytest

test:
	$(pytest)

up:
	docker compose -f deploy/docker-compose.yml up --build

down:
	docker compose -f deploy/docker-compose.yml down
