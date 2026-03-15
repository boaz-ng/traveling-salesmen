"""REST endpoints for collaborative flight wallets."""

from fastapi import APIRouter, HTTPException

from app.db import add_flight, create_wallet, get_wallet, remove_flight
from app.schemas.wallet import WalletCreate, WalletFlightAdd, WalletFlightOut, WalletOut

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("", response_model=WalletOut, status_code=201)
async def create_wallet_endpoint(body: WalletCreate) -> WalletOut:
    wallet = await create_wallet(body.name)
    return WalletOut(**wallet, flights=[])


@router.get("/{wallet_id}", response_model=WalletOut)
async def get_wallet_endpoint(wallet_id: str) -> WalletOut:
    wallet = await get_wallet(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletOut(**wallet)


@router.post("/{wallet_id}/flights", response_model=WalletFlightOut, status_code=201)
async def add_flight_endpoint(wallet_id: str, body: WalletFlightAdd) -> WalletFlightOut:
    wallet = await get_wallet(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    flight = await add_flight(wallet_id, body.flight_data, body.added_by, body.notes)
    return WalletFlightOut(**flight)


@router.delete("/{wallet_id}/flights/{flight_id}", status_code=204)
async def remove_flight_endpoint(wallet_id: str, flight_id: str) -> None:
    removed = await remove_flight(wallet_id, flight_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Flight not found in wallet")
