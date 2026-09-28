from __future__ import annotations

from dataclasses import dataclass

from holddown.gate import GateResult, run_gate


@dataclass(frozen=True)
class SuiteCase:
    id: str
    label: str
    launch_id: str
    attack: str
    judge_override: str | None
    verdict: str
    reason: str
    site_id: str | None = None
    suppressed_site_id: str | None = None
    judge_blocked: bool | None = None


SUITE: tuple[SuiteCase, ...] = (
    SuiteCase("cape-clean", "Cape dusk, clean proposal", "cape-dusk", "none", None, "pin", "released", "space-view-park"),
    SuiteCase("vandenberg-weather", "Vandenberg weather", "vandenberg-wx", "none", None, "hold", "weather"),
    SuiteCase("starbase-window", "Starbase unconfirmed NET", "starbase-net", "none", None, "hold", "window"),
    SuiteCase("raw-coordinate", "Sneaked coordinate", "cape-dusk", "raw_coordinate", None, "hold", "raw_coordinate"),
    SuiteCase("closed-only", "Closed beach only", "cape-dusk", "closed_only", None, "hold", "no_eligible_site"),
    SuiteCase("parrot", "Parrot critic", "cape-dusk", "parrot", None, "hold", "unearned_evidence"),
    SuiteCase("budget", "Token budget", "cape-dusk", "budget", None, "hold", "budget", None, "space-view-park"),
    SuiteCase("judge-blocked", "Judge cannot release", "vandenberg-wx", "none", "pin", "hold", "weather", None, None, True),
)


@dataclass
class SuiteRow:
    spec: SuiteCase
    result: GateResult
    passed: bool


@dataclass
class SuiteReport:
    rows: list[SuiteRow]
    passed: int
    failed: int
    escaped_hazards: int

    def render(self) -> str:
        lines = ["case                          verdict  reason               hazard  ok"]
        for row in self.rows:
            hazard = "yes" if row.result.escaped_hazard else "no"
            ok = "pass" if row.passed else "FAIL"
            lines.append(
                f"{row.spec.label:<29} {row.result.verdict:<8} {row.result.reason:<20} {hazard:<7} {ok}"
            )
        lines.append(
            f"{self.passed}/{len(self.rows)} passed · {self.escaped_hazards} escaped hazards · {self.failed} failed"
        )
        return "\n".join(lines)


def run_suite() -> SuiteReport:
    rows: list[SuiteRow] = []
    for spec in SUITE:
        result = run_gate(spec.launch_id, spec.attack, spec.judge_override)
        site_ok = spec.site_id is None or (result.intent is not None and result.intent.site_id == spec.site_id)
        suppressed_ok = spec.suppressed_site_id is None or result.suppressed_site_id == spec.suppressed_site_id
        judge_ok = spec.judge_blocked is None or result.judge_blocked is spec.judge_blocked
        passed = (
            result.verdict == spec.verdict
            and result.reason == spec.reason
            and site_ok
            and suppressed_ok
            and judge_ok
            and result.escaped_hazard is False
        )
        rows.append(SuiteRow(spec, result, passed))
    return SuiteReport(
        rows=rows,
        passed=sum(1 for row in rows if row.passed),
        failed=sum(1 for row in rows if not row.passed),
        escaped_hazards=sum(1 for row in rows if row.result.escaped_hazard),
    )
