# 📋 Release Notes

## Version 0.1.5 - Phone Bridge Live 📞

**Release Date**: 2026-04-21
**Branch**: `main`
**Status**: Production
**Revision**: azd-1776792457

---

### 🎉 Major Release: Phone Bridge is Production

The phone-to-Realtime integration is live and verified on real Azure Communication Services hardware.

#### What's New
- **Real Phone Integration**: Call +1 (913) 217-1946 from any phone to reach the agent
- **Full Bidirectional Transcripts**: Caller speech AND agent responses render in real time on `/live`
- **Same 3-Agent Pipeline**: Phone calls run through QueryAgent → RouterAgent → ActionAgent, identical to browser voice
- **Production Architecture**: ACS Call Automation → WebSocket bridge (managed identity auth) → Azure OpenAI Realtime API
- **No Persistent Credentials**: Ephemeral tokens; backend uses managed identity for Azure access

#### Verification
- Browser voice (WebRTC) ✅ Working
- Phone bridge (ACS → Realtime) ✅ Working  
- Real-time transcripts on `/live` ✅ Bidirectional (caller + agent)
- Same knowledge base, routing, ticket creation ✅ Full parity

---

## Version 0.1.4 - Test Fixes & Hackathon-to-Bootcamp Rename 🛠️

**Release Date**: 2026-03-01
**Branch**: `main`
**Status**: Stable

---

### 🔧 Fixes

#### Hackathon → Boot Camp Rename
- **Changed**: All references renamed from "hackathon" to "boot camp" across the entire codebase (docs, code, configs)

#### Lab 05 Test Fix
- **Fixed**: `test_lab05.py` async tests now properly discovered by pytest with `@pytest.mark.asyncio` decorators
- **Added**: `@requires_azure` skip condition so tests gracefully skip when Azure credentials are not configured

#### Frontend Test Configuration
- **Fixed**: `vitest.config.ts` now excludes `tests/e2e/**` to prevent Playwright tests from being collected by vitest
- **Result**: Frontend unit tests: 8/8 passing cleanly

#### GPT-4o Eval Fix
- **Fixed**: Work-study job classification eval in `test_gpt4o_evals.py` now accepts both `GENERAL_INQUIRY` and `STUDENT_SERVICES` as valid categories
- **Result**: Backend tests: 435/435 passing

### 📊 Test Results Summary

| Suite | Result |
|-------|--------|
| Backend tests | 435/435 ✅ |
| Frontend unit tests | 8/8 ✅ |
| Lab 01 - Understanding Agents | 7/7 ✅ (EXEMPLARY) |
| Lab 02 - Azure MCP Setup | 5/10 ⚠️ (requires az login) |
| Lab 03 - Spec-Driven Dev | 8/8 ✅ (EXEMPLARY) |
| Lab 05 - Agent Orchestration | 3/3 ✅ |
| Lab 06 - Deploy with azd | 10/13 ⚠️ (requires az login) |
| Lab 07 - MCP Server | 8/8 ✅ (EXEMPLARY) |

---

### 📁 Files Updated (This Release)

- `labs/05-agent-orchestration/test_lab05.py`
- `frontend/vitest.config.ts`
- `backend/tests/test_gpt4o_evals.py`
- `CHANGELOG.md`
- `RELEASE_NOTES.md`
- `docs/LAB_TEST_PLAN.md`
- `docs/LAB_TESTING_SUMMARY.md`
- `docs/LAB_VALIDATION_RESULTS.md`
- `docs/LAB_00_VALIDATION_RESULTS.md`
- `README.md`

---

## Version 0.1.3 - Deployment Reliability & Lab Runbook Updates ☁️

**Release Date**: 2026-02-26
**Branch**: `main`
**Status**: Stable

---

### 🔥 Major Improvements

#### Azure Deployment Hardening (Lab 06)

- **Added**: Service-principal-first authentication guidance for `az` and `azd` in Conditional Access environments (`AADSTS53003` fallback)
- **Added**: Provider registration runbook for `Microsoft.App` and `Microsoft.Web`
- **Fixed**: Key Vault naming reliability in Bicep (length/character-safe naming)
- **Added**: Dedicated `cosmosLocation` support to decouple Cosmos region from app-hosting region
- **Validated**: Cosmos deployment succeeds in `canadacentral` while ACA runs in `southcentralus`

#### Lab Documentation Refresh (Especially Exercises)

- **Updated**: Lab 02 README with Node 20+ requirement and modern Azure MCP package usage (`@azure/mcp`)
- **Updated**: Lab 06 README and Exercise 06b with backend-first deploy path, non-interactive `azd up --no-prompt`, and real-world failure mitigations
- **Updated**: Exercise 06a with deploy-safe dependency guidance to prevent Docker build failures from optional packages

#### Coach Runbook Enhancements

- **Expanded**: `coach-guide/TROUBLESHOOTING.md` with practical fixes for:
  - `AADSTS53003` login failures
  - Node 20 requirement for Azure MCP
  - Missing provider registration
  - Cosmos regional capacity constraints

---

### 📁 Files Updated (This Release)

- `README.md`
- `docs/specs/spec.md`
- `docs/deployment/COST_ESTIMATION.md`
- `coach-guide/TROUBLESHOOTING.md`
- `labs/02-azure-mcp-setup/README.md`
- `labs/06-deploy-with-azd/README.md`
- `labs/06-deploy-with-azd/exercises/06a-local-docker.md`
- `labs/06-deploy-with-azd/exercises/06b-azure-deployment.md`
- `infra/main.bicep`
- `infra/main.parameters.json`

---

## Version 0.1.2 - Codespaces Proxy & Networking Fixes 🌐

**Release Date**: 2026-02-26
**Branch**: `main`
**Status**: Stable

---

### 🔥 Critical Fixes

#### Frontend API Proxy — IPv4/IPv6 Mismatch

- **Fixed**: Vite proxy target changed from `http://localhost:8000` to `http://127.0.0.1:8000` in `vite.config.ts`
- **Root cause**: In Codespaces (Debian), Vite binds to IPv6 (`::1`) and resolves `localhost` to IPv6 in its proxy. Uvicorn binds to IPv4 (`0.0.0.0`). The proxy silently failed with HTTP 500 and an empty response body.
- **Diagnosis**: `ss -tlnp | grep -E '8000|5173'` showed the address family mismatch
- **Impact**: All API calls through the Vite proxy now succeed in Codespaces and local development

#### Frontend .env — Removed hardcoded localhost backend URL

- **Fixed**: `VITE_API_BASE_URL` in `frontend/.env` cleared (was `http://localhost:8000`)
- **Root cause**: In Codespaces, the browser runs outside the container. Setting `VITE_API_BASE_URL=http://localhost:8000` caused the browser to call `localhost:8000` directly, bypassing the Vite proxy entirely. This resulted in `ERR_CONNECTION_REFUSED` and "Service temporarily unavailable" in the chat UI.
- **Impact**: API calls now use relative paths (`/api/...`) and are correctly proxied by the Vite dev server

---

### 🔍 How to Diagnose

If the frontend shows "Service temporarily unavailable" or 502 errors:

1. Check `frontend/.env` — `VITE_API_BASE_URL` must be **empty** in Codespaces
2. Check browser console — `ERR_CONNECTION_REFUSED` to `localhost:8000` means the env var is wrong
3. Run `ss -tlnp | grep -E '8000|5173'` — if address families differ (IPv4 vs IPv6), update `vite.config.ts` proxy target to `http://127.0.0.1:8000`
4. After changes, restart Vite and hard-refresh the browser (Ctrl+Shift+R)

---

### 📁 Files Changed

- `frontend/.env` — Cleared `VITE_API_BASE_URL` (was `http://localhost:8000`)
- `frontend/vite.config.ts` — Proxy target changed to `http://127.0.0.1:8000`

---

## Version 0.1.1 - Critical Safety Fixes 🚨

**Release Date**: 2026-02-03
**Branch**: `main`
**Status**: Stable

---

### 🔥 Critical Fixes

#### Emergency Escalation System

- **Fixed**: Emergency safety messages (harm, danger, threats) now properly escalate to human support
- **Added**: Comprehensive safety keywords to sensitive topics detection:
  - `harm`, `hurt`, `hurting`, `harming`
  - `danger`, `dangerous`
  - `attack`, `attacking`
  - `abuse`, `abusing`
- **Impact**: Student safety messages now receive immediate human attention with 1-hour response time

#### Intent Classification

- **Fixed**: Nonsensical clarification questions with duplicate options
- **Improved**: Deduplication logic in clarification question generation
- **Enhanced**: Intent examples for better "login issues" classification

#### Test Infrastructure

- **Fixed**: ActionAgent test failures with AsyncMock configuration
- **Fixed**: CORS configuration for GitHub Codespaces environment
- **Verified**: All core chat functionality tests passing

---

### 🧪 Testing Updates

- ✅ Emergency escalation verified with real safety messages
- ✅ Playwright E2E tests passing for core functionality
- ✅ Chat interface, routing, and escalation flows working correctly
- ✅ CORS configuration confirmed with no errors

---

### 📁 Files Changed

- [backend/mock_data/intent_examples.json](backend/mock_data/intent_examples.json#L360-L380) - Added safety keywords
- [backend/app/services/mock/llm_service.py](backend/app/services/mock/llm_service.py#L244-L253) - Deduplication logic
- [backend/tests/test_agents.py](backend/tests/test_agents.py#L206-L211) - Fixed AsyncMock
- [backend/.env](backend/.env#L36) - Fixed CORS Codespaces URL

---

## Version 0.1.0 - Initial Release 🎉

**Release Date**: 2026-01-21
**Branch**: `1-front-door-agent`
**Status**: MVP / Demo Ready

---

### 🌟 Highlights

This is the initial release of the **Universal Front Door Support Agent** - a three-agent AI system designed to solve the "47 front doors" problem in university student support.

---

### ✨ New Features

#### 🤖 Three-Agent Architecture

- **QueryAgent**: Intent detection with 30+ categories and entity extraction
- **RouterAgent**: Smart routing to 7 departments with escalation logic
- **ActionAgent**: Ticket creation and knowledge base retrieval

#### 🎯 Intent Detection

- LLM-based classification with few-shot prompting
- Supports 30+ intent categories including:
  - Account access (password reset, login issues)
  - Academic records (transcripts, grades)
  - Financial (aid inquiries, tuition)
  - Facilities (maintenance, room booking)
  - Enrollment (course registration, holds)
  - Student services (parking, ID cards)

#### 🔀 Smart Routing

- Routes to: IT, HR, Registrar, Financial Aid, Facilities, Student Affairs, Campus Safety
- Automatic escalation triggers:
  - Low confidence (< 0.70)
  - Policy keywords (appeal, waiver, refund)
  - Sensitive topics (Title IX, mental health)
  - Multi-department coordination
  - User request for human
  - Max clarification attempts exceeded

#### 🎫 Ticket Management

- Structured ticket IDs: `TKT-{DEPT}-{YYYYMMDD}-{SEQ}`
- Priority levels: Low, Medium, High, Urgent
- SLA-based response time estimates

#### 📚 Knowledge Base Integration

- Top 3 relevant articles per query
- Semantic search capabilities
- Department-specific content

#### 💬 Modern Chat Interface

- React 18 with TypeScript
- Real-time typing indicators
- One-click ticket ID copying
- Responsive mobile design

#### ♿ Accessibility (WCAG AA)

- High contrast mode toggle
- Keyboard navigation support
- Screen reader optimized
- Skip-to-content links
- ARIA labels throughout

---

### 🏗️ Technical Implementation

#### Backend (Python 3.11+)

- FastAPI with async/await patterns
- Pydantic v2 for data validation
- Dependency injection container
- Comprehensive mock services for demo mode

#### Frontend (React 18)

- TypeScript for type safety
- Tailwind CSS for styling
- Custom hooks (useChat, useHighContrast)
- Component-based architecture

#### Infrastructure Ready

- Docker multi-stage builds
- Docker Compose orchestration
- nginx reverse proxy configuration
- Azure deployment configs prepared

---

### 📊 Implementation Progress

| Phase   | Description                   | Status      |
| ------- | ----------------------------- | ----------- |
| Phase 1 | Project Setup & Configuration | ✅ Complete |
| Phase 2 | Foundational Services         | ✅ Complete |
| Phase 3 | US1 - Standard Support Flow   | ✅ Complete |
| Phase 4 | US2 - Policy Escalation       | 🔄 40%      |
| Phase 5 | US3 - Status Tracking         | ⏳ Pending  |
| Phase 6 | US4 - Clarification Flow      | ⏳ Pending  |
| Phase 7 | US5 - Human Request           | ⏳ Pending  |
| Phase 8 | Polish & Documentation        | ⏳ Pending  |

---

### 🧪 Testing

#### Unit Tests

- Agent logic coverage
- Service layer tests
- Model validation tests

#### Integration Tests

- Chat flow end-to-end
- Escalation scenarios
- Ticket creation flow

#### E2E Tests (Playwright)

- Full user journey tests
- Accessibility compliance tests
- Mobile responsiveness tests

---

### 🔧 Configuration

#### Environment Variables

| Variable                | Description          | Default |
| ----------------------- | -------------------- | ------- |
| `MOCK_MODE`             | Enable demo services | `true`  |
| `AZURE_OPENAI_ENDPOINT` | LLM endpoint         | -       |
| `COSMOS_DB_ENDPOINT`    | Database endpoint    | -       |
| `SERVICENOW_INSTANCE`   | Ticket system        | -       |

---

### 📁 Project Structure

```
front-door/
├── backend/           # Python FastAPI backend
│   ├── src/
│   │   ├── agents/    # QueryAgent, RouterAgent, ActionAgent
│   │   ├── models/    # Pydantic schemas
│   │   ├── services/  # Business logic & integrations
│   │   └── api/       # REST endpoints
│   └── tests/         # pytest test suite
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── hooks/       # Custom React hooks
│   │   └── services/    # API client
│   └── tests/           # Jest & Playwright tests
└── specs/             # Feature specifications
```

---

### 🚀 Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Access at: http://localhost:5173

---

### 🐛 Known Limitations

1. **English Only**: Multi-language support planned for v2
2. **Mock Services**: Production integrations require Azure configuration
3. **Students Only**: Faculty/staff support planned for v2/v3
4. **Partial Implementation**: Phases 4-8 are work in progress

---

### 🔮 Roadmap

#### v0.2.0 (Planned)

- Complete US2-US5 implementation
- Enhanced error handling
- Performance optimizations

#### v1.0.0 (Future)

- Production Azure integrations
- Full E2E test coverage
- Performance benchmarking
- Security audit

#### v2.0.0 (Future)

- Multi-language support
- Faculty support
- Voice channel integration

---

### 📝 Contributors

- Implementation by Claude Opus 4.5

---

### 📄 License

Proprietary - Higher Education CAB Project

---

**Full documentation**: See [README.md](README.md)
**Specifications**: See [specs/1-front-door-agent/](specs/1-front-door-agent/)
