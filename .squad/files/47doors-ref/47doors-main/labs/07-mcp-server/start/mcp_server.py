"""
MCP Server for University Support System - Lab 07

This server exposes tools for interacting with the university support system,
including querying the support pipeline, checking department hours,
creating support tickets, and searching the knowledge base.

Key Concepts:
- MCP Server: Provides tools that AI assistants can invoke
- Tools: Functions the AI can call to perform actions or retrieve data
- Resources: Data sources (like files or APIs) the AI can read

How to Run:
    python mcp_server.py

    Or with MCP Inspector for testing:
    npx @modelcontextprotocol/inspector python mcp_server.py
"""

import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# -----------------------------------------------------------------------------
# MCP SDK imports
# -----------------------------------------------------------------------------
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Path setup for importing from other labs
# -----------------------------------------------------------------------------
LABS_DIR = Path(__file__).parent.parent.parent
SHARED_DIR = LABS_DIR.parent / "shared"
LAB04_SOLUTION = LABS_DIR / "04-build-rag-pipeline" / "solution"
LAB05_SOLUTION = LABS_DIR / "05-agent-orchestration" / "solution"

sys.path.insert(0, str(LAB04_SOLUTION))
sys.path.insert(0, str(LAB05_SOLUTION))

DEPARTMENT_ROUTING_PATH = SHARED_DIR / "department_routing.json"

# -----------------------------------------------------------------------------
# Configure logging (use stderr to avoid interfering with MCP protocol)
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Lazy initialization for lab components
# -----------------------------------------------------------------------------
_search_tool = None
_agent_pipeline = None


def get_search_tool():
    """Lazily initialize and return the SearchTool from Lab 04."""
    global _search_tool
    if _search_tool is not None:
        return _search_tool
    try:
        from search_tool import SearchTool
        _search_tool = SearchTool()
        logger.info("SearchTool initialized successfully")
        return _search_tool
    except ImportError as e:
        logger.warning(f"Lab 04 SearchTool not available: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize SearchTool: {e}")
        return None


def get_agent_pipeline():
    """Lazily initialize and return the AgentPipeline from Lab 05."""
    global _agent_pipeline
    if _agent_pipeline is not None:
        return _agent_pipeline
    try:
        from pipeline import AgentPipeline
        _agent_pipeline = AgentPipeline()
        logger.info("AgentPipeline initialized successfully")
        return _agent_pipeline
    except ImportError as e:
        logger.warning(f"Lab 05 AgentPipeline not available: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize AgentPipeline: {e}")
        return None


def load_department_routing() -> Optional[dict]:
    """Load the department routing configuration from JSON file."""
    try:
        if DEPARTMENT_ROUTING_PATH.exists():
            with open(DEPARTMENT_ROUTING_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Department routing file not found: {DEPARTMENT_ROUTING_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error loading department routing: {e}")
        return None


# -----------------------------------------------------------------------------
# Create the MCP Server
# -----------------------------------------------------------------------------
mcp = FastMCP(
    name="university-support",
    instructions="MCP server providing university student support tools. "
                 "Use these tools to help students with support queries, "
                 "department information, support tickets, and knowledge base searches."
)


# =============================================================================
# Tool 1: university_support_query
# =============================================================================
@mcp.tool()
async def university_support_query(
    query: str,
    session_id: Optional[str] = None
) -> str:
    """
    Process a university support query through the full agent pipeline.

    This tool routes queries to the AgentPipeline for comprehensive handling,
    including intent classification, department routing, and response generation.

    Args:
        query: The user's support question or request
        session_id: Optional session identifier for conversation continuity

    Returns:
        The agent pipeline's response to the query
    """
    logger.info(f"Processing support query: {query[:50]}...")

    pipeline = get_agent_pipeline()

    if pipeline is None:
        # Fallback when pipeline is unavailable
        return json.dumps({
            "error": "Agent pipeline not available",
            "message": "The AI support system is currently unavailable. "
                      "Please try again later or contact support directly.",
            "fallback": True
        }, indent=2)

    try:
        result, new_session_id = await pipeline.process(
            user_message=query,
            session_id=session_id
        )

        response = {
            "response": result.content,
            "session_id": new_session_id,
            "confidence": result.confidence,
            "requires_followup": result.requires_followup,
            "suggested_actions": result.suggested_actions,
        }

        if result.sources:
            response["sources"] = [
                {
                    "title": source.get("title", "Unknown"),
                    "preview": source.get("content_preview", "")[:100] + "..."
                }
                for source in result.sources
            ]

        return json.dumps(response, indent=2)

    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        return json.dumps({
            "error": str(e),
            "message": "An error occurred while processing your request. "
                      "Please try again or rephrase your question.",
        }, indent=2)


# =============================================================================
# Tool 2: check_department_hours
# =============================================================================
@mcp.tool()
async def check_department_hours(department: str) -> dict:
    """
    Get information about a specific university department.

    Retrieves department details including name, operating hours,
    and contact information.

    Available department IDs:
    - financial_aid: Financial Aid Office
    - registration: Office of the Registrar
    - housing: Housing & Residence Life
    - it_support: IT Help Desk
    - academic_advising: Academic Advising Center
    - student_accounts: Student Financial Services

    Args:
        department: The name/ID of the department to look up
                   (e.g., "financial_aid", "it_support")

    Returns:
        Dictionary containing department info including hours and contact
    """
    logger.info(f"Checking hours for department: {department}")

    routing_data = load_department_routing()

    if routing_data is None:
        return {
            "error": "Department information unavailable",
            "message": "Unable to load department data. Please contact the main "
                      "university switchboard at 555-123-4000."
        }

    departments = routing_data.get("departments", [])
    dept_info = None

    # Find the requested department (case-insensitive)
    department_lower = department.lower().replace(" ", "_")
    for dept in departments:
        if dept.get("id") == department_lower or dept.get("name", "").lower() == department.lower():
            dept_info = dept
            break

    if dept_info is None:
        available_depts = [d.get("id") for d in departments]
        return {
            "error": "Department not found",
            "message": f"Unknown department: '{department}'",
            "available_departments": available_depts,
            "hint": "Use one of the available department IDs listed above"
        }

    # Check if currently open
    is_open, today_hours = _check_if_open(dept_info.get("business_hours", {}))

    return {
        "name": dept_info.get("name"),
        "hours": dept_info.get("business_hours"),
        "contact": {
            "email": dept_info.get("email"),
            "phone": dept_info.get("phone")
        },
        "location": f"Main Campus - {dept_info.get('name')}",
        "timezone": dept_info.get("timezone"),
        "categories": dept_info.get("categories", []),
        "currently_open": is_open,
        "today_hours": today_hours
    }


def _check_if_open(business_hours: dict) -> tuple[bool, Optional[dict]]:
    """Check if a department is currently open based on business hours."""
    try:
        now = datetime.now()
        day_name = now.strftime("%A").lower()

        today_hours = business_hours.get(day_name)
        if not today_hours:
            return False, None

        open_time = today_hours.get("open")
        close_time = today_hours.get("close")

        if not open_time or not close_time:
            return False, {"status": "closed", "day": day_name}

        current_time = now.strftime("%H:%M")
        is_open = open_time <= current_time <= close_time

        return is_open, {
            "day": day_name,
            "open": open_time,
            "close": close_time,
            "current_time": current_time,
            "status": "open" if is_open else "closed"
        }
    except Exception as e:
        logger.warning(f"Error checking business hours: {e}")
        return False, None


# =============================================================================
# Tool 3: create_support_ticket
# =============================================================================
@mcp.tool()
async def create_support_ticket(
    issue_description: str,
    priority: str = "medium",
    department: Optional[str] = None,
    contact_email: Optional[str] = None
) -> dict:
    """
    Create a new support ticket in the system.

    Creates a ticket for issues that require follow-up from university staff.

    Priority levels:
    - low: General inquiries, 2-3 business days response
    - medium: Standard issues, 1-2 business days response
    - high: Urgent matters, same-day response
    - urgent/critical: Emergencies, within 2 hours

    Args:
        issue_description: Detailed description of the issue or request
        priority: Ticket priority level - "low", "medium", "high", or "urgent"
        department: Optional target department for the ticket
        contact_email: Optional email for ticket updates

    Returns:
        Dictionary containing ticket details including ID and status
    """
    logger.info(f"Creating support ticket: {issue_description[:50]}...")

    # Validate priority level
    valid_priorities = ["low", "medium", "high", "urgent", "critical"]
    if priority.lower() not in valid_priorities:
        priority = "medium"

    # Generate unique ticket ID
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"

    # Determine estimated response time
    response_times = {
        "low": "2-3 business days",
        "medium": "1-2 business days",
        "high": "Same business day",
        "urgent": "Within 2 hours",
        "critical": "Within 2 hours"
    }

    # Build the ticket
    ticket = {
        "ticket_id": ticket_id,
        "status": "open",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "estimated_response": response_times.get(priority.lower(), "2-3 business days"),
        "priority": priority.lower(),
        "department": department or "general",
        "description": issue_description
    }

    if contact_email:
        ticket["contact_email"] = contact_email
        ticket["notification_sent"] = True

    ticket["tracking_url"] = f"https://support.university.edu/tickets/{ticket_id}"

    logger.info(f"Created ticket {ticket_id} - Priority: {priority}")

    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": ticket["status"],
        "created_at": ticket["created_at"],
        "estimated_response": ticket["estimated_response"],
        "message": f"Your support ticket has been created successfully. "
                  f"A member of the {(department or 'general').replace('_', ' ').title()} team "
                  f"will respond within {ticket['estimated_response']}.",
        "next_steps": [
            f"Save your ticket ID: {ticket_id}",
            "Check your email for confirmation (if email provided)",
            f"Track status at: {ticket['tracking_url']}"
        ]
    }


# =============================================================================
# Tool 4: search_knowledge_base
# =============================================================================
@mcp.tool()
async def search_knowledge_base(
    query: str,
    department: Optional[str] = None,
    max_results: int = 5
) -> list[dict]:
    """
    Search the university knowledge base directly.

    Performs a semantic search across university documentation, FAQs,
    and support articles using Azure AI Search.

    Args:
        query: Search query text
        department: Optional department filter to narrow results
        max_results: Maximum number of results to return (default: 5)

    Returns:
        List of dictionaries containing matching documents with:
        - title: Document or article title
        - content: Relevant excerpt or summary
        - source: Source document reference
        - relevance_score: Search relevance score (0-1)
        - department: Associated department if applicable
    """
    logger.info(f"Searching knowledge base: {query[:50]}...")

    max_results = max(1, min(20, max_results))

    search_tool = get_search_tool()

    if search_tool is None:
        return [{
            "error": "Knowledge base search unavailable",
            "message": "The search system is currently unavailable. "
                      "This may be because Azure AI Search is not configured. "
                      "Please try the university_support_query tool instead.",
            "fallback_suggestion": "Use university_support_query for general questions"
        }]

    try:
        results = search_tool.search(
            query=query,
            top_k=max_results,
            use_hybrid=True
        )

        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.metadata.get("title", "Unknown"),
                "content": result.content[:500] + "..." if len(result.content) > 500 else result.content,
                "source": result.metadata.get("source", "Knowledge Base"),
                "relevance_score": result.score,
                "department": result.metadata.get("department", department or "general")
            })

        if not formatted_results:
            return [{
                "message": "No matching documents found.",
                "suggestions": [
                    "Use more general terms",
                    "Check spelling of specific terms",
                    "Try breaking complex queries into simpler ones"
                ]
            }]

        return formatted_results

    except Exception as e:
        logger.exception(f"Search error: {e}")
        return [{
            "error": str(e),
            "message": "An error occurred while searching. Please try again.",
            "query": query
        }]


# =============================================================================
# Bonus Tool: list_departments
# =============================================================================
@mcp.tool()
async def list_departments() -> str:
    """
    List all available university departments and their IDs.

    Use this to discover which departments are available before calling
    check_department_hours or create_support_ticket.

    Returns:
        JSON string with an array of departments
    """
    routing_data = load_department_routing()

    if routing_data is None:
        return json.dumps({
            "error": "Department list unavailable",
            "message": "Unable to load department information."
        }, indent=2)

    departments = []
    for dept in routing_data.get("departments", []):
        departments.append({
            "id": dept.get("id"),
            "name": dept.get("name"),
            "email": dept.get("email"),
            "phone": dept.get("phone"),
            "handles": ", ".join(dept.get("categories", []))
        })

    return json.dumps({
        "department_count": len(departments),
        "departments": departments
    }, indent=2)


# =============================================================================
# Server Entry Point
# =============================================================================
async def main() -> None:
    """
    Run the MCP server using stdio transport.
    """
    logger.info("Starting University Support MCP Server...")
    logger.info(f"Lab 04 path: {LAB04_SOLUTION}")
    logger.info(f"Lab 05 path: {LAB05_SOLUTION}")
    logger.info(f"Shared data path: {SHARED_DIR}")

    mcp.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
