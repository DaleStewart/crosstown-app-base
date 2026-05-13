"""Orchestrator-level eval — grades the user-visible reply, not tool layer.

POSTs each scenario to `${ORCHESTRATOR_URL}/api/turn` in live mode, or replays
cassettes from `orch_cassettes/` in offline mode. Grades the *response text*
against expectations:

- response includes specific substrings  (`expected_substrings`)
- response surface mentions at least one citation id of each required type
- foundry evaluators (optional, `--with-foundry`) score the final reply

Hard rule: zero scenarios with `expected_substrings` may be missing all of
them. Citation regex must find at least one match if `expect_citations: true`.

Usage:
    python -m orchestrator_runner --max-fail-pct 0
    EVAL_MODE=live ORCHESTRATOR_URL=https://... python -m orchestrator_runner
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import httpx
import yaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parent
ORCH_SCENARIOS = ROOT / "orch_scenarios"
ORCH_CASSETTES = ROOT / "orch_cassettes"
REPORT = ROOT / ".report"

CITATION_REGEX = re.compile(r"\b(L-\d{6}|INC-\d{4}|RB-\d{2}[a-z0-9\-]*)\b")


@dataclass
class OrchOutcome:
    scenario_id: str
    title: str
    response: str
    passed: bool
    reason: str = ""
    missing_substrings: list[str] = field(default_factory=list)
    foundry_scores: list[dict[str, Any]] = field(default_factory=list)
    foundry_failures: list[str] = field(default_factory=list)


def load_scenarios() -> list[dict[str, Any]]:
    return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(ORCH_SCENARIOS.glob("*.yaml"))]


def load_cassette(sid: str) -> dict[str, Any] | None:
    path = ORCH_CASSETTES / f"{sid}.json"
    if not path.exists():
        return None
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj if isinstance(obj, dict) else None


def fetch_live(base_url: str, prompt: str) -> dict[str, Any]:
    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        r = client.post("/api/turn", json={"text": prompt})
        r.raise_for_status()
        obj = r.json()
        return obj if isinstance(obj, dict) else {}


def grade(scn: dict[str, Any], cassette_or_live: dict[str, Any], with_foundry: bool) -> OrchOutcome:
    out = OrchOutcome(
        scenario_id=scn["id"],
        title=scn["title"],
        response=str(cassette_or_live.get("text", "")),
        passed=True,
    )

    expected = [s.lower() for s in scn.get("expected_substrings", [])]
    lo = out.response.lower()
    out.missing_substrings = [s for s in expected if s not in lo]
    if out.missing_substrings:
        out.passed = False
        out.reason = f"missing substrings: {out.missing_substrings}"

    if scn.get("expect_citations", False):
        if not CITATION_REGEX.search(out.response):
            out.passed = False
            out.reason = (out.reason + " | no_citation_in_text").strip(" |")

    if with_foundry:
        try:
            from foundry_evaluators import PASS_BAR, run_foundry_evaluators
        except Exception as e:  # noqa: BLE001
            out.passed = False
            out.reason = (out.reason + f" | foundry import: {e}").strip(" |")
        else:
            context = "\n".join(
                str(c.get("snippet", ""))
                for c in (cassette_or_live.get("citations") or [])
                if isinstance(c, dict)
            )
            scores = run_foundry_evaluators(
                query=scn.get("prompt", ""),
                response=out.response,
                context=context,
            )
            for s in scores:
                out.foundry_scores.append({"name": s.name, "score": s.score, "reason": s.reason})
                if s.score is not None and s.score < PASS_BAR:
                    out.foundry_failures.append(f"{s.name}={s.score:.1f}")
            if out.foundry_failures:
                out.passed = False
                out.reason = (out.reason + f" | foundry: {out.foundry_failures}").strip(" |")
    return out


def run(mode: str, base_url: str | None, with_foundry: bool) -> list[OrchOutcome]:
    outcomes: list[OrchOutcome] = []
    for scn in load_scenarios():
        sid = scn["id"]
        if mode == "offline":
            cas = load_cassette(sid)
            if cas is None:
                outcomes.append(
                    OrchOutcome(
                        scenario_id=sid, title=scn["title"], response="", passed=False,
                        reason="no cassette",
                    )
                )
                continue
            payload = cas
        else:
            try:
                payload = fetch_live(base_url or "", scn["prompt"])
            except Exception as e:  # noqa: BLE001
                outcomes.append(
                    OrchOutcome(
                        scenario_id=sid, title=scn["title"], response="", passed=False,
                        reason=f"live error: {e}",
                    )
                )
                continue
        outcomes.append(grade(scn, payload, with_foundry))
    return outcomes


def render(outcomes: list[OrchOutcome], max_fail_pct: float) -> tuple[bool, dict[str, Any]]:
    console = Console(force_terminal=True, legacy_windows=False)
    t = Table(title="Orchestrator Eval Results")
    t.add_column("ID")
    t.add_column("Title")
    t.add_column("Response (head)")
    t.add_column("Reason")
    t.add_column("Pass")
    for o in outcomes:
        t.add_row(
            o.scenario_id,
            o.title[:40],
            (o.response or "")[:60].replace("\n", " "),
            o.reason or "-",
            "PASS" if o.passed else "FAIL",
        )
    console.print(t)

    total = len(outcomes)
    failed = [o for o in outcomes if not o.passed]
    fail_pct = (100 * len(failed) / total) if total else 0.0
    gate_ok = fail_pct <= max_fail_pct
    console.print(
        f"\nScenarios: {total} - failed: {len(failed)} ({fail_pct:.1f}%) - "
        f"gate <= {max_fail_pct}% -> {'PASS' if gate_ok else 'FAIL'}"
    )

    REPORT.mkdir(exist_ok=True)
    report = {
        "total": total,
        "failed": len(failed),
        "fail_pct": fail_pct,
        "max_fail_pct": max_fail_pct,
        "scenarios": [asdict(o) for o in outcomes],
    }
    (REPORT / "orchestrator-eval-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return gate_ok, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-fail-pct", type=float, default=0.0)
    parser.add_argument("--with-foundry", action="store_true")
    args = parser.parse_args()

    mode = os.environ.get("EVAL_MODE", "offline")
    base = os.environ.get("ORCHESTRATOR_URL")
    outcomes = run(mode, base, args.with_foundry)
    if not outcomes:
        print("No scenarios under evals/orch_scenarios/.", file=sys.stderr)
        return 1
    passed, _ = render(outcomes, args.max_fail_pct)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
