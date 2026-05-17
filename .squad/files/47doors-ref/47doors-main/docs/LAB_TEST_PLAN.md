# 47 Doors Boot Camp Labs - Comprehensive Test Plan

**Version:** 1.1
**Date:** 2026-03-01
**Status:** Validated
**Owner:** Boot Camp Team

---

## Executive Summary

This test plan outlines the comprehensive testing strategy for the 47 Doors Boot Camp Labs (00-07). The plan includes automated testing, manual validation, user acceptance testing, and end-to-end integration testing to ensure all labs are ready for participant delivery.

**Testing Objectives:**
- Validate all 8 labs work correctly in GitHub Codespaces
- Ensure labs can be completed within stated time limits
- Verify solution code works with live Azure services
- Confirm documentation is complete and accurate
- Identify and document common issues for troubleshooting guide

---

## Test Environment

### Primary Test Environment
- **Platform:** GitHub Codespaces
- **Configuration:** Default 4-core machine
- **Branch:** `main`
- **Prerequisites:** Fresh Codespace with no prior setup

### Secondary Test Environments
- **Local Development:** macOS, Windows 11, Ubuntu 22.04
- **Browsers:** Chrome 120+, Firefox 121+, Safari 17+ (for frontend testing)

### Azure Resources Required
- Azure OpenAI (GPT-4o) - Labs 04, 05, 07
- Azure AI Search - Labs 04, 05
- Azure Container Apps - Lab 06
- Azure Resource Group with appropriate permissions

---

## Test Scope

### In Scope
✅ Lab 00-07 functionality and documentation
✅ GitHub Codespaces compatibility
✅ Mock mode functionality (Labs 00-03, 06)
✅ Azure integration (Labs 04, 05, 07)
✅ Solution code correctness
✅ Time estimates accuracy
✅ Troubleshooting documentation
✅ Coach materials completeness

### Out of Scope
❌ Performance benchmarking
❌ Load testing
❌ Security penetration testing
❌ Multi-region Azure deployment testing
❌ Custom Azure tenant configurations

---

## Test Categories

## 1. Automated Tests (Current Status: ✅ PASSING)

### 1.1 Lab Solution Syntax Tests
**Location:** `backend/tests/test_lab_solutions.py`
**Status:** 23/23 tests passing
**Run Command:** `cd backend && pytest tests/test_lab_solutions.py -v`

| Test Category | Tests | Status | Notes |
|--------------|-------|--------|-------|
| Lab 04 - RAG Pipeline | 3 | ✅ PASS | Syntax and structure validation |
| Lab 05 - Agent Orchestration | 5 | ✅ PASS | All three agents + pipeline |
| Lab 07 - MCP Server | 2 | ✅ PASS | Server structure and tools |
| Documentation Completeness | 8 | ✅ PASS | All labs have READMEs |
| Solution Code Existence | 3 | ✅ PASS | Labs 04, 05, 07 |
| Knowledge Base Content | 2 | ✅ PASS | 50+ articles, 4+ departments |

**Last Run:** 2026-02-03
**Next Run:** After any code changes to lab solutions

### 1.2 Frontend Unit Tests
**Location:** `frontend/src/components/`
**Status:** ✅ ALL PASSING (8/8)
**Run Command:** `cd frontend && npx vitest run`

| Test Suite | Tests | Status |
|------------|-------|--------|
| ChatInput | 8 | ✅ PASS |

**Last Run:** 2026-03-01

**Note:** E2E Playwright tests (`frontend/tests/e2e/`) are excluded from vitest via `vitest.config.ts` and should be run separately with `cd frontend && npm run test:e2e`. E2E tests require a running frontend/backend and browser drivers.

**Resolved Issues:**
- ✅ Fixed vitest.config.ts to exclude `tests/e2e/**` — Playwright tests were being incorrectly collected by vitest

### 1.3 Backend Unit Tests
**Location:** `backend/tests/`
**Status:** ✅ ALL PASSING (359/359)
**Run Command:** `cd backend && pytest tests/ -v`

**Test Coverage Areas:**
- ✅ Agent implementations (QueryAgent, RouterAgent, ActionAgent)
- ✅ Mock services (LLM, Ticketing, Knowledge Base)
- ✅ API endpoints (/api/chat, /api/health, /api/session)
- ✅ Intent classification
- ✅ Emergency escalation logic
- ✅ GPT-4o evals (intent classification, PII detection, sentiment, entity extraction)
- ✅ Spec compliance tests (22 functional requirements)
- ✅ Lab solution syntax tests

**Last Run:** 2026-03-01 (all 359 tests passing)

---

## 2. Manual Lab Validation

### 2.1 Lab 00 - Environment Setup (30 minutes)

**Test ID:** LAB-00-E2E
**Objective:** Validate GitHub Codespaces setup flow
**Prerequisites:** None

#### Test Steps:
1. **Launch Codespace**
   - [ ] Navigate to repository on GitHub
   - [ ] Click Code → Codespaces → Create codespace on main
   - [ ] Wait for Codespace to build (should complete in 3-5 minutes)
   - [ ] Verify Python 3.11+ and Node.js 18+ are installed

2. **Get Codespace Name**
   ```bash
   echo $CODESPACE_NAME
   ```
   - [ ] Variable returns valid codespace name (not empty)

3. **Configure CORS**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with correct CODESPACE_NAME
   ```
   - [ ] CORS_ORIGINS includes correct Codespaces URLs
   - [ ] MOCK_MODE=true is set

4. **Start Backend**
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - [ ] Server starts without errors
   - [ ] Shows "Application startup complete"

5. **Make Port 8000 Public**
   ```bash
   gh codespace ports visibility 8000:public -c $CODESPACE_NAME
   ```
   - [ ] Command succeeds
   - [ ] Port 8000 shows as "Public" in PORTS tab

6. **Test Health Endpoint**
   ```bash
   curl https://$CODESPACE_NAME-8000.app.github.dev/api/health
   ```
   - [ ] Returns 200 OK
   - [ ] JSON shows all services "up" with mock mode

7. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   - [ ] Vite starts successfully
   - [ ] Shows local URL and Network URL

8. **Access Frontend**
   - [ ] Click globe icon next to port 5173 in PORTS tab
   - [ ] Frontend loads with 47 Doors logo
   - [ ] No CORS errors in browser console (F12)

9. **Test Chat Interface**
   - [ ] Type "I forgot my password" and send
   - [ ] Receive response with ticket ID
   - [ ] Response includes knowledge base articles
   - [ ] No errors in browser console

**Expected Duration:** 20-30 minutes for first-time participant
**Pass Criteria:** All steps complete without errors, chat interface works
**Common Issues:** Port 8000 not public, CORS misconfiguration

---

### 2.2 Lab 01 - Understanding AI Agents (90 minutes)

**Test ID:** LAB-01-E2E
**Objective:** Validate intent classification exercises
**Prerequisites:** Lab 00 complete

#### Test Steps:
1. **Read Lab Documentation**
   - [ ] README.md is clear and complete
   - [ ] Learning objectives are well-defined
   - [ ] Architecture diagrams are helpful

2. **Exercise 01a - Intent Classification**
   - [ ] Open `labs/01-understanding-agents/exercises/01a-intent-classification.md`
   - [ ] Follow instructions to explore intent examples
   - [ ] Test intent classifier with provided test queries
   - [ ] Verify >90% accuracy on test dataset

3. **Exercise 01b - Prompt Engineering**
   - [ ] Open `labs/01-understanding-agents/exercises/01b-prompt-engineering.md`
   - [ ] Experiment with different prompt structures
   - [ ] Test edge cases and ambiguous queries
   - [ ] Document improvements

4. **Comprehension Check**
   - [ ] Can explain QueryAgent → RouterAgent → ActionAgent pattern
   - [ ] Understands when to use multi-agent vs monolithic
   - [ ] Can identify intents from sample queries

**Expected Duration:** 60-90 minutes
**Pass Criteria:** Understands agent architecture, intent classifier works
**Assessment:** Coach evaluation using rubric (15 points)

---

### 2.3 Lab 02 - Azure MCP Setup (30 minutes)

**Test ID:** LAB-02-E2E
**Objective:** Validate MCP configuration for Azure services
**Prerequisites:** Lab 00 complete, Azure credentials provided

#### Test Steps:
1. **Review MCP Concepts**
   - [ ] README explains Model Context Protocol clearly
   - [ ] Start code is present in `labs/02-azure-mcp-setup/start/`

2. **Configure MCP Server**
   - [ ] Follow README to set up MCP server configuration
   - [ ] Add Azure OpenAI credentials to MCP config
   - [ ] Test MCP server connection

3. **Test Natural Language Queries**
   - [ ] Send test query: "What Azure resources do I have?"
   - [ ] Verify MCP server responds correctly
   - [ ] Test error handling with invalid queries

4. **Compare with Solution**
   - [ ] Review solution code in `labs/02-azure-mcp-setup/solution/`
   - [ ] Verify implementation matches expected pattern

**Expected Duration:** 30 minutes
**Pass Criteria:** MCP server responds to @azure queries
**Note:** Can run in mock mode without real Azure credentials

---

### 2.4 Lab 03 - Spec-Driven Development (45 minutes)

**Test ID:** LAB-03-E2E
**Objective:** Validate spec writing and code generation workflow
**Prerequisites:** Lab 01 complete

#### Test Steps:
1. **Review Templates**
   - [ ] `labs/03-spec-driven-development/templates/spec-template.md` is clear
   - [ ] `labs/03-spec-driven-development/templates/constitution-template.md` is clear

2. **Exercise 03a - Write Spec**
   - [ ] Follow `exercises/03a-write-spec.md`
   - [ ] Write SPEC.md for Escalation Detection Agent
   - [ ] Include user stories, functional requirements
   - [ ] Spec is clear and unambiguous

3. **Exercise 03b - Generate from Spec**
   - [ ] Follow `exercises/03b-generate-from-spec.md`
   - [ ] Use GitHub Copilot or Claude to generate code from spec
   - [ ] Review generated code for correctness
   - [ ] Test generated code functionality

4. **Constitution Writing**
   - [ ] Write constitution.md with Higher Ed guardrails
   - [ ] Include principles for sensitive topics handling
   - [ ] Document escalation criteria

**Expected Duration:** 45 minutes
**Pass Criteria:** Spec written, constitution documented, code generated
**Assessment:** Deliverables evaluation (spec quality, constitution completeness)

---

### 2.5 Lab 04 - Build RAG Pipeline (120 minutes)

**Test ID:** LAB-04-E2E
**Objective:** Validate RAG implementation with Azure AI Search
**Prerequisites:** Labs 01-02 complete, Azure credentials configured

#### Test Steps:
1. **Setup Azure AI Search**
   - [ ] Follow README to create Azure AI Search resource
   - [ ] Note down endpoint and API key
   - [ ] Configure in backend/.env

2. **Ingest Knowledge Base Articles**
   - [ ] Run ingestion script on `labs/04-build-rag-pipeline/data/` files
   - [ ] Verify 50+ articles indexed
   - [ ] Check embeddings generated correctly
   - [ ] View index in Azure Portal

3. **Implement Search Tool**
   - [ ] Start with code in `labs/04-build-rag-pipeline/start/`
   - [ ] Implement hybrid search (vector + keyword)
   - [ ] Test search with sample queries
   - [ ] Verify relevant results returned

4. **Build RetrieveAgent**
   - [ ] Implement RetrieveAgent using search tool
   - [ ] Add citation/source attribution
   - [ ] Test with knowledge base queries
   - [ ] Handle queries with no relevant results

5. **Compare with Solution**
   - [ ] Review `labs/04-build-rag-pipeline/solution/search_tool.py`
   - [ ] Review `labs/04-build-rag-pipeline/solution/retrieve_agent.py`
   - [ ] Verify implementation correctness

6. **End-to-End Testing**
   - [ ] Query: "How do I reset my password?"
   - [ ] Query: "What are the parking permit costs?"
   - [ ] Query: "How do I apply for financial aid?"
   - [ ] Verify responses include citations
   - [ ] Verify response quality is high

**Expected Duration:** 90-120 minutes
**Pass Criteria:** Hybrid search works, citations included, quality responses
**Assessment:** 25 points (highest weight in rubric)

**CRITICAL:** This lab requires live Azure OpenAI and Azure AI Search

---

### 2.6 Lab 05 - Agent Orchestration (120 minutes)

**Test ID:** LAB-05-E2E
**Objective:** Validate three-agent pipeline with session management
**Prerequisites:** Lab 04 complete

#### Test Steps:
1. **Review Architecture**
   - [ ] README explains QueryAgent → RouterAgent → ActionAgent flow
   - [ ] Understand session context and handoff protocols

2. **Implement QueryAgent**
   - [ ] Start with `labs/05-agent-orchestration/start/query_agent.py`
   - [ ] Implement query analysis and intent detection
   - [ ] Test with sample queries

3. **Implement RouterAgent**
   - [ ] Start with `labs/05-agent-orchestration/start/router_agent.py`
   - [ ] Implement routing logic based on intent
   - [ ] Test routing decisions

4. **Implement ActionAgents**
   - [ ] Start with `labs/05-agent-orchestration/start/action_agent.py`
   - [ ] Implement specialized agents (IT, Registrar, Financial Aid, etc.)
   - [ ] Test individual agent actions

5. **Wire Up Pipeline**
   - [ ] Start with `labs/05-agent-orchestration/start/pipeline.py`
   - [ ] Integrate all three agent types
   - [ ] Implement session context management
   - [ ] Add error handling and fallbacks

6. **Test Multi-Turn Conversations**
   ```
   Turn 1: "I forgot my password"
   Turn 2: "For Canvas"
   Turn 3: "Still can't login"
   ```
   - [ ] Session context maintained across turns
   - [ ] Agent handoffs work correctly
   - [ ] Escalation triggers appropriately

7. **Compare with Solution**
   - [ ] Review all solution files in `labs/05-agent-orchestration/solution/`
   - [ ] Verify implementation matches expected patterns

**Expected Duration:** 90-120 minutes
**Pass Criteria:** Full pipeline works, multi-turn works, session managed
**Assessment:** 25 points (highest weight in rubric)

**CRITICAL:** This lab requires live Azure OpenAI

---

### 2.7 Lab 06 - Deploy with azd (90 minutes)

**Test ID:** LAB-06-E2E
**Objective:** Validate Azure deployment with azd
**Prerequisites:** Lab 05 complete, Azure subscription with contributor access

#### Test Steps:
1. **Review Deployment Architecture**
   - [ ] README explains Azure resources to be created
   - [ ] Infrastructure as Code templates are present

2. **Prepare for Deployment**
   - [ ] Install azd (Azure Developer CLI) if needed
   - [ ] Login to Azure: `azd auth login`
   - [ ] Review `labs/06-deploy-with-azd/infra/` Bicep templates

3. **Containerize Application**
   - [ ] Follow exercise `labs/06-deploy-with-azd/exercises/06a-local-docker.md`
   - [ ] Build Docker images locally
   - [ ] Test containers locally with docker-compose
   - [ ] Verify health endpoints work

4. **Deploy to Azure**
   ```bash
   azd init
   azd up
   ```
   - [ ] Resource provisioning starts
   - [ ] All resources created successfully
   - [ ] Application deployed to Azure Container Apps

5. **Verify Deployment**
   - [ ] Access deployed frontend URL
   - [ ] Test chat interface in production
   - [ ] Check health endpoint: `<url>/api/health`
   - [ ] Review logs in Azure Portal
   - [ ] Verify monitoring/Application Insights configured

6. **Test Production Features**
   - [ ] Send test queries through production endpoint
   - [ ] Verify Azure OpenAI integration works
   - [ ] Check secrets management (Key Vault)
   - [ ] Test with multiple concurrent users (2-3)

7. **Compare with Solution**
   - [ ] Review `labs/06-deploy-with-azd/solution/` files
   - [ ] Verify Bicep templates are correct

**Expected Duration:** 60-90 minutes
**Pass Criteria:** App deployed, publicly accessible, health check responds
**Assessment:** 15 points

**Note:** Can be tested locally with Docker without Azure deployment for mock mode validation

---

### 2.8 Lab 07 - MCP Server (Stretch) (60 minutes)

**Test ID:** LAB-07-E2E
**Objective:** Validate MCP server exposing 47 Doors functionality
**Prerequisites:** Lab 05 complete

#### Test Steps:
1. **Review MCP Server Concepts**
   - [ ] README explains tool/resource model
   - [ ] Start code present in `labs/07-mcp-server/start/`

2. **Implement MCP Server**
   - [ ] Define `university_support_query` tool
   - [ ] Expose ticket creation functionality
   - [ ] Expose knowledge base search
   - [ ] Test server starts correctly

3. **Test with Claude Desktop / VS Code**
   - [ ] Configure MCP server in Claude Desktop settings
   - [ ] Test @47doors query: "How do I reset password?"
   - [ ] Verify tool invocation works
   - [ ] Check response formatting

4. **Compare with Solution**
   - [ ] Review `labs/07-mcp-server/solution/mcp_server.py`
   - [ ] Verify tool definitions are correct

**Expected Duration:** 45-60 minutes
**Pass Criteria:** MCP server responds, @47doors queries work
**Assessment:** 10 points (bonus/stretch goal)

**CRITICAL:** This lab requires live Azure OpenAI

---

## 3. Integration Testing

### 3.1 Full 8-Hour Boot Camp Simulation

**Test ID:** INTEGRATION-01
**Objective:** Validate complete boot camp experience end-to-end
**Prerequisites:** Fresh GitHub Codespace, Azure credentials

#### Simulation Plan:
1. **Participant Profile:** Mid-level developer, familiar with Python/React, some Azure experience
2. **Time Allocation:**
   - Lab 00: 30 min (target) → Actual: ___
   - Lab 01: 90 min (target) → Actual: ___
   - Lab 02: 30 min (target) → Actual: ___
   - Lab 03: 45 min (target) → Actual: ___
   - Lab 04: 120 min (target) → Actual: ___
   - Lab 05: 120 min (target) → Actual: ___
   - Lab 06: 90 min (target) → Actual: ___
   - Lab 07: 60 min (target) → Actual: ___
   - **Total Target:** 7.75 hours (465 minutes)

3. **Tracking:**
   - [ ] Start timer for each lab
   - [ ] Document all blockers and issues encountered
   - [ ] Note unclear instructions or missing information
   - [ ] Rate difficulty (1-5) after each lab
   - [ ] Record Azure costs incurred

4. **Evaluation:**
   - [ ] Can complete all core labs (00-06) in 6.5 hours?
   - [ ] Are time estimates accurate (±20%)?
   - [ ] Are instructions clear without coach intervention?
   - [ ] Do solution files help when stuck?

**Pass Criteria:** Complete core labs in ≤7 hours with minimal external help

---

### 3.2 Coach Walkthrough

**Test ID:** INTEGRATION-02
**Objective:** Validate coach materials and facilitation guides
**Prerequisites:** Complete coach materials

#### Test Steps:
1. **Review Coach Guide**
   - [ ] `coach-guide/FACILITATION.md` is comprehensive
   - [ ] `coach-guide/TROUBLESHOOTING.md` covers common issues
   - [ ] `coach-guide/ASSESSMENT_RUBRIC.md` is clear and fair
   - [ ] `coach-guide/TALKING_POINTS.md` helps with explanations

2. **Simulate Participant Questions**
   - [ ] "My port 8000 won't go public" → Solution in guide?
   - [ ] "I'm getting CORS errors" → Solution in guide?
   - [ ] "Azure OpenAI is returning 429 rate limit" → Solution in guide?
   - [ ] "My intent classifier accuracy is only 60%" → Guidance in guide?
   - [ ] "The azd up command failed" → Troubleshooting steps available?

3. **Assessment Simulation**
   - [ ] Use rubric to score sample participant work
   - [ ] Rubric is unambiguous and easy to apply
   - [ ] Point allocations feel fair
   - [ ] Can provide constructive feedback using rubric

**Pass Criteria:** Coach can facilitate without external documentation

---

## 4. User Acceptance Testing

### 4.1 Participant UAT (3-5 participants)

**Test ID:** UAT-01
**Participants:** 3-5 real developers (mix of experience levels)
**Duration:** Full 8-hour boot camp

#### Feedback Collection:
- Pre-boot camp survey (experience level, expectations)
- Live observation (note struggles, questions asked)
- Post-lab surveys (clarity, difficulty, time)
- Post-boot camp interview (overall experience)

#### Success Metrics:
- [ ] ≥80% complete Lab 00 within 30 minutes
- [ ] ≥70% complete Lab 01 within 90 minutes
- [ ] ≥70% complete core labs (00-06)
- [ ] ≥60% attempt stretch goal (Lab 07)
- [ ] Average satisfaction score ≥4.0/5.0
- [ ] Would recommend boot camp to colleague ≥80%

---

## 5. Performance and Cost Testing

### 5.1 Azure Cost Validation

**Test ID:** COST-01
**Objective:** Validate estimated Azure costs per participant

#### Test Plan:
1. **Baseline Measurement**
   - [ ] Start with clean Azure subscription
   - [ ] Note starting costs

2. **Execute Full Boot Camp**
   - [ ] Run all labs requiring Azure (04, 05, 07)
   - [ ] Track API calls to Azure OpenAI
   - [ ] Monitor Azure AI Search query counts
   - [ ] Run for 8 hours

3. **Post-Boot Camp Analysis**
   - [ ] Calculate total Azure costs
   - [ ] Break down by service (OpenAI, Search, Container Apps)
   - [ ] Compare to estimate in documentation

**Expected Cost per Participant:** $5-15 for 8-hour session
**Pass Criteria:** Actual costs within 20% of estimate

---

### 5.2 Codespaces Resource Validation

**Test ID:** PERF-01
**Objective:** Validate Codespaces performance with default 4-core machine

#### Test Plan:
1. **Monitor Resource Usage**
   - [ ] Backend server memory usage
   - [ ] Frontend build performance
   - [ ] Concurrent backend + frontend running
   - [ ] Docker build in Lab 06

2. **Performance Targets**
   - [ ] Backend server startup: <10 seconds
   - [ ] Frontend hot reload: <3 seconds
   - [ ] API response time: <500ms (mock mode)
   - [ ] Docker build: <5 minutes

**Pass Criteria:** All targets met on 4-core Codespace

---

## 6. Documentation Testing

### 6.1 README Completeness

**Test ID:** DOC-01
**Checklist per Lab:**

- [ ] **Learning Objectives** clearly stated
- [ ] **Prerequisites** listed explicitly
- [ ] **Step-by-step instructions** are complete
- [ ] **Code snippets** are correct and tested
- [ ] **Expected outputs** are shown
- [ ] **Troubleshooting section** covers common issues
- [ ] **Deliverables** clearly defined
- [ ] **Next lab link** provided
- [ ] **Estimated duration** stated
- [ ] **Screenshots/diagrams** where helpful

**Target:** All items checked for all 8 labs

---

### 6.2 Link Validation

**Test ID:** DOC-02

#### Automated Link Check:
```bash
# Install markdown-link-check if needed
npm install -g markdown-link-check

# Check all lab READMEs
find labs -name "README.md" -exec markdown-link-check {} \;
```

- [ ] All internal links work
- [ ] All external links resolve (200 OK)
- [ ] Azure documentation links are current
- [ ] GitHub file references point to correct paths

---

## 7. Security and Compliance

### 7.1 Secrets Management

**Test ID:** SEC-01

#### Validation:
- [ ] No hardcoded API keys in repository
- [ ] .env.example doesn't contain real credentials
- [ ] .gitignore properly excludes .env files
- [ ] Coach guides emphasize secret protection
- [ ] Azure Key Vault used in Lab 06 deployment

---

### 7.2 Sensitive Data Handling

**Test ID:** SEC-02

#### Test Cases:
- [ ] System properly detects PII in user messages
- [ ] Emergency safety keywords trigger escalation
- [ ] Sensitive topics route to human support
- [ ] No sensitive data logged to console
- [ ] Session data includes appropriate redaction

---

## 8. Accessibility Testing

### 8.1 Frontend Accessibility

**Test ID:** A11Y-01
**Tool:** axe DevTools, Playwright accessibility tests

#### Validation:
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels present and correct
- [ ] Color contrast meets WCAG AA standards
- [ ] Screen reader compatible
- [ ] High contrast mode works

**Current Status:** 13/14 tests passing (Chromium)
**Action Required:** Fix 1 failing accessibility test

---

## Test Execution Schedule

### Phase 1: Pre-Launch Validation (3-5 days)
**Target Completion:** Before first boot camp event

| Task | Owner | Due Date | Status |
|------|-------|----------|--------|
| Fix failing E2E tests (branding, selectors) | Dev Team | Day 1 | ⏳ TODO |
| Lab 00 validation (LAB-00-E2E) | QA | Day 1 | 🔄 IN PROGRESS |
| Lab 01-03 validation (mock mode) | QA | Day 2 | ⏳ TODO |
| Lab 04-05 validation (Azure required) | Dev Team | Day 3 | ⏳ TODO |
| Lab 06-07 validation | Dev Team | Day 4 | ⏳ TODO |
| Full 8-hour simulation (INTEGRATION-01) | Senior Dev | Day 5 | ⏳ TODO |
| Coach materials review (INTEGRATION-02) | Coach | Day 5 | ⏳ TODO |
| Documentation review (DOC-01, DOC-02) | Tech Writer | Day 3 | ⏳ TODO |
| Azure cost validation (COST-01) | DevOps | Day 4 | ⏳ TODO |

### Phase 2: Participant UAT (1-2 weeks)
**Target:** 3-5 participant validation sessions

| Session | Participants | Date | Status |
|---------|-------------|------|--------|
| UAT Session 1 | 3 participants | TBD | ⏳ SCHEDULED |
| UAT Session 2 | 2 participants | TBD | ⏳ SCHEDULED |

### Phase 3: Post-UAT Fixes (3-5 days)
- Address feedback from UAT
- Update documentation based on participant questions
- Refine time estimates
- Update troubleshooting guide

### Phase 4: Final Validation (1 day)
- Re-run all critical tests
- Sign-off from stakeholders
- Ready for production use

---

## Issue Tracking

### Current Known Issues

| ID | Issue | Severity | Lab | Status | Notes |
|----|-------|----------|-----|--------|-------|
| ISSUE-001 | Firefox/Webkit E2E tests fail in Codespaces | Medium | All | Open | Browser driver config issue |
| ISSUE-002 | Branding E2E tests fail | Low | All | Open | Admin UI not in lab scope |
| ISSUE-003 | "Talk to Human" selector incorrect | Medium | Lab 00 | Open | UI element not found |
| ISSUE-004 | Ticket card test intermittent | Medium | Lab 00 | Open | Timing issue |

### Issue Priority Definitions
- **Critical:** Blocks lab completion
- **High:** Significantly impacts user experience
- **Medium:** Causes confusion or delays
- **Low:** Minor documentation or cosmetic issue

---

## Success Criteria

### Go/No-Go Decision Points

**Minimum Requirements for Launch:**
- ✅ All automated tests passing (23/23 lab solution tests)
- ⏳ Lab 00 validated end-to-end in Codespaces
- ⏳ Labs 01-07 manually validated by QA team
- ⏳ At least 1 full 8-hour simulation completed
- ⏳ Coach materials reviewed and approved
- ⏳ At least 2 UAT sessions with positive feedback
- ✅ No Critical severity issues open
- ⏳ Azure cost estimates validated

**Nice-to-Have (Not Blockers):**
- All E2E tests passing (including Firefox/Webkit)
- 5 UAT sessions completed
- Accessibility score 100% (currently 13/14)
- Video walkthroughs recorded

---

## Appendix A: Test Data

### Sample Test Queries (for Lab 00, 04, 05 validation)

**Account Access (IT Department):**
- "I forgot my password"
- "Can't log into Canvas"
- "Locked out of my account"
- "Still can't login" (follow-up)

**Academic Records (Registrar):**
- "I need a transcript"
- "How do I get my official transcript?"
- "Question about my grade in CS101"

**Financial (Financial Aid):**
- "When will my financial aid come in?"
- "How do I pay my tuition?"
- "Questions about my aid package"

**Facilities:**
- "The heat isn't working in my classroom"
- "Elevator is broken in Smith Hall"

**Emergency/Escalation:**
- "I want to talk to a person"
- "Someone is threatening me"
- "I'm feeling really depressed"

**Expected Responses:** All should route correctly, create tickets, return relevant KB articles

---

## Appendix B: Environment Setup Checklist

### Fresh Codespace Setup (for test repeatability)

1. Delete any existing Codespaces for this repo
2. Create new Codespace on main branch
3. Wait for postCreateCommand to complete
4. Verify Python 3.11+ and Node.js 18+
5. Backend .venv should exist (pre-created)
6. Frontend node_modules should exist (pre-installed)
7. No manual installation required

### Azure Test Environment

**Required Azure Services:**
- Resource Group: `rg-47doors-test`
- Azure OpenAI: GPT-4o deployment
- Azure AI Search: Standard tier
- Azure Container Apps: For Lab 06

**Cost Management:**
- Set spending alerts at $50/day
- Delete resources after testing
- Use mock mode whenever possible

---

## Appendix C: Contact Information

**Test Plan Owner:** [Name/Email]
**Lab Content Owner:** [Name/Email]
**DevOps/Azure Lead:** [Name/Email]
**QA Lead:** [Name/Email]

**Slack Channels:**
- #47doors-testing (for test execution updates)
- #47doors-boot-camp (for general discussion)

**Issue Reporting:**
- GitHub Issues: https://github.com/[org]/47doors/issues
- Tag issues with `lab-testing` label

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-03 | Test Team | Initial test plan created |

---

**Approval:**

- [ ] Test Plan Reviewed by QA Lead
- [ ] Test Plan Approved by Product Owner
- [ ] Ready for Execution

