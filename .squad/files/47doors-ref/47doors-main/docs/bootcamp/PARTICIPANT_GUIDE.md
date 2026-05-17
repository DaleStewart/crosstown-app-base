# 47 Doors Boot Camp - Participant Guide

Welcome to the 47 Doors Boot Camp! This guide will help you get started and navigate through the labs.

---

## What You're Building

You will build a **three-agent AI system** that eliminates the "47 Front Doors" problem in university student support. Instead of students navigating multiple disconnected support channels, they interact with one intelligent interface that detects intent, routes requests to the correct department, retrieves knowledge base articles, and creates support tickets automatically. By the end of this boot camp, you will have a working agent pipeline deployed to Azure that can classify student queries, search a knowledge base with RAG, and orchestrate multi-turn conversations.

- 🎤 **Voice interaction** — speak to the same AI pipeline via browser microphone
- 📱 **Phone support** — the same agents answer real phone calls at +1 (913) 217-1946 (now live!)

---

## Prerequisites Checklist

Before starting Lab 00, verify you have:

- [ ] **Python 3.11+** - `python --version`
- [ ] **Node.js 18+** - `node --version`
- [ ] **VS Code** with GitHub Copilot extension installed
- [ ] **Azure CLI** - `az --version`
- [ ] **Docker Desktop** installed and running
- [ ] **Git** - `git --version`
- [ ] **Azure subscription** with access credentials (provided by instructor)
- Microphone (for optional voice exercises in Lab 05)

---

## Lab Overview

| Lab | Title | Duration | What You'll Do |
|-----|-------|----------|----------------|
| **00** | Environment Setup | 30 min | Configure credentials, verify tools, test health endpoint |
| **01** | Understanding AI Agents | 90 min | Learn three-agent pattern, build intent classifier |
| **02** | Azure MCP Setup | 30 min | Configure MCP Server for Copilot, test Azure queries |
| **03** | Spec-Driven Development | 45 min | Write SPEC.md, create constitution, generate code from spec |
| **04** | Build RAG Pipeline | 120 min | Set up Azure AI Search, create embeddings, build RetrieveAgent |
| **05** | Agent Orchestration | 120 min | Wire up three-agent pipeline, implement handoffs, add multi-turn; optional voice/phone extension |
| **06** | Deploy with azd | 90 min | Containerize with Docker, deploy to Azure, configure monitoring |
| **07** | MCP Server (Stretch) | 60 min | Expose 47 Doors as MCP server for Copilot Agent Mode |

**Total Estimated Time:** 9+ hours (full day boot camp)

---

## How to Get Help

1. **Raise your hand** - Instructors and lab assistants are circulating
2. **Check the solution folder** - Each lab has a `solution/` directory with reference implementations
3. **Use the boot camp chat channel** - Post questions for peer support
4. **Review troubleshooting sections** - Each lab README includes common issues and fixes
5. **Pair with a neighbor** - Two heads are better than one!

---

## Assessment Criteria

Your progress will be evaluated on these deliverables:

| Lab | Key Deliverable | Success Criteria |
|-----|-----------------|------------------|
| 00 | Environment verification | `verify_environment.py` passes all checks |
| 01 | Intent classifier | >90% accuracy on sample queries |
| 02 | MCP configuration | `@azure` queries work in Copilot |
| 03 | Specification document | Complete SPEC.md with acceptance criteria |
| 04 | RAG pipeline | Hybrid search returns relevant KB articles with citations |
| 05 | Agent orchestration | Full pipeline handles multi-turn conversations |
| 06 | Azure deployment | Agent deployed and health check responds |
| **Bonus** | **Voice & Phone Extensions (Bonus):** 10 points | Browser voice works; phone bridge demonstrates end-to-end (live at +1 (913) 217-1946) |

---

## Important Links

| Resource | URL |
|----------|-----|
| Repository | `https://github.com/your-org/47doors` |
| API Documentation | `http://localhost:8000/docs` (after starting backend) |
| Azure Portal | `https://portal.azure.com` |
| Azure OpenAI Studio | `https://oai.azure.com` |
| GitHub Copilot Docs | `https://docs.github.com/copilot` |
| Azure AI Search Docs | `https://learn.microsoft.com/azure/search/` |
| FastAPI Documentation | `https://fastapi.tiangolo.com` |

---

## Tips for Success

1. **Read the full lab README** before starting each exercise
2. **Don't skip Lab 00** - environment issues will slow you down later
3. **Commit frequently** - save your progress as you go
4. **Ask for help early** - don't struggle alone for more than 10 minutes
5. **Use Copilot liberally** - that's what it's here for!

---

Good luck, and have fun building the future of university support!
