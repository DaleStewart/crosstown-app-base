# 🔌 Lab 07 - MCP Server (Stretch Goal)

| 📋 Attribute | Value |
|-------------|-------|
| ⏱️ **Duration** | 60 minutes |
| 📊 **Difficulty** | ⭐⭐⭐⭐ Expert |
| 🎯 **Prerequisites** | Lab 05 completed |
| 🏆 **Points** | 10 (bonus) |

---

> 🌟 **STRETCH GOAL**: This lab is for participants who finish Labs 01-06 early. Completing this lab is optional and will not affect your ability to pass the boot camp.

---

## 📈 Progress Tracker

```
Lab Progress: [░░░░░░░░░░] 0% - Not Started

Checkpoints:
□ Step 1: Install MCP Dependencies
□ Step 2: Create the MCP Server Module
□ Step 3: Create MCP Server Entry Point
□ Step 4: Configure VS Code for MCP
□ Step 5: Implement the 4 Required Tools
□ Step 6: Test with Copilot Agent Mode
```

---

## 🌟 Overview

Transform your 47 Doors FastAPI backend into a Model Context Protocol (MCP) server, enabling direct integration with AI assistants like GitHub Copilot in VS Code.

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

1. 📚 **Understand the MCP Tool/Resource Model** - Learn how AI assistants discover and invoke tools through MCP
2. 🔌 **Expose 47 Doors as an MCP Server** - Convert your existing FastAPI endpoints into MCP-compatible tools
3. 🧪 **Test with Copilot Agent Mode** - Use your MCP server directly from VS Code's Copilot chat

## 🤔 What is MCP (Model Context Protocol)?

The Model Context Protocol (MCP) is an open standard that defines how AI assistants communicate with external tools and data sources. Think of it as a universal adapter that lets any AI assistant use any tool, similar to how USB lets any device connect to any computer.

### 🔑 Key Concepts

| 📋 Concept | 📝 Description |
|-----------|-------------|
| 🔧 **Tools** | Functions that AI can invoke (e.g., `university_support_query`, `list_categories`) |
| 📚 **Resources** | Data sources that AI can read (e.g., FAQ database, ticket history) |
| 📝 **Prompts** | Pre-defined templates for common interactions |
| 🖥️ **Server** | Your application that exposes tools and resources via MCP |

### 🌟 Why MCP Matters

Without MCP, every AI assistant needs custom integrations for every tool. With MCP:
- ✍️ Write once, use everywhere (Copilot, Claude, ChatGPT, etc.)
- 🔒 Standardized security and authentication
- 🔍 AI can discover what tools are available and how to use them

## 📋 Prerequisites

Before starting this lab, ensure you have:

- [ ] ✅ Lab 05 completed with working RAG pipeline
- [ ] 🤖 VS Code with GitHub Copilot extension installed
- [ ] 🐍 Python 3.11+ environment active
- [ ] 🔧 FastAPI backend running locally

---

## 📝 Step-by-Step Instructions

### 🔹 Step 1: Install MCP Dependencies (5 minutes)

Add the MCP SDK to your project:

```bash
cd backend
pip install "mcp>=1.6.0"
```

Add to `requirements.txt`:
```
mcp>=1.6.0
```

### 🔹 Step 2: Create the MCP Server Module (15 minutes)

Create a new file `backend/app/mcp_server.py`:

```python
"""
🔌 MCP Server for 47 Doors University Support
Exposes RAG-powered support tools via Model Context Protocol
"""
import asyncio
from typing import Any
from mcp.server import Server
# InitializationOptions removed in MCP SDK 1.1+; server info is set via Server() constructor
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ResourceTemplate,
)

from app.services.rag_service import RAGService
from app.core.config import get_settings

# 🔌 Initialize MCP server
server = Server("47doors-university-support")

# 🔍 Initialize RAG service (reuse your existing implementation)
rag_service = None

async def get_rag_service():
    """Lazy initialization of RAG service."""
    global rag_service
    if rag_service is None:
        settings = get_settings()
        rag_service = RAGService(settings)
        await rag_service.initialize()
    return rag_service


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    📋 List available tools for the AI assistant.
    This is called when the AI needs to discover what tools are available.
    """
    return [
        Tool(
            name="university_support_query",
            description="🎓 Answer university support questions using the 47 Doors knowledge base. "
                       "Use this for questions about admissions, financial aid, housing, "
                       "registration, student services, and general university policies.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The student's question about university services or policies"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (admissions, financial_aid, housing, etc.)",
                        "enum": ["admissions", "financial_aid", "housing", "registration", "student_services", "general"]
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="list_faq_categories",
            description="📚 List all available FAQ categories in the knowledge base.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_category_faqs",
            description="🏷️ Get all FAQs for a specific category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The category to retrieve FAQs for"
                    }
                },
                "required": ["category"]
            }
        ),
        Tool(
            name="submit_support_ticket",
            description="🎫 Create a support ticket when the knowledge base cannot answer a question. "
                       "Use this as a fallback when university_support_query returns low confidence.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Brief summary of the issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the student's question or issue"
                    },
                    "student_email": {
                        "type": "string",
                        "description": "Student's email for follow-up"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Ticket priority level"
                    }
                },
                "required": ["subject", "description"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    ⚡ Handle tool invocation from the AI assistant.
    """
    rag = await get_rag_service()

    if name == "university_support_query":
        question = arguments["question"]
        category = arguments.get("category")

        # 🔍 Use your existing RAG pipeline
        result = await rag.query(question, category_filter=category)

        response_text = f"""## 💬 Answer

{result.answer}

## 📊 Confidence
{result.confidence:.0%}

## 📚 Sources
"""
        for source in result.sources:
            response_text += f"- {source.title} (relevance: {source.score:.0%})\n"

        return [TextContent(type="text", text=response_text)]

    elif name == "list_faq_categories":
        categories = await rag.get_categories()

        response_text = "## 📚 Available FAQ Categories\n\n"
        for cat in categories:
            response_text += f"- **{cat.name}**: {cat.description} ({cat.faq_count} FAQs)\n"

        return [TextContent(type="text", text=response_text)]

    elif name == "get_category_faqs":
        category = arguments["category"]
        faqs = await rag.get_faqs_by_category(category)

        response_text = f"## 🏷️ FAQs in {category}\n\n"
        for faq in faqs:
            response_text += f"### {faq.question}\n{faq.answer}\n\n"

        return [TextContent(type="text", text=response_text)]

    elif name == "submit_support_ticket":
        # 🎫 In a real implementation, this would create a ticket in your system
        ticket_id = f"TKT-{int(__import__("time").time()):.0f}"

        response_text = f"""## 🎫 Support Ticket Created

**Ticket ID**: {ticket_id}
**Subject**: {arguments['subject']}
**Priority**: {arguments.get('priority', 'medium')}

A support representative will follow up shortly. ✅
"""
        return [TextContent(type="text", text=response_text)]

    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """
    📚 List available resources (data sources) for the AI assistant.
    """
    return [
        Resource(
            uri="47doors://faq/all",
            name="All FAQs",
            description="Complete FAQ database for university support",
            mimeType="application/json"
        )
    ]


async def main():
    """🚀 Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

### 🔹 Step 3: Create MCP Server Entry Point (5 minutes)

Create `backend/mcp_main.py` to run the MCP server:

```python
"""
🚀 Entry point for running 47 Doors as an MCP server.
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
```

### 🔹 Step 4: Configure VS Code for MCP (10 minutes)

Create or update `.vscode/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "47doors": {
      "command": "python",
      "args": ["backend/mcp_main.py"],
      "env": {
        "AZURE_OPENAI_ENDPOINT": "${env:AZURE_OPENAI_ENDPOINT}",
        "AZURE_OPENAI_API_KEY": "${env:AZURE_OPENAI_API_KEY}",
        "AZURE_SEARCH_ENDPOINT": "${env:AZURE_SEARCH_ENDPOINT}",
        "AZURE_SEARCH_API_KEY": "${env:AZURE_SEARCH_API_KEY}"
      }
    }
  }
}
```

### 🔹 Step 5: Implement the 4 Required Tools (15 minutes)

Your MCP server should expose these four tools:

| 🔧 Tool | 📝 Purpose | 📥 Input |
|------|---------|-------|
| `university_support_query` | RAG-powered Q&A | question, optional category |
| `list_faq_categories` | List all categories | none |
| `get_category_faqs` | Get FAQs by category | category name |
| `submit_support_ticket` | Create support ticket | subject, description, email, priority |

The code in Step 2 implements all four. Customize them to match your existing service layer.

### 🔹 Step 6: Test with Copilot Agent Mode (10 minutes)

1. 🔄 **Restart VS Code** to load the MCP configuration

2. 💬 **Open Copilot Chat** and switch to **Agent Mode** (click the mode selector at the top of the chat panel and choose "Agent")

3. ✅ **Verify MCP Server Connection**:
   - In the chat input, click the **Tools** icon to see available MCP tools
   - You should see tools from your `47doors` MCP server listed (e.g., `university_support_query`, `list_faq_categories`)
   - MCP tools are automatically discovered in Agent Mode -- no `@` prefix is needed

4. 🧪 **Test Each Tool**:

   ```
   What are the housing options for freshmen?
   ```
   Expected: RAG-powered response with sources ✅

   ```
   List all FAQ categories
   ```
   Expected: List of categories with descriptions ✅

   ```
   Show me all financial aid FAQs
   ```
   Expected: FAQs from the financial_aid category ✅

   ```
   I can't find information about parking permits, please create a ticket
   ```
   Expected: Support ticket confirmation ✅

5. 🐛 **Debug if Needed**:
   - Check VS Code Output panel (select "MCP" from dropdown)
   - Run MCP server manually to see logs:
     ```bash
     python backend/mcp_main.py
     ```

---

## ✅ Deliverables

When you complete this lab, verify the following:

- [ ] 🚀 MCP server starts without errors
- [ ] 🔧 `university_support_query` tool responds to questions
- [ ] 💬 Copilot Agent Mode invokes your MCP tools correctly
- [ ] ✅ All four tools are discoverable and functional

---

## 🔧 Troubleshooting

### ❌ MCP Server Won't Start

```
Error: ModuleNotFoundError: No module named 'mcp'
```
**Solution**: Ensure you installed the MCP SDK: `pip install "mcp>=1.6.0"`

### ❌ MCP Tools Don't Appear in Agent Mode

1. 📄 Check that `.vscode/mcp.json` exists and has valid JSON
2. 🔄 Restart VS Code completely (not just reload window)
3. 📦 Check VS Code version supports MCP (1.85+)
4. 📋 Look for errors in Output > MCP

### ❌ Tool Invocation Fails

```
Error: Connection refused
```
**Solution**:
1. ✅ Verify environment variables are set correctly
2. 🔧 Ensure your RAG service is properly initialized
3. ☁️ Check that Azure services are accessible

### ❌ RAG Service Errors

```
Error: Azure OpenAI endpoint not configured
```
**Solution**: Ensure your `.env` file has all required variables and they're passed to the MCP server via the config.

---

## 🏗️ Architecture Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                         VS Code                                  │
│  ┌──────────────────┐    ┌─────────────────────────────────┐   │
│  │  GitHub Copilot  │───▶│      MCP Client (built-in)      │   │
│  └──────────────────┘    └─────────────────────────────────┘   │
│                                        │                         │
└────────────────────────────────────────│─────────────────────────┘
                                         │ stdio
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    47 Doors MCP Server                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     mcp_server.py                         │  │
│  │  • 📋 list_tools() → Expose 4 tools                      │  │
│  │  • ⚡ call_tool() → Handle invocations                   │  │
│  │  • 📚 list_resources() → Expose FAQ database             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    RAG Service                            │  │
│  │  (Reuses Lab 05 implementation)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
└──────────────────────────────│───────────────────────────────────┘
                               │
                               ▼
┌──────────────────┐    ┌──────────────────┐
│  Azure OpenAI    │    │  Azure AI Search │
│  (Embeddings +   │    │  (Vector Store)  │
│   Completions)   │    │                  │
└──────────────────┘    └──────────────────┘
```

---

## ➡️ Next Steps

After completing this lab, you have built a full-stack AI-powered application:

1. 🎨 **Labs 01-02**: Understanding agents and Azure MCP setup
2. 🔧 **Labs 03-04**: Spec-driven development and RAG pipeline
3. 🔍 **Lab 05**: RAG pipeline with vector search
4. 🚀 **Lab 06**: Deployment to Azure
5. 🔌 **Lab 07**: MCP server for AI assistant integration

Consider these extensions:
- 🔒 Add authentication to your MCP server
- 📊 Implement MCP resources for real-time data
- 📝 Create custom MCP prompts for common workflows
- 🔗 Explore other MCP clients (Claude Desktop, custom integrations)

---

## 📚 Resources

- 📖 [MCP Specification](https://spec.modelcontextprotocol.io/)
- 🐍 [MCP Python SDK](https://github.com/anthropics/mcp)
- 💻 [VS Code MCP Documentation](https://code.visualstudio.com/docs/copilot/mcp)
- 🏗️ [Building MCP Servers](https://modelcontextprotocol.io/docs/concepts/servers)

---

## 📊 Version Matrix

| Component | Required Version | Tested Version |
|-----------|-----------------|----------------|
| 🐍 Python | 3.11+ | 3.12.10 |
| 🔌 MCP SDK | 1.6+ | 1.6.0 |
| 🤖 GitHub Copilot | Latest | 1.x |
| 🖥️ VS Code | 1.96+ | 1.99+ |

---

<div align="center">

[← Lab 06](../06-deploy-with-azd/README.md) | **Lab 07** | 🏆 Boot Camp Complete!

📅 Last Updated: 2026-02-26 | 📝 Version: 1.1.0

</div>
