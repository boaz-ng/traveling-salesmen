"""Static airport information for major airports worldwide.

Provides terminal, lounge, and general info so the agent can answer
"What's at JFK?" or "Lounges at LAX" without an external API.
"""

from typing import Any

AIRPORT_DATA: dict[str, dict[str, Any]] = {
    "JFK": {
        "name": "John F. Kennedy International Airport",
        "city": "New York",
        "country": "US",
        "terminals": ["Terminal 1", "Terminal 2", "Terminal 4", "Terminal 5", "Terminal 7", "Terminal 8"],
        "lounges": [
            "Centurion Lounge (T4)",
            "Delta Sky Club (T2, T4)",
            "British Airways Galleries (T7)",
            "Turkish Airlines Lounge (T1)",
            "Admirals Club (T8)",
            "TWA Hotel (T5)",
        ],
        "tips": "AirTrain connects all terminals. Allow extra time for Terminal 1 security.",
    },
    "LAX": {
        "name": "Los Angeles International Airport",
        "city": "Los Angeles",
        "country": "US",
        "terminals": ["Terminal 1", "Terminal 2", "Terminal 3", "Terminal 4", "Terminal 5", "Terminal 6", "Terminal 7", "Terminal 8", "Tom Bradley International Terminal (TBIT)"],
        "lounges": [
            "Star Alliance Lounge (TBIT)",
            "Centurion Lounge (TBIT)",
            "Delta Sky Club (T2, T3)",
            "United Club (T7, T8)",
            "Qantas First Lounge (TBIT)",
            "Korean Air Lounge (TBIT)",
        ],
        "tips": "Use the LAX-it lot for rideshare pickups. Inter-terminal buses run airside.",
    },
    "ORD": {
        "name": "O'Hare International Airport",
        "city": "Chicago",
        "country": "US",
        "terminals": ["Terminal 1 (United)", "Terminal 2 (Delta, other domestic)", "Terminal 3 (American)", "Terminal 5 (International)"],
        "lounges": [
            "United Polaris Lounge (T1)",
            "United Club (T1, T2)",
            "Centurion Lounge (T3)",
            "Admirals Club (T3)",
            "Delta Sky Club (T2)",
        ],
        "tips": "ATS people-mover connects T1–T3. T5 requires re-screening; allow 30+ min to transfer.",
    },
    "ATL": {
        "name": "Hartsfield-Jackson Atlanta International Airport",
        "city": "Atlanta",
        "country": "US",
        "terminals": ["Domestic Terminal (North/South)", "Concourse T", "Concourses A–F", "International Terminal (Concourse F)"],
        "lounges": [
            "Delta Sky Club (Concourses A, B, C, E, F, T)",
            "The Club ATL (Concourse B, T)",
            "Centurion Lounge (Concourse T)",
        ],
        "tips": "Plane Train connects all concourses in ~2 min. World's busiest airport by passengers.",
    },
    "SFO": {
        "name": "San Francisco International Airport",
        "city": "San Francisco",
        "country": "US",
        "terminals": ["Terminal 1", "Terminal 2", "Terminal 3", "International Terminal (A/G)"],
        "lounges": [
            "Centurion Lounge (T3)",
            "United Polaris Lounge (Int'l G)",
            "United Club (T3, Int'l G)",
            "SFO Museum galleries throughout",
        ],
        "tips": "BART runs directly to Terminal 1. AirTrain connects all terminals airside.",
    },
    "MIA": {
        "name": "Miami International Airport",
        "city": "Miami",
        "country": "US",
        "terminals": ["North Terminal (D)", "Central Terminal (E, F)", "South Terminal (H, J)"],
        "lounges": [
            "Centurion Lounge (Concourse D)",
            "Admirals Club (Concourse D)",
            "Delta Sky Club (Concourse J)",
            "Turkish Airlines Lounge (Concourse E)",
        ],
        "tips": "MIA Mover connects to the Miami Intermodal Center (Metrorail, Tri-Rail).",
    },
    "DFW": {
        "name": "Dallas/Fort Worth International Airport",
        "city": "Dallas",
        "country": "US",
        "terminals": ["Terminal A", "Terminal B", "Terminal C", "Terminal D (International)", "Terminal E"],
        "lounges": [
            "Centurion Lounge (Terminal D)",
            "Admirals Club (A, C, D)",
            "Capital One Lounge (Terminal D)",
            "The Club DFW (Terminal E)",
        ],
        "tips": "Skylink train connects all 5 terminals airside in ~10 min.",
    },
    "LHR": {
        "name": "London Heathrow Airport",
        "city": "London",
        "country": "UK",
        "terminals": ["Terminal 2 (Queen's Terminal)", "Terminal 3", "Terminal 4", "Terminal 5 (British Airways)"],
        "lounges": [
            "British Airways Galleries First/Business (T3, T5)",
            "Star Alliance Lounge (T2)",
            "Cathay Pacific Lounge (T3)",
            "Plaza Premium Lounge (T2, T4, T5)",
            "Virgin Atlantic Clubhouse (T3)",
        ],
        "tips": "Heathrow Express to Paddington in 15 min. Elizabeth Line (Crossrail) is cheaper.",
    },
    "NRT": {
        "name": "Narita International Airport",
        "city": "Tokyo",
        "country": "JP",
        "terminals": ["Terminal 1 (Star Alliance, OneWorld)", "Terminal 2 (SkyTeam, LCCs)", "Terminal 3 (Budget carriers)"],
        "lounges": [
            "ANA Lounge (T1)",
            "JAL Sakura Lounge (T2)",
            "United Club (T1)",
            "Priority Pass lounges (T1, T2)",
        ],
        "tips": "Narita Express to Tokyo Station in ~60 min. Keisei Skyliner to Ueno in ~40 min.",
    },
    "HND": {
        "name": "Tokyo Haneda Airport",
        "city": "Tokyo",
        "country": "JP",
        "terminals": ["Terminal 1 (JAL domestic)", "Terminal 2 (ANA domestic)", "Terminal 3 (International)"],
        "lounges": [
            "ANA Suite Lounge (T3 Int'l)",
            "JAL First Class Lounge (T3 Int'l)",
            "TIAT Lounge (T3)",
            "Sky Lounge (T1, T2)",
        ],
        "tips": "Monorail to Hamamatsucho in 13 min. Much closer to central Tokyo than Narita.",
    },
    "SIN": {
        "name": "Singapore Changi Airport",
        "city": "Singapore",
        "country": "SG",
        "terminals": ["Terminal 1", "Terminal 2", "Terminal 3", "Terminal 4", "Jewel Changi (landside)"],
        "lounges": [
            "SilverKris Lounge (T2, T3)",
            "SATS Premier Lounge (T1, T2, T3)",
            "Qantas Singapore Lounge (T1)",
            "Plaza Premium Lounge (T1)",
        ],
        "tips": "Jewel has a 40m indoor waterfall, gardens, and 280+ shops. Free transit tours available.",
    },
    "DXB": {
        "name": "Dubai International Airport",
        "city": "Dubai",
        "country": "AE",
        "terminals": ["Terminal 1 (International airlines)", "Terminal 2 (Regional/LCC)", "Terminal 3 (Emirates exclusive)"],
        "lounges": [
            "Emirates First/Business Lounge (T3)",
            "Marhaba Lounge (T1, T3)",
            "Sleep 'n Fly pods (T1, T3)",
        ],
        "tips": "Metro Red Line runs to T1 and T3. T2 is separate; allow 60+ min for transfers.",
    },
    "CDG": {
        "name": "Paris Charles de Gaulle Airport",
        "city": "Paris",
        "country": "FR",
        "terminals": ["Terminal 1", "Terminal 2 (A–G)", "Terminal 3"],
        "lounges": [
            "Air France Salon (T2E, T2F)",
            "Star Alliance Lounge (T1)",
            "Yotel Air (T2E airside)",
            "Qantas Lounge (T1)",
        ],
        "tips": "RER B to central Paris in ~35 min. CDGVAL shuttle connects all terminals.",
    },
    "ICN": {
        "name": "Incheon International Airport",
        "city": "Seoul",
        "country": "KR",
        "terminals": ["Terminal 1 (most airlines)", "Terminal 2 (Korean Air, Delta, SkyTeam)"],
        "lounges": [
            "Korean Air Prestige Lounge (T2)",
            "Asiana Business Lounge (T1)",
            "Sky Hub Lounge (T1)",
            "Matina Lounge (T1, T2)",
        ],
        "tips": "AREX express to Seoul Station in 43 min. Free transit tours and sleeping areas available.",
    },
    "EWR": {
        "name": "Newark Liberty International Airport",
        "city": "Newark",
        "country": "US",
        "terminals": ["Terminal A (new)", "Terminal B", "Terminal C (United hub)"],
        "lounges": [
            "United Polaris Lounge (TC)",
            "United Club (T A, T C)",
            "Centurion Lounge (T A — upcoming)",
        ],
        "tips": "NJ Transit / Amtrak to Penn Station in ~30 min. AirTrain connects terminals + rail.",
    },
    "DEN": {
        "name": "Denver International Airport",
        "city": "Denver",
        "country": "US",
        "terminals": ["Jeppesen Terminal", "Concourse A (International)", "Concourse B (United, Frontier)", "Concourse C (Southwest, other)"],
        "lounges": [
            "United Club (B, C)",
            "Centurion Lounge (C)",
            "United Polaris Lounge (planned)",
        ],
        "tips": "RTD A Line train to Union Station in ~37 min. Famous blucifer horse statue outside.",
    },
    "SEA": {
        "name": "Seattle-Tacoma International Airport",
        "city": "Seattle",
        "country": "US",
        "terminals": ["Main Terminal", "North Satellite", "South Satellite", "Concourses A–D"],
        "lounges": [
            "Alaska Lounge (C, D, N Satellite)",
            "Delta Sky Club (S Satellite)",
            "Centurion Lounge (upcoming)",
            "The Club SEA (A)",
        ],
        "tips": "Link Light Rail to downtown Seattle in ~40 min. SEA is an Alaska Airlines hub.",
    },
    "BOS": {
        "name": "Boston Logan International Airport",
        "city": "Boston",
        "country": "US",
        "terminals": ["Terminal A", "Terminal B", "Terminal C", "Terminal E (International)"],
        "lounges": [
            "Delta Sky Club (A)",
            "Admirals Club (B)",
            "The Lounge (E)",
        ],
        "tips": "Blue Line T to downtown in ~20 min. Free shuttle between all terminals.",
    },
}


def get_airport_info(airport_code: str) -> dict[str, Any] | None:
    """Return static info for a major airport, or None if not in our data."""
    code = airport_code.strip().upper() if airport_code else ""
    return AIRPORT_DATA.get(code)
