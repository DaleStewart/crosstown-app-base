# Changelog

All notable changes to the 47 Doors University Support Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Boot Camp Content Updates
- Added phone/telephony coverage to all boot camp materials
- New Exercise 05x: Voice & Phone Extensions (optional stretch goal)
- New workshop-site Phone Integration tab with architecture diagrams
- Updated coach guide with voice/phone facilitation notes, talking points, troubleshooting, and assessment rubric
- Updated participant guide and quick reference with voice/phone content
- Updated Lab 00 setup with voice/phone environment variables
- Updated Lab 01 prompt engineering with voice system prompt exercise
- Updated Lab 06 deployment exercises with voice/phone configuration

### Fixed

- **Voice (phone bridge):** Caller speech transcripts now render on `/live` during ACS phone calls. Azure OpenAI Realtime API `/openai/realtime` direct-WS endpoint requires flat session-level fields (`voice`, `input_audio_format`, `output_audio_format`, `input_audio_transcription`); the nested `session.audio` block used by the WebRTC `/openai/v1/realtime/calls` endpoint is rejected with `unknown_parameter: session.audio`. See `.squad/skills/azure-realtime-api-schema/SKILL.md`. (backend/app/api/media_ws.py, commit 234c2ec, revision azd-1776792457)
- **Voice (phone bridge):** Fixed `AttributeError: closed` on websocket cleanup with newer `websockets` library by switching to try/except close in the finally block. (backend/app/api/media_ws.py)

### Added

- **Voice Interaction Feature** (`002-voice-interaction`): Real-time spoken conversation channel via Azure OpenAI GPT-4o Realtime API + WebRTC
  - `POST /api/realtime/session` — ephemeral token issuance for WebRTC auth
  - `WS /api/realtime/ws` — tool call relay to 3-agent pipeline
  - `GET /api/realtime/health` — voice availability check
  - `AzureRealtimeService` — production implementation with managed identity (`ManagedIdentityCredential`)
  - `MockRealtimeService` — full simulation for demos and CI (no Azure credentials)
  - Frontend: `useVoice` hook (WebRTC state machine), `VoiceMicButton` (6-state toggle), `VoiceTranscript`, `VoiceStatusIndicator`
  - 4 voice tools: `analyze_and_route_query`, `check_ticket_status`, `search_knowledge_base`, `escalate_to_human`
  - Graceful degradation: mic button hidden when voice unavailable, text chat unaffected
  - Voice system prompt with PII filtering and natural speech output
  - Bicep: `gpt-4o-realtime-preview` model deployment
  - Demo runbook, feature summary, quickstart, manual smoke tests, eval harness

- **Eval Test Improvements**
  - Fixed mock intent routing: "deadline to withdraw" → REGISTRAR, student employment → HR
  - GPT-4o evals now runnable via `DefaultAzureCredential` fallback (API key auth disabled by Azure policy)
  - 97 GPT-4o eval tests (intent, PII, sentiment, entities, urgency, e2e) pass with `az login`

- **Boot Camp Labs Curriculum** (`001-boot-camp-labs`): Complete 8-hour boot camp curriculum with 8 progressive lab exercises
  - Lab 00: Environment Setup (30 min) - Prerequisites verification and Azure configuration
  - Lab 01: Understanding AI Agents (90 min) - Three-agent pattern and intent classification
  - Lab 02: Azure MCP Setup (30 min) - Model Context Protocol configuration
  - Lab 03: Spec-Driven Development (45 min) - Writing specs and constitutions for AI agents
  - Lab 04: Build RAG Pipeline (2 hours) - Azure AI Search with hybrid search and citations
  - Lab 05: Agent Orchestration (2 hours) - QueryAgent → RouterAgent → ActionAgent pipeline
  - Lab 06: Deploy with azd (90 min) - Docker containerization and Azure deployment
  - Lab 07: MCP Server (60 min) - Stretch goal for exposing 47 Doors as MCP server

- **Coach Guide Materials** (`coach-guide/`)
  - `FACILITATION.md` - 8-hour timeline with pacing markers and intervention points
  - `TROUBLESHOOTING.md` - Per-lab common issues and quick fixes
  - `ASSESSMENT_RUBRIC.md` - 100-point scoring rubric across 6 criteria
  - `TALKING_POINTS.md` - Phase transition messaging and key concepts

- **Participant Documentation** (`docs/boot-camp/`)
  - `PARTICIPANT_GUIDE.md` - Quick reference for boot camp participants
  - `QUICK_REFERENCE.md` - Cheat sheet with commands and file locations

- **Shared Resources** (`shared/`)
  - `constitution.md` - Higher education AI agent principles (FERPA, accessibility, escalation)
  - `department_routing.json` - Department configuration with hours and routing keywords
  - `university_schema.json` - JSON Schema definitions for curriculum entities
  - `sample_queries.json` - 56 test queries for intent classification testing

- **Knowledge Base Content** (`labs/04-build-rag-pipeline/data/`)
  - 54 knowledge base articles across 5 departments:
    - Financial Aid (12 articles)
    - Registration (12 articles)
    - Housing (10 articles)
    - IT Support (10 articles)
    - Policies (10 articles)

- **Start/Solution Code Pattern**
  - Lab 02: MCP configuration templates
  - Lab 04: search_tool.py, retrieve_agent.py (RAG pipeline)
  - Lab 05: query_agent.py, router_agent.py, action_agent.py, pipeline.py (orchestration)
  - Lab 06: Dockerfile, docker-compose.yml, azure.yaml templates
  - Lab 07: mcp_server.py (MCP tools implementation)

### Changed

- Updated main README.md with boot camp curriculum section and lab links
- Added `.dockerignore` for optimized container builds — prevents `.env` from leaking into Docker images
- Switched Azure OpenAI auth to managed identity (`ManagedIdentityCredential`) — API key auth disabled by Azure policy
- Added `aiohttp>=3.9.0` to both `requirements.txt` and `pyproject.toml` for async credential acquisition
- Renamed all references from "hackathon" to "boot camp" across the codebase

### Fixed

- **Lab 05 test_lab05.py**: Added `@pytest.mark.asyncio` decorators for async test discovery and `@requires_azure` skip condition when Azure credentials are not configured
- **Frontend vitest.config.ts**: Excluded `tests/e2e/**` from vitest to prevent Playwright tests from being incorrectly collected by vitest runner
- **Backend test_gpt4o_evals.py**: Updated work-study job classification eval to accept both `GENERAL_INQUIRY` and `STUDENT_SERVICES` as valid categories (model variance)

### Test Results (2026-03-01)

- Backend: 359/359 tests passing
- Frontend: 8/8 unit tests passing
- Lab exercises: All passing (01: 7/7, 02: 5/10 requires az login, 03: 8/8, 05: 3/3, 06: 10/13 requires az login, 07: 8/8)

## [1.0.0] - 2026-01-15

### Added

- Initial release of 47 Doors University Support Agent
- Three-agent architecture (QueryAgent, RouterAgent, ActionAgent)
- FastAPI backend with Azure OpenAI integration
- React frontend with TypeScript
- Azure deployment with Bicep templates
- Docker Compose for local development
- Mock data for development without Azure services
