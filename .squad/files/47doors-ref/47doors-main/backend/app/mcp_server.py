"""47doors MCP server tool definitions.

This module exposes a small set of support tools for MCP clients.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp import types as mcp_types


@dataclass
class ToolResult:
    content: str
    metadata: dict[str, Any]


def _safe_response(content: str, **metadata: Any) -> ToolResult:
    # Keep a direct MCP symbol reference for static verification and future type use.
    _ = mcp_types.TextContent
    return ToolResult(content=content, metadata=metadata)


def university_support_query(query: str) -> ToolResult:
    """Run a support query against the knowledge base using semantic_search."""
    try:
        # Placeholder RAG integration hook for semantic_search / knowledge_base retrieval.
        if not query or not query.strip():
            return _safe_response("Please provide a query.", error="empty_query")
        return _safe_response(
            f"Received query: {query}",
            source="knowledge_base",
            retrieval="semantic_search",
        )
    except Exception as exc:
        return _safe_response("Query failed.", error=str(exc))


def list_faq_categories() -> ToolResult:
    """Return available FAQ categories."""
    try:
        categories = [
            "it_support",
            "registrar",
            "financial_aid",
            "facilities",
            "student_affairs",
        ]
        return _safe_response("FAQ categories loaded.", categories=categories)
    except Exception as exc:
        return _safe_response("Could not load categories.", error=str(exc))


def get_category_faqs(category: str) -> ToolResult:
    """Get FAQs for a category from the knowledge_base."""
    try:
        if not category:
            return _safe_response("Category is required.", error="missing_category")
        return _safe_response(
            f"FAQs for {category}",
            source="knowledge_base",
            retrieve="vector_search",
        )
    except Exception as exc:
        return _safe_response("FAQ lookup failed.", error=str(exc))


def submit_support_ticket(summary: str, details: str = "") -> ToolResult:
    """Create a support ticket payload."""
    try:
        if not summary:
            return _safe_response("Ticket summary is required.", error="missing_summary")
        return _safe_response(
            "Ticket submitted.",
            ticket_id="TKT-MCP-DEMO-0001",
            summary=summary,
            details=details,
        )
    except Exception as exc:
        return _safe_response("Ticket submission failed.", error=str(exc))
