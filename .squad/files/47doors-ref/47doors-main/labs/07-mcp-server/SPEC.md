# Lab 07: MCP Server - Completion Specification

> **STRETCH GOAL**: This lab is optional. Participants who skip this lab can still pass the boot camp with full marks on Labs 01-06.

## What "Done" Looks Like

A successfully completed Lab 07 demonstrates:

1. **MCP Server Running**: The 47 Doors backend runs as an MCP server using stdio transport
2. **Tools Exposed**: All four required tools are discoverable by MCP clients
3. **VS Code Integration**: Copilot chat can invoke tools via `Copilot Agent Mode` mentions
4. **RAG Integration**: The `university_support_query` tool returns contextual answers using your Lab 05 RAG pipeline

## Deliverables

### Deliverable 1: MCP Server Implementation

| Criterion | Requirement |
|-----------|-------------|
| File Location | `backend/app/mcp_server.py` |
| Server Name | `47doors-university-support` |
| Transport | stdio (standard input/output) |
| Dependencies | `mcp`, `` in requirements.txt |

**Acceptance Criteria**:
- [ ] Server starts without errors when run via `python backend/mcp_main.py`
- [ ] Server exports `list_tools()` handler returning 4 tools
- [ ] Server exports `call_tool()` handler that invokes tool logic
- [ ] Server properly initializes RAG service from Lab 05

### Deliverable 2: Four MCP Tools

| Tool Name | Input Schema | Expected Output |
|-----------|--------------|-----------------|
| `university_support_query` | `{question: string, category?: string}` | RAG answer with confidence and sources |
| `list_faq_categories` | `{}` | List of category objects with names and counts |
| `get_category_faqs` | `{category: string}` | List of FAQ Q&A pairs for category |
| `submit_support_ticket` | `{subject: string, description: string, student_email?: string, priority?: string}` | Ticket confirmation with ID |

**Acceptance Criteria**:
- [ ] `university_support_query` returns answers with confidence scores
- [ ] `university_support_query` includes source citations
- [ ] `list_faq_categories` returns all categories from your knowledge base
- [ ] `get_category_faqs` filters FAQs by the specified category
- [ ] `submit_support_ticket` generates a ticket ID and confirmation

### Deliverable 3: VS Code MCP Configuration

| Criterion | Requirement |
|-----------|-------------|
| File Location | `.vscode/mcp.json` |
| Server Key | `47doors` |
| Environment Variables | Properly references Azure credentials |

**Acceptance Criteria**:
- [ ] VS Code recognizes the MCP server configuration
- [ ] `Copilot Agent Mode` appears in Copilot chat agent list
- [ ] Environment variables are passed correctly to MCP server

### Deliverable 4: Working Integration

**Acceptance Criteria**:
- [ ] Typing `Copilot Agent Mode What is the deadline for housing applications?` returns a RAG-powered answer
- [ ] The answer includes source citations
- [ ] Multiple consecutive queries work without server restart
- [ ] Error cases (unknown category, empty query) are handled gracefully

## Assessment Rubric

| Component | Points | Criteria |
|-----------|--------|----------|
| MCP Server Starts | 2 | Server runs without errors, stdio transport works |
| Tools Discoverable | 2 | `list_tools()` returns all 4 tools with correct schemas |
| RAG Tool Works | 3 | `university_support_query` returns contextual answers with sources |
| VS Code Integration | 2 | `Copilot Agent Mode` queries work in Copilot chat |
| Error Handling | 1 | Graceful handling of edge cases and errors |
| **Total** | **10** | **Stretch goal bonus points** |

## Grading Notes

### This is a Stretch Goal

- **Skipping Lab 07 does NOT affect your boot camp score**
- Labs 01-06 are worth 100% of the required points
- Lab 07 is bonus credit for participants who finish early
- Attempting Lab 07 shows advanced understanding even if incomplete

### Partial Credit

| Completion Level | Points Awarded |
|------------------|----------------|
| MCP server runs with at least 1 working tool | 4 |
| All tools work but VS Code integration incomplete | 7 |
| Full completion | 10 |
| Exceptional (custom resources, prompts, or additional tools) | 10 + recognition |

## Verification Checklist

Before submitting, verify:

```bash
# 1. MCP server starts
python backend/mcp_main.py
# Should start without errors (Ctrl+C to stop)

# 2. Dependencies installed
pip show mcp 
# Should show package info for both

# 3. VS Code config exists
cat .vscode/mcp.json
# Should show 47doors server configuration
```

In VS Code:
1. Open Copilot Chat (Ctrl+Shift+I)
2. Type `@` and verify `47doors` appears
3. Send: `Copilot Agent Mode List all FAQ categories`
4. Verify response lists your categories

## Common Issues That Block Completion

| Issue | Resolution |
|-------|------------|
| RAG service not initialized | Ensure Lab 05 `RAGService` is importable |
| Environment variables missing | Check `.env` file and `mcp.json` env section |
| VS Code doesn't see MCP server | Restart VS Code (full restart, not just reload) |
| Tool schema validation fails | Verify inputSchema matches MCP spec exactly |
| Azure connection errors | Confirm Lab 05 tests pass before attempting Lab 07 |

## Success Indicators

You have successfully completed Lab 07 when:

1. You can ask `Copilot Agent Mode` questions in VS Code Copilot
2. Answers are contextually relevant (using your RAG pipeline)
3. Source citations appear in responses
4. The demo works reliably for multiple queries

This demonstrates mastery of:
- MCP protocol and tool design
- Integration between multiple systems (RAG + MCP + VS Code)
- Production-ready AI assistant patterns
