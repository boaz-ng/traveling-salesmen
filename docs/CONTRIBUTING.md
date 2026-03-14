# Contributing to Traveling Salesmen

## Prerequisites

- Python 3.11+
- Node.js 18+
- API keys: Qwen/DashScope or Anthropic (see `.env.example`), Amadeus (test tier)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/boaz-ng/traveling-salesmen.git
   cd traveling-salesmen
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install all dependencies**
   ```bash
   make install
   ```

4. **Set up pre-commit hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Team Ownership

The codebase is split into four modules, each owned by one team member:

| Module | Owner | Directory | Tests | Make targets |
|--------|-------|-----------|-------|--------------|
| **Frontend** | Person 1 | `frontend/` | `npm run build` | `make frontend`, `make lint-frontend`, `make test-frontend-build` |
| **LLM / Orchestration** | Person 2 | `backend/app/llm/` | `test_provider.py` | `make test-llm`, `make lint-llm` |
| **Flight Search / Data** | Person 3 | `backend/app/flights/`, `backend/app/schemas/` | `test_amadeus_client.py`, `test_scoring.py`, `test_regions.py`, `test_schemas.py` | `make test-flights`, `make test-schemas`, `make lint-flights` |
| **API / Integration** | Person 4 | `backend/app/routers/`, `main.py`, `session.py`, `config.py` | `test_chat_api.py`, `test_session.py`, `test_config.py` | `make test-api`, `make lint-api` |

**Contract tests** (`test_contracts.py`) verify the interfaces between modules. Run them with `make test-contracts` — everyone should run these before opening a PR.

### Module boundaries

- **Schemas** (`backend/app/schemas/`) are the shared contract. Changes here affect everyone — coordinate before modifying.
- **LLM ↔ Flights**: The `handle_tool_call()` function in `provider.py` is the seam. LLM team owns the tool schemas; Flights team owns the implementation.
- **API ↔ Orchestrator**: The chat router calls `run_conversation()` — the function signature is the contract.
- **Frontend ↔ Backend**: The `POST /chat` request/response shape (defined in `schemas/chat.py`) is the contract.

## Running

```bash
# Start the backend (from project root)
make backend

# Start the frontend (in another terminal)
make frontend

# Run all tests
make test

# Run only your module's tests
make test-llm          # LLM team
make test-flights      # Flight search team
make test-api          # API team
make test-frontend-build  # Frontend team

# Run contract tests (everyone)
make test-contracts

# Lint
make lint              # all
make lint-backend      # Python only
make lint-frontend     # JS only
make lint-llm          # LLM module only
make lint-flights      # Flights module only
make lint-api          # API module only
```

## Code Style

- **Python**: We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting (100 char line length). Run `ruff check` before committing.
- **JavaScript**: We use [ESLint](https://eslint.org/) with the flat config in `frontend/eslint.config.js`. Run `npx eslint src/` in the frontend directory.
- **Pre-commit hooks**: Install with `pre-commit install` to auto-run ruff and eslint on staged files.

## Testing

- Backend tests are in `backend/tests/`
- Run all tests: `make test`
- Run module tests: `make test-llm`, `make test-flights`, `make test-api`, `make test-schemas`
- Run contract tests: `make test-contracts`
- When adding new features, add corresponding tests in the module test file
- Mock external API calls (Amadeus, Claude, Qwen) in tests
- **Always run contract tests** before opening a PR to ensure module boundaries are intact

## Making Changes

1. Create a feature branch from `main`
2. Make your changes within your owned module
3. Run your module's tests and lint
4. Run `make test-contracts` to check module boundaries
5. Run `make test` for the full suite
6. Submit a pull request with a clear description

## Key Files to Know

- `backend/app/schemas/intent.py` — The `FlightSearchIntent` model is the contract between the LLM layer and the flight search layer. See [INTENT_SCHEMA.md](INTENT_SCHEMA.md).
- `backend/app/llm/provider.py` — Abstract `LLMProvider` base class + shared tool handler
- `backend/app/llm/orchestrator.py` — Provider factory (toggle via `LLM_PROVIDER` env var)
- `backend/app/flights/regions.py` — Region-to-airport mapping (easy to extend)
- `backend/app/flights/scoring.py` — Flight scoring weights
- `backend/tests/test_contracts.py` — Cross-module contract tests
