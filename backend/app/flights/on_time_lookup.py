"""On-time arrival likelihood from historical trends (BTS-style data).

Three tiers of resolution, checked in order:
1. Route + airline  (origin_destination_carrier → rate)
2. Route only       (origin_destination → rate)
3. Airline only     (carrier → rate)

Falls back to industry-average if nothing matches.
"""

# -- Tier 1 & 2: route-level on-time rates (BTS TranStats approximations) ----------
# Key format: "ORIGIN_DEST" or "ORIGIN_DEST_CARRIER"
ROUTE_ON_TIME_RATE: dict[str, float] = {
    # High-traffic domestic US routes
    "JFK_LAX": 0.79,
    "LAX_JFK": 0.78,
    "JFK_LAX_DL": 0.83,
    "JFK_LAX_AA": 0.74,
    "JFK_LAX_B6": 0.72,
    "JFK_MIA": 0.81,
    "JFK_MIA_DL": 0.84,
    "JFK_MIA_AA": 0.76,
    "JFK_SFO": 0.78,
    "JFK_SFO_DL": 0.82,
    "JFK_SFO_UA": 0.76,
    "JFK_ORD": 0.76,
    "JFK_ORD_AA": 0.73,
    "JFK_ORD_UA": 0.75,
    "LAX_SFO": 0.84,
    "SFO_LAX": 0.85,
    "ORD_LAX": 0.77,
    "LAX_ORD": 0.76,
    "ATL_LAX": 0.80,
    "LAX_ATL": 0.79,
    "ATL_JFK": 0.81,
    "JFK_ATL": 0.80,
    "ATL_ORD": 0.78,
    "ORD_ATL": 0.77,
    "DFW_LAX": 0.80,
    "LAX_DFW": 0.79,
    "DEN_LAX": 0.82,
    "LAX_DEN": 0.81,
    "SEA_LAX": 0.83,
    "LAX_SEA": 0.82,
    "SFO_JFK": 0.77,
    "BOS_JFK": 0.83,
    "JFK_BOS": 0.84,
    "EWR_LAX": 0.74,
    "LAX_EWR": 0.73,
    "EWR_SFO": 0.73,
    "SFO_EWR": 0.72,
    "LGA_ORD": 0.77,
    "ORD_LGA": 0.76,
    "LGA_ATL": 0.79,
    "ATL_LGA": 0.78,
    "DFW_ORD": 0.79,
    "ORD_DFW": 0.78,
    "MIA_ATL": 0.80,
    "ATL_MIA": 0.81,
    # International routes
    "JFK_LHR": 0.82,
    "LHR_JFK": 0.80,
    "JFK_LHR_BA": 0.79,
    "JFK_LHR_DL": 0.84,
    "JFK_CDG": 0.80,
    "CDG_JFK": 0.79,
    "JFK_NRT": 0.86,
    "NRT_JFK": 0.85,
    "JFK_NRT_JL": 0.89,
    "JFK_NRT_NH": 0.90,
    "LAX_NRT": 0.87,
    "NRT_LAX": 0.86,
    "LAX_ICN": 0.85,
    "ICN_LAX": 0.84,
    "LAX_HND": 0.88,
    "SFO_LHR": 0.80,
    "LHR_SFO": 0.79,
    "SFO_NRT": 0.86,
    "ORD_LHR": 0.79,
    "LHR_ORD": 0.78,
    "JFK_DXB": 0.84,
    "DXB_JFK": 0.83,
    "JFK_DXB_EK": 0.87,
    "JFK_DOH": 0.85,
    "DOH_JFK": 0.84,
    "JFK_DOH_QR": 0.86,
    "SFO_SIN": 0.87,
    "SIN_SFO": 0.86,
    "SFO_SIN_SQ": 0.90,
    "JFK_FCO": 0.77,
    "FCO_JFK": 0.76,
    "LAX_SYD": 0.82,
    "SYD_LAX": 0.81,
    "JFK_CUN": 0.83,
    "MIA_BOG": 0.78,
    "MIA_GRU": 0.77,
    "DFW_EZE": 0.76,
}

# -- Tier 3: airline-level on-time rates -------------------------------------------
AIRLINE_ON_TIME_RATE: dict[str, float] = {
    "DL": 0.818,   # Delta
    "HA": 0.836,   # Hawaiian
    "WN": 0.799,   # Southwest
    "AS": 0.762,   # Alaska
    "B6": 0.731,   # JetBlue
    "NK": 0.695,   # Spirit
    "F9": 0.695,   # Frontier
    "AA": 0.725,   # American
    "UA": 0.76,    # United
    "G4": 0.75,    # Allegiant
    "SY": 0.77,    # Sun Country
    "QX": 0.80,    # Horizon (Alaska regional)
    "YX": 0.82,    # Republic
    "9E": 0.78,    # Endeavor
    "OH": 0.78,    # PSA (American regional)
    "MQ": 0.76,    # Envoy (American)
    "OO": 0.798,   # SkyWest
    "CP": 0.80,    # Compass (historical)
    "BA": 0.78,    # British Airways
    "LH": 0.80,    # Lufthansa
    "AF": 0.78,    # Air France
    "KL": 0.79,    # KLM
    "AC": 0.77,    # Air Canada
    "EK": 0.82,    # Emirates
    "SQ": 0.85,    # Singapore
    "NH": 0.88,    # ANA
    "JL": 0.86,    # Japan Airlines
    "CX": 0.84,    # Cathay Pacific
    "QR": 0.82,    # Qatar
    "TK": 0.78,    # Turkish
    "IB": 0.76,    # Iberia
    "AZ": 0.77,    # ITA
}

DEFAULT_ON_TIME_RATE = 0.78  # Industry average fallback


def _norm_code(code: str | None) -> str:
    """Normalize an IATA code to uppercase, stripped."""
    if not code:
        return ""
    c = code.strip().upper()
    return c[:2] if len(c) > 3 else c  # airline codes ≤2, airport codes = 3


def get_on_time_likelihood(
    airline_code: str | None,
    origin_airport: str | None = None,
    destination_airport: str | None = None,
) -> float | None:
    """Return on-time arrival likelihood (0–1).

    Lookup order:
    1. Route + carrier  (e.g. JFK_LAX_DL)
    2. Route only       (e.g. JFK_LAX)
    3. Carrier only     (e.g. DL)
    4. Default industry average
    Returns None only when airline_code is empty so the UI can hide the metric.
    """
    carrier = _norm_code(airline_code)
    if not carrier:
        return None

    origin = origin_airport.strip().upper() if origin_airport else ""
    dest = destination_airport.strip().upper() if destination_airport else ""

    if origin and dest:
        route_carrier_key = f"{origin}_{dest}_{carrier}"
        if route_carrier_key in ROUTE_ON_TIME_RATE:
            return ROUTE_ON_TIME_RATE[route_carrier_key]
        route_key = f"{origin}_{dest}"
        if route_key in ROUTE_ON_TIME_RATE:
            return ROUTE_ON_TIME_RATE[route_key]

    return AIRLINE_ON_TIME_RATE.get(carrier, DEFAULT_ON_TIME_RATE)
