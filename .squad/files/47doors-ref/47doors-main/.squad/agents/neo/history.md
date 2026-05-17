# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### Cross-Team Update — 2026-04-21

**Status:** Phone bridge verified on prod, full doc sweep landed

- Phone bridge transcript schema fix verified live on prod (revision azd-1776792457)
- Full doc sweep completed across specs, runbook, release notes, participant guide, coach guide
- Backend tests: 461/461 green
- Frontend: TypeScript clean
- See .squad/decisions.md for complete decision log
