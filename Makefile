.PHONY: backend frontend test lint install \
       test-llm test-flights test-api test-schemas test-frontend \
       lint-backend lint-frontend

# ── Setup ────────────────────────────────────────────────────────────────────

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

# ── Run ──────────────────────────────────────────────────────────────────────

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

# ── Test (all) ───────────────────────────────────────────────────────────────

test: test-backend test-frontend-build

test-backend:
	cd backend && python -m pytest tests/ -v

test-frontend-build:
	cd frontend && npm run build

# ── Test (per module) ────────────────────────────────────────────────────────
# Each team member can run only their module's tests:
#   make test-llm        → LLM / orchestration team
#   make test-flights    → Flight search / data team
#   make test-api        → API / integration team
#   make test-schemas    → Shared schemas (flight search / data team)

test-llm:
	cd backend && python -m pytest tests/test_provider.py -v

test-flights:
	cd backend && python -m pytest tests/test_amadeus_client.py tests/test_scoring.py tests/test_regions.py -v

test-api:
	cd backend && python -m pytest tests/test_chat_api.py tests/test_session.py tests/test_config.py -v

test-schemas:
	cd backend && python -m pytest tests/test_schemas.py -v

test-contracts:
	cd backend && python -m pytest tests/test_contracts.py -v

# ── Lint (all) ───────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check app/ tests/

lint-frontend:
	cd frontend && npx eslint src/

# ── Lint (per module) ────────────────────────────────────────────────────────

lint-llm:
	cd backend && ruff check app/llm/ tests/test_provider.py

lint-flights:
	cd backend && ruff check app/flights/ app/schemas/ tests/test_amadeus_client.py tests/test_scoring.py tests/test_regions.py tests/test_schemas.py

lint-api:
	cd backend && ruff check app/main.py app/config.py app/session.py app/routers/ tests/test_chat_api.py tests/test_session.py tests/test_config.py

