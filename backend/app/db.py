"""SQLite database layer for collaborative flight wallets."""

import json
import uuid
from pathlib import Path
from typing import Any

import aiosqlite

DB_PATH = Path(__file__).parent.parent.parent / "wallet.db"

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS wallets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'My Trip',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS wallet_flights (
    id TEXT PRIMARY KEY,
    wallet_id TEXT NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    added_by TEXT NOT NULL DEFAULT 'Anonymous',
    notes TEXT NOT NULL DEFAULT '',
    flight_data TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_CREATE_TABLES)
        await db.execute("PRAGMA foreign_keys = ON")
        await db.commit()


async def create_wallet(name: str = "My Trip") -> dict[str, Any]:
    wallet_id = uuid.uuid4().hex[:12]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            "INSERT INTO wallets (id, name) VALUES (?, ?)",
            (wallet_id, name),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT id, name, created_at FROM wallets WHERE id = ?", (wallet_id,)
        )
        row = await cursor.fetchone()
    return {"id": row[0], "name": row[1], "created_at": row[2]}


async def get_wallet(wallet_id: str) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        cursor = await db.execute(
            "SELECT id, name, created_at FROM wallets WHERE id = ?", (wallet_id,)
        )
        wallet_row = await cursor.fetchone()
        if not wallet_row:
            return None

        cursor = await db.execute(
            "SELECT id, wallet_id, added_by, notes, flight_data, added_at "
            "FROM wallet_flights WHERE wallet_id = ? ORDER BY added_at DESC",
            (wallet_id,),
        )
        flight_rows = await cursor.fetchall()

    flights = [
        {
            "id": r[0],
            "wallet_id": r[1],
            "added_by": r[2],
            "notes": r[3],
            "flight_data": json.loads(r[4]),
            "added_at": r[5],
        }
        for r in flight_rows
    ]

    return {
        "id": wallet_row[0],
        "name": wallet_row[1],
        "created_at": wallet_row[2],
        "flights": flights,
    }


async def add_flight(
    wallet_id: str,
    flight_data: dict[str, Any],
    added_by: str = "Anonymous",
    notes: str = "",
) -> dict[str, Any]:
    flight_id = uuid.uuid4().hex[:12]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            "INSERT INTO wallet_flights (id, wallet_id, added_by, notes, flight_data) "
            "VALUES (?, ?, ?, ?, ?)",
            (flight_id, wallet_id, added_by, notes, json.dumps(flight_data)),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT id, wallet_id, added_by, notes, flight_data, added_at "
            "FROM wallet_flights WHERE id = ?",
            (flight_id,),
        )
        row = await cursor.fetchone()

    return {
        "id": row[0],
        "wallet_id": row[1],
        "added_by": row[2],
        "notes": row[3],
        "flight_data": json.loads(row[4]),
        "added_at": row[5],
    }


async def remove_flight(wallet_id: str, flight_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        cursor = await db.execute(
            "DELETE FROM wallet_flights WHERE id = ? AND wallet_id = ?",
            (flight_id, wallet_id),
        )
        await db.commit()
        return cursor.rowcount > 0
