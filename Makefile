.PHONY: up down build logs migrate seed test test-backend e2e backup fmt

up:            ## Start the full stack
	docker compose up -d --build

down:          ## Stop the stack
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f api web

migrate:       ## Apply DB migrations
	docker compose exec api alembic upgrade head

seed:          ## Seed demo data
	docker compose exec api python -m app.cli seed

test: test-backend ## Run all backend tests

test-backend:
	cd backend && pytest

e2e:           ## Run Playwright e2e (stack must be up)
	cd tests/e2e && npm test

backup:
	bash scripts/backup.sh

deploy:
	bash scripts/deploy.sh
