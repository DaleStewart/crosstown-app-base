"""Eval runner — citation-gated for the Log Analyst.

Usage:
    python -m runner --max-uncited-pct 5
    EVAL_MODE=live LOG_ANALYST_URL=https://... python -m runner

Reads YAML scenarios from ./scenarios, plays them either offline (cassettes)
or live (real HTTP), and asserts the citation gate.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import yaml
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parent
SCENARIOS = ROOT / "scenarios"
CASSETTES = ROOT / "cassettes"
REPORT = ROOT / ".report"


@dataclass
class ToolCallResult:
    name: str
    args: dict[str, Any]
    response: dict[str, Any]


@dataclass
class ScenarioOutcome:
    scenario_id: str
    title: str
    turns: int
    uncited_turns: int
    missing_expected_tools: list[str] = field(default_factory=list)
    missing_citation_types: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.uncited_turns == 0
            and not self.missing_expected_tools
            and not self.missing_citation_types
            and not self.errors
        )


def load_scenarios() -> list[dict[str, Any]]:
    return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(SCENARIOS.glob("*.yaml"))]


def load_cassette(scenario_id: str) -> dict[str, Any] | None:
    path = CASSETTES / f"{scenario_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def args_contains(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    for k, v in expected.items():
        if v == "any":
            if k not in actual:
                return False
            continue
        if actual.get(k) != v:
            return False
    return True


def dispatch_offline(cassette: dict[str, Any], tool: str, args: dict[str, Any]) -> dict[str, Any]:
    for entry in cassette.get("calls", []):
        if entry["tool"] == tool and args_contains(args, entry.get("args_contains", {})):
            return entry["response"]
    return {
        "tool": tool,
        "result": {},
        "citations": [],
        "warnings": ["uncited", "no_cassette_match"],
    }


def dispatch_live(base_url: str, tool: str, args: dict[str, Any]) -> dict[str, Any]:
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        r = client.post(f"/tools/{tool}", json=args)
        r.raise_for_status()
        return r.json()


def run_scenario(scn: dict[str, Any], mode: str, base_url: str | None) -> ScenarioOutcome:
    out = ScenarioOutcome(scenario_id=scn["id"], title=scn["title"], turns=0, uncited_turns=0)
    cassette = load_cassette(scn["id"]) if mode == "offline" else None
    if mode == "offline" and cassette is None:
        out.errors.append("no cassette")
        return out

    seen_tools: set[str] = set()
    seen_citation_types: set[str] = set()

    for expected in scn.get("expected_tools", []):
        tool = expected["name"]
        args = expected.get("args_contains", {})
        try:
            if mode == "offline":
                resp = dispatch_offline(cassette or {}, tool, args)
            else:
                if not base_url:
                    raise RuntimeError("LOG_ANALYST_URL not set for live mode")
                resp = dispatch_live(base_url, tool, args)
        except Exception as e:  # noqa: BLE001
            out.errors.append(f"{tool}: {e}")
            continue
        out.turns += 1
        seen_tools.add(tool)
        citations = resp.get("citations") or []
        warnings = resp.get("warnings") or []
        if not citations and "uncited" not in warnings:
            out.uncited_turns += 1
        for c in citations:
            seen_citation_types.add(c.get("type", "?"))

    expected_tool_names = {e["name"] for e in scn.get("expected_tools", [])}
    out.missing_expected_tools = sorted(expected_tool_names - seen_tools)

    must_cite_types = {c["type"] for c in scn.get("must_cite", [])}
    out.missing_citation_types = sorted(must_cite_types - seen_citation_types)
    return out


def render_report(outcomes: list[ScenarioOutcome], max_uncited_pct: float) -> tuple[bool, dict[str, Any]]:
    total_turns = sum(o.turns for o in outcomes)
    total_uncited = sum(o.uncited_turns for o in outcomes)
    pct = (100 * total_uncited / total_turns) if total_turns else 0.0
    citation_ok = pct <= max_uncited_pct
    all_pass = all(o.passed for o in outcomes) and citation_ok

    console = Console(force_terminal=True, legacy_windows=False)
    t = Table(title="Eval Results")
    t.add_column("Scenario")
    t.add_column("Turns")
    t.add_column("Uncited")
    t.add_column("Missing tools")
    t.add_column("Missing cite types")
    t.add_column("Errors")
    t.add_column("Pass")
    for o in outcomes:
        t.add_row(
            f"{o.scenario_id} {o.title[:40]}",
            str(o.turns),
            str(o.uncited_turns),
            ", ".join(o.missing_expected_tools) or "-",
            ", ".join(o.missing_citation_types) or "-",
            ", ".join(o.errors) or "-",
            "PASS" if o.passed else "FAIL",
        )
    console.print(t)
    console.print(
        f"\nTotal turns: {total_turns} - uncited: {total_uncited} "
        f"({pct:.1f}%) - gate <= {max_uncited_pct}% -> {'PASS' if citation_ok else 'FAIL'}"
    )

    REPORT.mkdir(exist_ok=True)
    report = {
        "total_turns": total_turns,
        "uncited_turns": total_uncited,
        "uncited_pct": pct,
        "max_uncited_pct": max_uncited_pct,
        "citation_gate": "pass" if citation_ok else "fail",
        "scenarios": [
            {
                "id": o.scenario_id,
                "title": o.title,
                "passed": o.passed,
                "turns": o.turns,
                "uncited_turns": o.uncited_turns,
                "missing_expected_tools": o.missing_expected_tools,
                "missing_citation_types": o.missing_citation_types,
                "errors": o.errors,
            }
            for o in outcomes
        ],
    }
    (REPORT / "eval-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return all_pass, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-uncited-pct", type=float, default=5.0)
    args = parser.parse_args()

    mode = os.environ.get("EVAL_MODE", "offline")
    base_url = os.environ.get("LOG_ANALYST_URL")
    scenarios = load_scenarios()
    if not scenarios:
        print("No scenarios found under evals/scenarios/.", file=sys.stderr)
        return 1
    outcomes = [run_scenario(s, mode, base_url) for s in scenarios]
    all_pass, _report = render_report(outcomes, args.max_uncited_pct)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
