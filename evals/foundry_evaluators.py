"""Foundry-hosted evaluator wrapper.

Lazy-imports `azure-ai-evaluation` so the offline gate keeps running without
the extra dependency. Use `--with-foundry` on the eval runner to engage these.

Each wrapper returns a score on a 1..5 scale (Foundry's standard) and a short
reason. Failure to load the SDK or run an evaluator does NOT raise — it
returns ``score=None`` with the error in ``reason``.

Required env when enabled:

    AZURE_AI_FOUNDRY_PROJECT_ENDPOINT    (or AZURE_OPENAI_ENDPOINT)
    AZURE_OPENAI_CHAT_DEPLOYMENT          (judge model, default ``gpt-4o``)

The wrapper is intentionally tiny — the heavy lifting lives in
``azure-ai-evaluation``. Install with:

    pip install "azure-ai-evaluation>=1.0.0"
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

PASS_BAR = 3.0
SUPPORTED = ("groundedness", "relevance", "coherence", "retrieval")


@dataclass
class EvalScore:
    name: str
    score: float | None
    reason: str = ""

    @property
    def ok(self) -> bool:
        return self.score is not None and self.score >= PASS_BAR


def _judge_config() -> dict[str, str] | None:
    endpoint = (
        os.environ.get("AZURE_OPENAI_ENDPOINT")
        or os.environ.get("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
    )
    deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
    if not endpoint:
        return None
    return {
        "azure_endpoint": endpoint,
        "azure_deployment": deployment,
        "api_version": "2024-08-01-preview",
    }


def _try_import() -> dict[str, Any] | None:
    try:
        from azure.ai.evaluation import (  # type: ignore[import-not-found]
            CoherenceEvaluator,
            GroundednessEvaluator,
            RelevanceEvaluator,
            RetrievalEvaluator,
        )
    except Exception:  # noqa: BLE001
        return None
    return {
        "groundedness": GroundednessEvaluator,
        "relevance": RelevanceEvaluator,
        "coherence": CoherenceEvaluator,
        "retrieval": RetrievalEvaluator,
    }


def run_foundry_evaluators(
    *,
    query: str,
    response: str,
    context: str,
    evaluators: list[str] | None = None,
) -> list[EvalScore]:
    """Run a fixed bundle of Foundry evaluators on one turn.

    ``context`` should be a concatenation of cited snippets — this is what
    ``groundedness`` and ``retrieval`` are checked against.
    """
    names = evaluators or list(SUPPORTED)
    cls_map = _try_import()
    if cls_map is None:
        return [
            EvalScore(name=n, score=None, reason="azure-ai-evaluation not installed")
            for n in names
        ]
    cfg = _judge_config()
    if cfg is None:
        return [
            EvalScore(name=n, score=None, reason="AZURE_OPENAI_ENDPOINT not set")
            for n in names
        ]

    results: list[EvalScore] = []
    for name in names:
        ev_cls = cls_map.get(name)
        if ev_cls is None:
            results.append(EvalScore(name=name, score=None, reason="unknown evaluator"))
            continue
        try:
            ev = ev_cls(model_config=cfg)
            raw = ev(query=query, response=response, context=context)
            score_raw = raw.get(name)
            if score_raw is None:
                score_raw = raw.get(f"{name}_score")
            score = float(score_raw) if score_raw is not None else None
            results.append(
                EvalScore(
                    name=name,
                    score=score,
                    reason=str(raw.get("reason", ""))[:200],
                )
            )
        except Exception as e:  # noqa: BLE001
            results.append(EvalScore(name=name, score=None, reason=f"{type(e).__name__}: {e}"))
    return results
