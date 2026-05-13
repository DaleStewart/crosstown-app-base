"""Pydantic models shared by every tool response."""
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
        """Add ``uncited`` warning when no citations were attached.

        ``warnings`` is left unchanged when it already contains entries (so a
        tool can attach domain-specific warnings such as ``no_patterns`` without
        getting overwritten).
        """
        if not self.citations and not self.warnings:
            self.warnings = ["uncited"]
        return self


class ToolDescriptor(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
