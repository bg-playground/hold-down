from __future__ import annotations

import json
import sys

from holddown.gate import run_gate
from holddown.suite import run_suite


def main() -> int:
    report = run_suite()
    print(report.render())
    if len(sys.argv) > 1 and sys.argv[1] == "--trace":
        launch_id = sys.argv[2] if len(sys.argv) > 2 else "cape-dusk"
        result = run_gate(launch_id)
        payload = {
            "launchId": result.launch_id,
            "verdict": result.verdict,
            "reason": result.reason,
            "findings": result.findings,
            "intent": None if result.intent is None else result.intent.as_dict(),
            "tokens": result.tokens,
            "latencyMs": result.latency_ms,
            "escapedHazard": result.escaped_hazard,
            "events": [
                {
                    "id": event.id,
                    "actor": event.actor,
                    "name": event.name,
                    "detail": event.detail,
                    "tokens": event.tokens,
                    "earned": event.earned,
                    "toolCallId": event.tool_call_id,
                }
                for event in result.events
            ],
        }
        print()
        print(json.dumps(payload, indent=2))
    return 0 if report.failed == 0 and report.escaped_hazards == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
