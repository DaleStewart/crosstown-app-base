"""Loads disruption records, runbooks, and the route graph from the bundled
``data/`` directory.

Lookups are O(1) over an in-memory index built at import time. The service is
stateless on disruption status — re-deploy the container to publish a new
``DSR-*`` record.
"""
from __future__ import annotations

import json
from functools import cache, lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_json(path: Path) -> dict[str, Any]:
    obj: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"expected object in {path}")
    return obj


@lru_cache(maxsize=1)
def load_disruptions() -> dict[str, dict[str, Any]]:
    """Return disruption records keyed by disruption_id."""
    out: dict[str, dict[str, Any]] = {}
    for p in sorted((DATA_DIR / "disruptions").glob("*.json")):
        doc = _load_json(p)
        did = str(doc.get("disruption_id", ""))
        if did:
            out[did] = doc
    return out


@lru_cache(maxsize=1)
def load_route_graph() -> dict[str, Any]:
    return _load_json(DATA_DIR / "route_graph.json")


@cache
def runbook_snippet(runbook_id: str) -> str:
    """Return a short snippet (first non-comment, non-heading line) from a runbook."""
    path = DATA_DIR / "runbooks" / f"{runbook_id}.md"
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("<!--") or s.startswith("#") or s.startswith("_"):
            continue
        return s[:160]
    return ""


def active_disruption_for_line(line: str) -> dict[str, Any] | None:
    """First active disruption whose ``line`` matches (case-insensitive)."""
    line_u = line.upper()
    for doc in load_disruptions().values():
        if str(doc.get("line", "")).upper() == line_u and doc.get("status") == "active":
            return doc
    return None


def reset_cache() -> None:
    """Clear cached singletons. Used by tests."""
    load_disruptions.cache_clear()
    load_route_graph.cache_clear()
    runbook_snippet.cache_clear()
