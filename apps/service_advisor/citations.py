"""Shared Pydantic models for the cited-tool-response contract.

Mirrors apps/log_analyst/citations.py. Both services duplicate the file so each
remains independently buildable (one Docker context per service per
azure.yaml). The two copies MUST stay shape-compatible — the orchestrator's
``ToolRegistry`` treats every specialist response identically.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

CitationType = Literal["log", "runbook", "incident"]


class Citation(BaseModel):
    type: CitationType
    id: str
    snippet: str = ""


class ToolResponse(BaseModel):
    tool: str
    result: dict[str, Any]
    citations: list[Citation] = Field(default_factory=list)
    trace_id: str
    warnings: list[str] | None = None

    def finalize(self) -> ToolResponse:
        if not self.citations and not self.warnings:
            self.warnings = ["uncited"]
        return self


class ToolDescriptor(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
