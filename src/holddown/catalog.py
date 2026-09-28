"""Recorded range card. Not a live clearance."""

from __future__ import annotations

from dataclasses import dataclass

MIN_KM = 10.0
MAX_KM = 50.0
TOKEN_BUDGET = 800
LATENCY_BUDGET_MS = 1500
ARRIVAL_BUFFER_MIN = 90
BUDGET_INFLATION = 2000

DISCLAIMER = (
    "Document only. Not a clearance, not an official viewing site, and not a sent route."
)


@dataclass(frozen=True)
class Pad:
    id: str
    name: str
    region: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Site:
    id: str
    name: str
    region: str
    lat: float
    lon: float
    note: str


@dataclass(frozen=True)
class Weather:
    flight: str
    viewer: str
    wind_kt: int


@dataclass(frozen=True)
class Launch:
    id: str
    name: str
    vehicle: str
    pad_id: str
    t0: str | None
    status: str
    net_confirmed: bool
    weather: Weather
    closure_site_ids: tuple[str, ...]


PADS: dict[str, Pad] = {
    "slc-40": Pad("slc-40", "SLC-40", "cape", 28.5618, -80.5772),
    "slc-4e": Pad("slc-4e", "SLC-4E", "vandenberg", 34.6321, -120.6108),
    "olm": Pad("olm", "Orbital Launch Mount", "starbase", 25.9972, -97.1554),
}

SITES: dict[str, Site] = {
    "playalinda-beach": Site(
        "playalinda-beach", "Playalinda Beach", "cape", 28.6495, -80.632, "Often inside a Cape closure"
    ),
    "space-view-park": Site(
        "space-view-park", "Space View Park", "cape", 28.6274, -80.8072, "Titusville"
    ),
    "jetty-park": Site("jetty-park", "Jetty Park", "cape", 28.4077, -80.5933, "Port Canaveral"),
    "surf-beach": Site(
        "surf-beach", "Surf Beach", "vandenberg", 34.6828, -120.6068, "Frequently closed for launches"
    ),
    "harris-grade": Site(
        "harris-grade", "Harris Grade overlook", "vandenberg", 34.5458, -120.3915, "Inland public overlook"
    ),
    "boca-chica-beach": Site(
        "boca-chica-beach", "Boca Chica Beach", "starbase", 25.9965, -97.155, "On the range"
    ),
    "isla-blanca": Site(
        "isla-blanca",
        "Isla Blanca viewpoint",
        "starbase",
        26.1,
        -97.17,
        "Approximate north-island gazetteer point",
    ),
}

PREFERENCE: dict[str, tuple[str, ...]] = {
    "cape": ("playalinda-beach", "space-view-park", "jetty-park"),
    "vandenberg": ("surf-beach", "harris-grade"),
    "starbase": ("boca-chica-beach", "isla-blanca"),
}

LAUNCHES: dict[str, Launch] = {
    item.id: item
    for item in (
        Launch(
            "cape-dusk",
            "Cape Dusk Starlink",
            "Falcon 9",
            "slc-40",
            "2026-10-04T23:14:00Z",
            "go",
            True,
            Weather("go", "clear", 8),
            ("playalinda-beach",),
        ),
        Launch(
            "vandenberg-wx",
            "Vandenberg Weather Hold",
            "Falcon 9",
            "slc-4e",
            "2026-10-06T18:30:00Z",
            "go",
            True,
            Weather("no-go", "hazard", 28),
            ("surf-beach",),
        ),
        Launch(
            "starbase-net",
            "Starbase NET Unconfirmed",
            "Starship",
            "olm",
            None,
            "tbd",
            False,
            Weather("go", "clear", 6),
            ("boca-chica-beach",),
        ),
    )
}


def launch_by_id(launch_id: str) -> Launch:
    try:
        return LAUNCHES[launch_id]
    except KeyError as exc:
        raise KeyError(f"unknown launch {launch_id}") from exc
