"""Golden document. The console is a view of this file, not a second engine."""

from __future__ import annotations

import json
from pathlib import Path

from holddown import __version__
from holddown.catalog import LAUNCHES, PADS, RANGE_TZ, SITES
from holddown.gate import run_gate
from holddown.suite import SUITE

ATTACKS = ("none", "raw_coordinate", "closed_only", "parrot", "budget")


def _event(event) -> dict:
    return {
        "id": event.id,
        "atMs": event.at_ms,
        "actor": event.actor,
        "name": event.name,
        "detail": event.detail,
        "tokens": event.tokens,
        "latencyMs": event.latency_ms,
        "earned": event.earned,
        "toolCallId": event.tool_call_id,
    }


def _case(launch_id: str, attack: str, judge_override: str | None) -> dict:
    result = run_gate(launch_id, attack, judge_override)
    return {
        "launchId": launch_id,
        "attack": attack,
        "judgeOverride": judge_override == "pin",
        "verdict": result.verdict,
        "reason": result.reason,
        "findings": result.findings,
        "siteChecks": [
            {
                "siteId": check.site_id,
                "code": check.code,
                "detail": check.detail,
                "distanceKm": check.distance_km,
                "toolCallId": check.tool_call_id,
            }
            for check in result.site_checks
        ],
        "intent": None if result.intent is None else result.intent.as_dict(),
        "suppressedSiteId": result.suppressed_site_id,
        "events": [_event(event) for event in result.events],
        "tokens": result.tokens,
        "latencyMs": result.latency_ms,
        "tokenBudget": result.token_budget,
        "latencyBudgetMs": result.latency_budget_ms,
        "judgeBlocked": result.judge_blocked,
        "judge": {
            "provenance": result.judge_provenance,
            "constraint": result.judge_constraint,
            "refusal": result.judge_refusal,
            "note": result.judge_note,
        },
        "escapedHazard": result.escaped_hazard,
    }


def build_document() -> dict:
    cases = [
        _case(launch.id, attack, override)
        for launch in LAUNCHES.values()
        for attack in ATTACKS
        for override in (None, "pin")
    ]
    card = [
        {
            "id": spec.id,
            "label": spec.label,
            "launchId": spec.launch_id,
            "attack": spec.attack,
            "judgeOverride": spec.judge_override == "pin",
        }
        for spec in SUITE
    ]
    escaped = sum(1 for case in cases if case["escapedHazard"])
    return {
        "engine": "holddown",
        "version": __version__,
        "escapedHazards": escaped,
        "pads": {
            pad.id: {"name": pad.name, "region": pad.region, "lat": pad.lat, "lon": pad.lon}
            for pad in PADS.values()
        },
        "sites": {
            site.id: {
                "name": site.name,
                "region": site.region,
                "lat": site.lat,
                "lon": site.lon,
                "note": site.note,
            }
            for site in SITES.values()
        },
        "rangeTz": RANGE_TZ,
        "launches": [
            {
                "id": launch.id,
                "name": launch.name,
                "vehicle": launch.vehicle,
                "padId": launch.pad_id,
                "t0": launch.t0,
                "status": launch.status,
                "netConfirmed": launch.net_confirmed,
            }
            for launch in LAUNCHES.values()
        ],
        "card": card,
        "cases": cases,
    }


def write_document(path: Path) -> dict:
    document = build_document()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n")
    return document
