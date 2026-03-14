# ✈️ Flight Concierge

A conversational flight search tool. Tell it something like *"fly from NYC to somewhere warm in late June, under $400"* and it interprets your intent, asks clarifying questions if needed, searches the Amadeus flight API, scores results, and presents the top options. Uses an **LLM-as-orchestrator** architecture with pluggable providers — currently supports **Qwen** (default) and **Anthropic Claude**, toggled via a single env var.

## Architecture

```mermaid
flowchart LR
    User([User]) --> Frontend[React Frontend]
    Frontend -->|POST /chat| FastAPI[FastAPI Backend]
    FastAPI --> Orchestrator[Orchestrator]
    Orchestrator -->|provider toggle| Provider{LLM Provider}
    Provider -->|Qwen| Qwen[Qwen API]
    Provider -->|Anthropic| Claude[Claude API]
    Orchestrator --> Regions[Region Resolver]
    Orchestrator --> AmadeusClient[Amadeus Client]
    AmadeusClient --> Amadeus[Amadeus API]
    AmadeusClient --> Scoring[Scoring Engine]
    Scoring --> Orchestrator
    Orchestrator --> FastAPI
    FastAPI --> Frontend
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- LLM API key: [Qwen/DashScope](https://dashscope.console.aliyun.com/) (default) or [Anthropic](https://console.anthropic.com/)
- [Amadeus](https://developers.amadeus.com/) API key (free test tier)

### Setup

```bash
# Clone
git clone https://github.com/boaz-ng/traveling-salesmen.git
cd traveling-salesmen

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
make install
```

### Run

```bash
# Terminal 1: Backend
make backend

# Terminal 2: Frontend
make frontend
```

Open http://localhost:5173 and start chatting.

### Test

```bash
make test
```

## Project Structure

```
├── README.md
├── .env.example
├── Makefile
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment config
│   │   ├── session.py           # In-memory session store
│   │   ├── routers/chat.py      # POST /chat endpoint
│   │   ├── llm/
│   │   │   ├── orchestrator.py  # Provider factory + delegation
│   │   │   ├── provider.py      # Abstract LLMProvider base class
│   │   │   ├── qwen_provider.py # Qwen (OpenAI-compatible) provider
│   │   │   ├── anthropic_provider.py # Anthropic (Claude) provider
│   │   │   ├── tools.py         # Tool definitions (both formats)
│   │   │   └── prompts.py       # System prompt
│   │   ├── flights/
│   │   │   ├── amadeus_client.py
│   │   │   ├── scoring.py
│   │   │   └── regions.py
│   │   └── schemas/
│   │       ├── intent.py        # FlightSearchIntent (team contract)
│   │       ├── chat.py
│   │       └── flight.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   │       ├── ChatWindow.jsx
│   │       ├── MessageBubble.jsx
│   │       └── FlightCard.jsx
│   └── vite.config.js
└── docs/
    ├── ARCHITECTURE.md
    ├── CONTRIBUTING.md
    └── INTENT_SCHEMA.md
```

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for setup instructions and guidelines.

## Current Status

- ✅ Project scaffold and architecture
- ✅ Backend: FastAPI + LLM orchestrator + Amadeus integration
- ✅ Pluggable LLM providers: Qwen (default) and Anthropic Claude
- ✅ Frontend: React chat interface with flight cards
- ✅ Scoring engine with cost/comfort/balanced preferences
- ✅ Region-to-airport resolution
- ✅ Tests for scoring, regions, Amadeus client, and provider abstraction
