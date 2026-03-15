"""Pydantic models for the collaborative flight wallet API."""

from typing import Any

from pydantic import BaseModel, Field


class WalletCreate(BaseModel):
    name: str = Field(default="My Trip", max_length=120)


class WalletFlightAdd(BaseModel):
    flight_data: dict[str, Any]
    added_by: str = Field(default="Anonymous", max_length=60)
    notes: str = Field(default="", max_length=500)


class WalletFlightOut(BaseModel):
    id: str
    wallet_id: str
    flight_data: dict[str, Any]
    added_by: str
    notes: str
    added_at: str


class WalletOut(BaseModel):
    id: str
    name: str
    created_at: str
    flights: list[WalletFlightOut] = []
