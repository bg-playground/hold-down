from __future__ import annotations

import math


def haversine_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    earth_km = 6371.0
    d_lat = math.radians(b_lat - a_lat)
    d_lon = math.radians(b_lon - a_lon)
    lat1 = math.radians(a_lat)
    lat2 = math.radians(b_lat)
    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    return 2 * earth_km * math.asin(math.sqrt(h))


def round1(value: float) -> float:
    # Match JS Math.round for positive distances (half away from -inf).
    return math.floor(value * 10 + 0.5) / 10
