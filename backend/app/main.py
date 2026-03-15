"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers.chat import router as chat_router
from app.routers.wallet import router as wallet_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Traveling Salesman",
    description="Conversational flight search powered by Claude Agent SDK and SerpApi",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(wallet_router)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
