"""
MCP Server for University Support - Lab 07 Solution

This module implements a Model Context Protocol (MCP) server that exposes
university support tools to AI assistants. MCP is an open protocol that
enables AI models to access external tools and data sources in a standardized way.

Key Concepts:
- MCP Server: Provides tools and resources that AI models can use
- Tools: Functions that the AI can call to perform actions or retrieve data
- Resources: Data sources (like files or APIs) that the AI can read
- Prompts: Pre-defined prompt templates for common tasks

This server integrates with previous labs:
- Lab 04: SearchTool for knowledge base queries (RAG)
- Lab 05: AgentPipeline for orchestrated query handling

Architecture:
    AI Assistant (Claude, etc.)
           |
           v
    MCP Protocol (JSON-RPC over stdio)
           |
           v
    This MCP Server
           |
    +------+------+------+------+
    |      |      |      |      |
    v      v      v      v      v
  Query  Search  Dept   Ticket  KB
  Agent  Tool   Hours  Create  Search

How to Run:
    # Direct execution (for testing)
    python mcp_server.py

    # Via MCP (recommended)
    # Add to your VS Code settings or Claude Desktop config (see bottom of file)

Requirements:
    pip install mcp pydantic python-dotenv

Environment Variables (in .env file or system environment):
    AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
    AZURE_OPENAI_KEY=your-api-key
    AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
    AZURE_SEARCH_KEY=your-search-key
    AZURE_SEARCH_INDEX=your-index-name
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# -----------------------------------------------------------------------------
# MCP SDK imports
# -----------------------------------------------------------------------------
# The MCP SDK provides the protocol implementation and server framework.
# We use the FastMCP helper which simplifies server creation.
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
    # dotenv is optional - environment variables can be set directly
    pass

# -----------------------------------------------------------------------------
# Path setup for importing from other labs
# -----------------------------------------------------------------------------
# We need to add the solution directories for Lab 04 and Lab 05 to the Python
# path so we can import their components. In production, you'd use proper
# package management instead.

# Get the labs directory (parent of parent of this file)
LABS_DIR = Path(__file__).parent.parent.parent
SHARED_DIR = LABS_DIR.parent / "shared"
LAB04_SOLUTION = LABS_DIR / "04-build-rag-pipeline" / "solution"
LAB05_SOLUTION = LABS_DIR / "05-agent-orchestration" / "solution"

# Add to path for imports
sys.path.insert(0, str(LAB04_SOLUTION))
sys.path.insert(0, str(LAB05_SOLUTION))

# Path to department routing configuration
DEPARTMENT_ROUTING_PATH = SHARED_DIR / "department_routing.json"


# -----------------------------------------------------------------------------
# Configure logging
# -----------------------------------------------------------------------------
# MCP servers often run as subprocesses, so logging to stderr is preferred
# to avoid interfering with the JSON-RPC communication on stdout.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Important: MCP uses stdout for JSON-RPC
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Lazy imports for lab components
# -----------------------------------------------------------------------------
# These modules may not be available during initial setup, so we use lazy
# loading with fallback behavior. This allows the server to start even if
# some dependencies are missing.

_search_tool = None
_agent_pipeline = None


def get_search_tool():
    """
    Lazily initialize and return the SearchTool from Lab 04.

    Lazy loading is used because:
    1. The tool requires Azure credentials that may not be set
    2. Initialization can fail if Lab 04 isn't completed
    3. We want the server to start even if search is unavailable

    Returns:
        SearchTool instance or None if unavailable
    """
    global _search_tool

    if _search_tool is not None:
        return _search_tool

    try:
        # Import the SearchTool from Lab 04
        from search_tool import SearchTool

        # Initialize with environment variables
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
    """
    Lazily initialize and return the AgentPipeline from Lab 05.

    The pipeline orchestrates multiple agents to handle complex queries.
    We cache it to reuse session state across calls.

    Returns:
        AgentPipeline instance or None if unavailable
    """
    global _agent_pipeline

    if _agent_pipeline is not None:
        return _agent_pipeline

    try:
        # Import the AgentPipeline from Lab 05
        from pipeline import AgentPipeline

        # Initialize with environment variables
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
    """
    Load the department routing configuration from JSON file.

    This file contains department information including:
    - Business hours
    - Contact information
    - Keywords for routing
    - Escalation triggers

    Returns:
        Dictionary with routing configuration or None if file not found
    """
    try:
        if DEPARTMENT_ROUTING_PATH.exists():
            with open(DEPARTMENT_ROUTING_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Department routing file not found: {DEPARTMENT_ROUTING_PATH}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in department routing file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading department routing: {e}")
        return None


# -----------------------------------------------------------------------------
# Create the MCP Server
# -----------------------------------------------------------------------------
# FastMCP is a high-level helper that simplifies creating MCP servers.
# It handles:
# - JSON-RPC protocol implementation
# - Tool registration and discovery
# - Error handling and response formatting
# - Async execution

mcp = FastMCP(
    name="university-support-server",
    version="1.0.0",
    description="MCP server providing university student support tools"
)


# =============================================================================
# Tool 1: university_support_query
# =============================================================================
# This tool calls the full AgentPipeline from Lab 05, which orchestrates
# multiple agents (QueryAgent, RouterAgent, ActionAgents) to handle queries.

@mcp.tool()
async def university_support_query(
    query: str,
    session_id: Optional[str] = None
) -> str:
    """
    Process a student support query using the AI agent pipeline.

    This tool sends the query through a multi-agent orchestration pipeline
    that understands intent, routes to the appropriate handler, and generates
    a helpful response with citations when applicable.

    Use this for general student questions about:
    - University policies and procedures
    - Course registration and enrollment
    - Financial aid and scholarships
    - Housing and campus services
    - Technical support (passwords, email, etc.)

    Args:
        query: The student's question or request in natural language.
               Example: "How do I reset my university email password?"
        session_id: Optional session ID to maintain conversation context.
                   Pass the session_id from a previous response to continue
                   the same conversation.

    Returns:
        A formatted string containing:
        - The agent's response to the query
        - Session ID for continuing the conversation
        - Confidence score and metadata

    Example:
        >>> result = await university_support_query("What are the library hours?")
        >>> print(result)
        Response: The main library is open Monday-Friday 7am-midnight...
        Session ID: abc-123-def-456
        Confidence: 0.85
    """
    logger.info(f"Processing support query: {query[:50]}...")

    # Get the agent pipeline (lazy initialization)
    pipeline = get_agent_pipeline()

    if pipeline is None:
        # Fallback response when pipeline is unavailable
        # This could happen if Lab 05 isn't complete or Azure credentials are missing
        return json.dumps({
            "error": "Agent pipeline not available",
            "message": "The AI support system is currently unavailable. "
                      "Please try again later or contact support directly.",
            "fallback": True
        }, indent=2)

    try:
        # Process the query through the full pipeline
        # The pipeline handles:
        # 1. Intent classification (QueryAgent)
        # 2. Routing decision (RouterAgent)
        # 3. Response generation (ActionAgent)
        result, new_session_id = await pipeline.process(
            user_message=query,
            session_id=session_id
        )

        # Format the response for the MCP client
        # We include metadata to help the AI assistant understand the context
        response = {
            "response": result.content,
            "session_id": new_session_id,
            "confidence": result.confidence,
            "requires_followup": result.requires_followup,
            "suggested_actions": result.suggested_actions,
        }

        # Include sources if available (from RAG queries)
        if result.sources:
            response["sources"] = [
                {
                    "title": source.get("title", "Unknown"),
                    "preview": source.get("content_preview", "")[:100] + "..."
                }
                for source in result.sources
            ]

        # Include metadata for debugging/logging
        if result.metadata:
            response["metadata"] = result.metadata

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
# This tool provides department information including business hours.
# It's useful for helping students know when and how to contact departments.

@mcp.tool()
async def check_department_hours(department_id: str) -> str:
    """
    Get information about a university department including business hours.

    Returns comprehensive department information including:
    - Department name and contact details (email, phone)
    - Business hours for each day of the week
    - Keywords and categories the department handles

    Available department IDs:
    - financial_aid: Financial Aid Office
    - registration: Office of the Registrar
    - housing: Housing & Residence Life
    - it_support: IT Help Desk
    - academic_advising: Academic Advising Center
    - student_accounts: Student Financial Services

    Args:
        department_id: The department identifier (e.g., "financial_aid", "it_support").
                      Use lowercase with underscores.

    Returns:
        JSON string with department information including:
        - name: Full department name
        - email: Department email address
        - phone: Department phone number
        - business_hours: Hours for each day of the week
        - timezone: Department's timezone
        - categories: Types of issues this department handles

    Example:
        >>> result = await check_department_hours("it_support")
        >>> print(result)
        {
          "name": "IT Help Desk",
          "email": "helpdesk@university.edu",
          "phone": "555-123-4004",
          "business_hours": { ... },
          ...
        }
    """
    logger.info(f"Checking hours for department: {department_id}")

    # Load the department routing configuration
    routing_data = load_department_routing()

    if routing_data is None:
        return json.dumps({
            "error": "Department information unavailable",
            "message": "Unable to load department data. Please contact the main "
                      "university switchboard at 555-123-4000."
        }, indent=2)

    # Find the requested department
    departments = routing_data.get("departments", [])
    department = None

    for dept in departments:
        if dept.get("id") == department_id:
            department = dept
            break

    if department is None:
        # Department not found - provide helpful error with available options
        available_depts = [d.get("id") for d in departments]
        return json.dumps({
            "error": "Department not found",
            "message": f"Unknown department ID: '{department_id}'",
            "available_departments": available_depts,
            "hint": "Use one of the available department IDs listed above"
        }, indent=2)

    # Check if department is currently open
    # This helps the AI provide context about availability
    is_open, current_hours = _check_if_open(department.get("business_hours", {}))

    # Build the response with all relevant information
    response = {
        "department_id": department_id,
        "name": department.get("name"),
        "email": department.get("email"),
        "phone": department.get("phone"),
        "business_hours": department.get("business_hours"),
        "timezone": department.get("timezone"),
        "categories": department.get("categories", []),
        "keywords": department.get("keywords", []),
        "currently_open": is_open,
    }

    if current_hours:
        response["today_hours"] = current_hours

    return json.dumps(response, indent=2)


def _check_if_open(business_hours: dict) -> tuple[bool, Optional[dict]]:
    """
    Check if a department is currently open based on business hours.

    This is a helper function that determines current availability.
    In production, you'd want to handle timezones properly.

    Args:
        business_hours: Dictionary with day names and open/close times

    Returns:
        Tuple of (is_open: bool, today_hours: dict or None)
    """
    try:
        # Get current day and time
        now = datetime.now()
        day_name = now.strftime("%A").lower()  # e.g., "monday"

        today_hours = business_hours.get(day_name)
        if not today_hours:
            return False, None

        open_time = today_hours.get("open")
        close_time = today_hours.get("close")

        if not open_time or not close_time:
            # Closed today (null hours)
            return False, {"status": "closed", "day": day_name}

        # Parse times and check if currently within hours
        # Note: This is a simplified check that doesn't handle timezones
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
# This tool creates support tickets for issues that need human follow-up.
# In a boot camp context, we generate mock ticket IDs.

@mcp.tool()
async def create_support_ticket(
    title: str,
    description: str,
    department: str = "general",
    priority: str = "medium",
    student_email: Optional[str] = None,
    student_id: Optional[str] = None
) -> str:
    """
    Create a support ticket for issues requiring human follow-up.

    Use this when:
    - A student's issue cannot be resolved by the AI
    - The student explicitly requests human support
    - Complex issues require investigation
    - Follow-up or callback is needed

    Priority levels:
    - low: General inquiries, can wait 2-3 business days
    - medium: Standard issues, 1-2 business day response
    - high: Urgent matters, same-day response
    - critical: Emergencies requiring immediate attention

    Args:
        title: Brief summary of the issue (max 100 characters).
               Example: "Unable to register for Fall semester courses"
        description: Detailed description of the problem including:
                    - What the student is trying to do
                    - What error or issue they encountered
                    - Steps they've already tried
        department: Department to route the ticket to. Options:
                   financial_aid, registration, housing, it_support,
                   academic_advising, student_accounts, general
        priority: Urgency level - low, medium, high, or critical
        student_email: Student's email for follow-up (optional but recommended)
        student_id: Student's university ID number (optional)

    Returns:
        JSON string with ticket information including:
        - ticket_id: Unique ticket identifier (format: TKT-XXXXXXXX)
        - status: Initial ticket status
        - estimated_response: Expected response timeframe
        - tracking_url: URL to check ticket status

    Example:
        >>> result = await create_support_ticket(
        ...     title="Cannot access Canvas LMS",
        ...     description="Getting 403 error when trying to view course materials",
        ...     department="it_support",
        ...     priority="high",
        ...     student_email="student@university.edu"
        ... )
    """
    logger.info(f"Creating support ticket: {title}")

    # Validate priority level
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority.lower() not in valid_priorities:
        priority = "medium"
        logger.warning(f"Invalid priority, defaulting to medium")

    # Generate a unique ticket ID
    # In production, this would come from a ticketing system API
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"

    # Determine estimated response time based on priority
    response_times = {
        "low": "2-3 business days",
        "medium": "1-2 business days",
        "high": "Same business day",
        "critical": "Within 2 hours"
    }

    # Build the ticket record
    # In production, this would be saved to a database
    ticket = {
        "ticket_id": ticket_id,
        "title": title[:100],  # Truncate if too long
        "description": description,
        "department": department,
        "priority": priority.lower(),
        "status": "open",
        "created_at": datetime.now().isoformat() + "Z",
        "estimated_response": response_times.get(priority.lower(), "2-3 business days"),
    }

    # Add optional fields if provided
    if student_email:
        ticket["student_email"] = student_email
        ticket["notification_sent"] = True

    if student_id:
        ticket["student_id"] = student_id

    # Add tracking URL (mock URL for boot camp)
    ticket["tracking_url"] = f"https://support.university.edu/tickets/{ticket_id}"

    # Log the ticket creation (in production, save to database)
    logger.info(f"Created ticket {ticket_id} - Priority: {priority}, Dept: {department}")

    # Build response message
    response = {
        "success": True,
        "ticket": ticket,
        "message": f"Your support ticket has been created successfully. "
                  f"A member of the {department.replace('_', ' ').title()} team "
                  f"will respond within {ticket['estimated_response']}.",
        "next_steps": [
            f"Save your ticket ID: {ticket_id}",
            "Check your email for confirmation (if email provided)",
            f"Track status at: {ticket['tracking_url']}"
        ]
    }

    return json.dumps(response, indent=2)


# =============================================================================
# Tool 4: search_knowledge_base
# =============================================================================
# This tool directly uses the SearchTool from Lab 04 for RAG queries.
# It's useful when you want just the search results without the full
# agent pipeline processing.

@mcp.tool()
async def search_knowledge_base(
    query: str,
    top_k: int = 5,
    use_hybrid: bool = True
) -> str:
    """
    Search the university knowledge base for relevant information.

    This tool performs a hybrid search (combining semantic and keyword search)
    against the indexed university documents. Use this for:
    - Finding specific policies or procedures
    - Looking up official information
    - Getting source documents to cite

    The search uses Azure AI Search with:
    - Vector search: Finds semantically similar content
    - Keyword search: Matches exact terms and phrases
    - Hybrid ranking: Combines both for best results

    Args:
        query: Natural language search query.
               Example: "What is the deadline for adding courses?"
        top_k: Maximum number of results to return (1-20, default 5).
               Higher values give more comprehensive results but may
               include less relevant documents.
        use_hybrid: Whether to use hybrid search (default True).
                   Set to False for vector-only search, which may
                   work better for conceptual queries.

    Returns:
        JSON string with search results including:
        - results: Array of matching documents with content and metadata
        - query: The original search query
        - result_count: Number of results returned

        Each result contains:
        - content: The relevant text passage
        - score: Relevance score (higher is better)
        - metadata: Source information (document title, page, etc.)

    Example:
        >>> result = await search_knowledge_base("tuition payment deadline")
        >>> data = json.loads(result)
        >>> for doc in data["results"]:
        ...     print(f"Score: {doc['score']:.2f}")
        ...     print(f"Content: {doc['content'][:200]}...")
    """
    logger.info(f"Searching knowledge base: {query[:50]}...")

    # Validate top_k parameter
    top_k = max(1, min(20, top_k))  # Clamp between 1 and 20

    # Get the search tool (lazy initialization)
    search_tool = get_search_tool()

    if search_tool is None:
        return json.dumps({
            "error": "Knowledge base search unavailable",
            "message": "The search system is currently unavailable. "
                      "This may be because Azure AI Search is not configured. "
                      "Please try the university_support_query tool instead.",
            "fallback_suggestion": "Use university_support_query for general questions"
        }, indent=2)

    try:
        # Perform the search using Lab 04's SearchTool
        results = search_tool.search(
            query=query,
            top_k=top_k,
            use_hybrid=use_hybrid
        )

        # Format results for the response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.content,
                "score": result.score,
                "metadata": result.metadata
            })

        response = {
            "query": query,
            "result_count": len(formatted_results),
            "search_type": "hybrid" if use_hybrid else "vector",
            "results": formatted_results
        }

        # Add helpful context if no results found
        if not formatted_results:
            response["message"] = "No matching documents found. Try rephrasing your query or using different keywords."
            response["suggestions"] = [
                "Use more general terms",
                "Check spelling of specific terms",
                "Try breaking complex queries into simpler ones"
            ]

        return json.dumps(response, indent=2)

    except Exception as e:
        logger.exception(f"Search error: {e}")
        return json.dumps({
            "error": str(e),
            "message": "An error occurred while searching. Please try again.",
            "query": query
        }, indent=2)


# =============================================================================
# Additional Resource: List Available Departments
# =============================================================================
# MCP also supports "resources" - data that can be read but not actively
# queried. This provides a list of all departments for reference.

@mcp.tool()
async def list_departments() -> str:
    """
    List all available university departments and their IDs.

    Use this to discover which departments are available before calling
    check_department_hours or create_support_ticket.

    Returns:
        JSON string with an array of departments, each containing:
        - id: Department identifier for use in other tools
        - name: Human-readable department name
        - email: Department contact email
        - handles: Brief description of what the department handles

    Example:
        >>> result = await list_departments()
        >>> data = json.loads(result)
        >>> for dept in data["departments"]:
        ...     print(f"{dept['id']}: {dept['name']}")
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
            "handles": ", ".join(dept.get("categories", []))
        })

    return json.dumps({
        "department_count": len(departments),
        "departments": departments
    }, indent=2)


# =============================================================================
# Server Entry Point
# =============================================================================

def main():
    """
    Main entry point for the MCP server.

    This starts the server and listens for incoming connections.
    The server communicates over stdio using the MCP protocol.
    """
    logger.info("Starting University Support MCP Server...")
    logger.info(f"Lab 04 path: {LAB04_SOLUTION}")
    logger.info(f"Lab 05 path: {LAB05_SOLUTION}")
    logger.info(f"Shared data path: {SHARED_DIR}")

    # Run the MCP server
    # This blocks and handles incoming requests until shutdown
    mcp.run()


if __name__ == "__main__":
    main()


# =============================================================================
# VS Code / Claude Desktop Configuration
# =============================================================================
"""
To use this MCP server with VS Code or Claude Desktop, add the following
configuration:

## VS Code Settings (settings.json)

Add to your VS Code settings.json:

{
    "mcp.servers": {
        "university-support": {
            "command": "python",
            "args": ["c:/Users/segayle/repos/edu/47doors/labs/07-mcp-server/solution/mcp_server.py"],
            "env": {
                "AZURE_OPENAI_ENDPOINT": "https://your-openai.openai.azure.com/",
                "AZURE_OPENAI_KEY": "your-api-key",
                "AZURE_SEARCH_ENDPOINT": "https://your-search.search.windows.net",
                "AZURE_SEARCH_KEY": "your-search-key",
                "AZURE_SEARCH_INDEX": "your-index-name"
            }
        }
    }
}


## Claude Desktop Configuration (claude_desktop_config.json)

For Claude Desktop, add to your configuration file:

{
    "mcpServers": {
        "university-support": {
            "command": "python",
            "args": [
                "c:/Users/segayle/repos/edu/47doors/labs/07-mcp-server/solution/mcp_server.py"
            ],
            "env": {
                "AZURE_OPENAI_ENDPOINT": "https://your-openai.openai.azure.com/",
                "AZURE_OPENAI_KEY": "your-api-key",
                "AZURE_SEARCH_ENDPOINT": "https://your-search.search.windows.net",
                "AZURE_SEARCH_KEY": "your-search-key",
                "AZURE_SEARCH_INDEX": "university-kb"
            }
        }
    }
}


## Environment Variables

Alternatively, create a .env file in the solution directory:

# .env file
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-search-key-here
AZURE_SEARCH_INDEX=university-kb


## Testing the Server

To test the server standalone:

1. Set environment variables or create .env file
2. Run: python mcp_server.py
3. The server will start and wait for MCP protocol messages on stdin

For interactive testing, you can use the MCP Inspector:
    npx @modelcontextprotocol/inspector python mcp_server.py


## Available Tools

After connecting, the following tools are available:

1. university_support_query(query, session_id?)
   - Process queries through the full agent pipeline
   - Maintains conversation context with session_id

2. check_department_hours(department_id)
   - Get department contact info and business hours
   - Shows if department is currently open

3. create_support_ticket(title, description, department?, priority?, ...)
   - Create tickets for human follow-up
   - Returns ticket ID for tracking

4. search_knowledge_base(query, top_k?, use_hybrid?)
   - Direct RAG search against the knowledge base
   - Returns ranked document matches

5. list_departments()
   - List all available departments and their IDs
   - Useful for discovering available routing options
"""
