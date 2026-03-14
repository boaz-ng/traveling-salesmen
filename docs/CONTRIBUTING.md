# Contributing to Flight Concierge

## Prerequisites

- Python 3.11+
- Node.js 18+
- API keys: Anthropic (Claude), Amadeus (test environment)

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

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -e ".[dev]"
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

## Running

```bash
# Start the backend (from project root)
make backend

# Start the frontend (in another terminal)
make frontend

# Run tests
make test

# Run linters
make lint
```

## Project Structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Code Style

- **Python**: We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting. Run `ruff check` before committing.
- **JavaScript**: We use [ESLint](https://eslint.org/) for linting. Run `npx eslint src/` in the frontend directory.

## Testing

- Backend tests are in `backend/tests/`
- Run with `make test` or `cd backend && pytest tests/ -v`
- When adding new features, add corresponding tests
- Mock external API calls (Amadeus, Claude) in tests

## Making Changes

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Submit a pull request with a clear description

## Key Files to Know

- `backend/app/schemas/intent.py` — The `FlightSearchIntent` model is the contract between the LLM layer and the flight search layer. See [INTENT_SCHEMA.md](INTENT_SCHEMA.md).
- `backend/app/llm/orchestrator.py` — The core conversation loop
- `backend/app/flights/regions.py` — Region-to-airport mapping (easy to extend)
- `backend/app/flights/scoring.py` — Flight scoring weights
