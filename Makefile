.PHONY: backend frontend test lint install

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest tests/ -v

lint:
	cd backend && ruff check app/ tests/
	cd frontend && npx eslint src/
