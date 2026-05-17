# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC + phone call-in via ACS Call Automation
- **Created:** 2026-04-09

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-04-09 — Hackathon Exercise Updates: Voice & Telephony Content Integration

**Mission**

Created comprehensive implementation plan and executed all changes to align 8 hackathon labs, coach guide, workshop site, and core documentation with Tank's and Switch's voice/telephony implementations.

**Scope**

- 20 files modified
- 968 lines added
- 1 commit: d9ec1fb ("Exercise updates: voice and telephony content...")

**Key Deliverables**

1. **New Exercise:** Exercise 05x (voice/telephony-focused lab)
2. **Lab Updates:** Labs 00-06 (all 8 labs) now explicitly reference:
   - Tank's phone call-in infrastructure (ACS Call Automation, Realtime API media streaming)
   - Tank's transcript streaming fix (GA event name `response.output_audio_transcript.done`, real service wiring)
   - Switch's RunbookPage/LivePage split (enables presenter control of audience view)
3. **Coach Guide Updates:** 4 files updated with:
   - Voice/phone feature orientation for facilitators
   - Walkthroughs showing how to use RunbookPage for preparation, LivePage for projection
   - Call demonstration scripts and troubleshooting notes
4. **Documentation:**
   - `participant-guide.md` — Added voice/phone feature overview and quick links
   - `quick-reference.md` — New voice/phone quick-start section
   - `README.md` — Updated project description to highlight voice/phone integration
   - `CHANGELOG.md` — Entry documenting exercise content alignment work
5. **Workshop Site:** New "Telephony" tab added to navigation; existing tabs updated with voice/phone references

**Architecture Patterns Documented**

- Voice features as modality extension of text chat (shared `session_id` UUID across modalities)
- Phone call-in as enterprise feature (ACS PSTN bridging to same 4-tool pipeline)
- Presenter control via RunbookPage/LivePage UI pattern (live demo experience management)
- Three-layer PII filter applies to both text and voice/phone

**Content Integration Strategy**

Each lab now includes:
1. **Feature Overview** — What voice/phone capability enables in that domain
2. **Architecture Reference** — Diagram or description of how voice/phone fits into 47 Doors pipeline
3. **Live Demo Walkthrough** — Step-by-step using RunbookPage + LivePage
4. **Exercise Modification** — Original text-based exercise + voice/phone extension task

**Coach Guide Enhancements**

- Preparation checklist: confirm phone number configured, test RunbookPage loading
- Facilitation notes: where to pause for demo questions, how to project LivePage
- Troubleshooting: common phone issues (ACS connection, audio quality) and fixes
- Accessibility note: voice feature includes captions/transcripts for deaf/hard-of-hearing participants

**Orchestration Log**

- `.squad/orchestration-log/2026-04-09T03-01-38Z-anvil.md`

**Team Coordination**

Exercise content now explicitly acknowledges and documents the work of Tank and Switch:
- Lab walkthroughs reference Tank's specific commits (transcript fix, real service wiring)
- RunbookPage/LivePage pattern is featured as a key UI innovation enabling live demos
- Coach guide points facilitators to these GitHub commits for deeper understanding

This ensures that as new cohorts work through labs, they understand the foundational voice/telephony work and can contribute improvements back to those areas of the codebase.

**Validation**

- All 20 files exist and are readable
- No tests required (documentation/content-only changes)
- Commit d9ec1fb verified in git log
- No merge conflicts with Tank's or Switch's branches (different file paths, both fully integrated)
