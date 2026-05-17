# 47 Doors Boot Camp Facilitation Guide

This guide provides facilitators with a structured approach to leading the 47 Doors AI Agent boot camp curriculum. The 7-hour format (9:00 AM - 4:00 PM) balances hands-on learning with sufficient pacing to accommodate diverse skill levels.

---

## Room Setup Checklist

Complete these items **before participants arrive**:

### Physical Environment

- [ ] Projector/screen tested and working
- [ ] Whiteboard markers available (at least 3 colors)
- [ ] Power strips at each table cluster
- [ ] Seating arranged in pairs or small groups (3-4 per table)
- [ ] Facilitator station near power and screen access
- [ ] Water/refreshments station identified

### Technical Environment

- [ ] Wi-Fi credentials posted visibly
- [ ] Test internet connectivity from multiple locations in room
- [ ] Azure subscription access verified for all participants
- [ ] GitHub Codespaces quota confirmed (if using cloud dev)
- [ ] Backup hotspot available for connectivity issues
- [ ] Shared screen/demo machine ready with all labs pre-loaded

### Materials

- [ ] Printed quick-reference cards (optional but helpful)
- [ ] Sticky notes for "parking lot" questions
- [ ] Name tags or table tents
- [ ] Feedback forms ready (digital or paper)

### Pre-Flight Verification

- [ ] Run through Lab 00 setup on a fresh account
- [ ] Verify Azure OpenAI endpoints are responding
- [ ] Confirm Azure AI Search index is accessible
- [ ] Test `azd` deployment flow end-to-end

---

## 7-Hour Timeline (9:00 AM - 4:00 PM)

### Coach Escalation Playbook (Enterprise Azure Environments)

Use this rapid triage sequence when multiple participants are blocked by Azure access issues:

1. **Conditional Access block (`AADSTS53003`)**
   - Switch affected participants to service principal auth workflow.
2. **No subscription visibility for SP**
   - Confirm RBAC assignment at subscription or resource-group scope.
3. **`MissingSubscriptionRegistration` during `azd up`**
   - Ask subscription admin to register `Microsoft.App` and `Microsoft.Web`.
4. **Cosmos regional capacity errors**
   - Move Cosmos to an allowed region (for example `canadacentral`) and keep app hosting region unchanged.
5. **Lab continuity strategy**
   - Keep participants progressing with backend-first deployment path; static frontend deployment can be a follow-on step.

### 9:00 - 9:30 | Welcome & Lab 00: Environment Setup (30 min)

**Objectives:**

- Establish psychological safety and excitement
- Verify all participants have working development environments
- Set expectations for the day

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 9:00-9:10 | Welcome, introductions, day overview |
| 9:10-9:15 | Distribute credentials, explain support channels |
| 9:15-9:28 | Participants complete Lab 00 setup |
| 9:28-9:30 | Quick poll: thumbs up/down on environment status |

**Pacing Markers:**

- By 9:20 (midpoint): 70% should have VS Code/Codespace open
- By 9:25: 90% should have Python environment activated
- By 9:30: 100% should show successful test run or be paired with someone who has

**If Behind:**

- Pair struggling participants with those who finished early
- Have facilitator circulate to troubleshoot top 3 issues
- Extend by 5 min max; cut intro content, not setup time

**Key Checkpoints:**

- [ ] Can run `python --version` (3.11+)
- [ ] Can run `pytest` with no errors
- [ ] Azure credentials loaded (environment variables set)

---

### 9:30 - 10:00 | Lab 01: Understanding Agents (30 min)

**Objectives:**

- Build mental model of AI agents vs. simple LLM calls
- Understand the three-agent pattern
- Review intent classification concepts

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 9:30-9:40 | Present agent concepts (slides/whiteboard) |
| 9:40-9:50 | Walk through three-agent architecture diagram |
| 9:50-9:55 | Quick exercise: classify sample intents as a group |
| 9:55-10:00 | Transition to Lab 02 |

**Pacing Markers:**

- By 9:45: All participants understand QueryAgent → RouterAgent → ActionAgent flow
- By 9:55: Group has classified 5+ sample intents together
- By 10:00: Ready to move to Azure MCP setup

**If Behind:**

- At 9:45, if concepts unclear: use whiteboard to draw data flow
- Focus on understanding, not hands-on coding (exercises are take-home)
- Keep energy high - this is foundational knowledge

**Key Checkpoints:**

- [ ] Participant can explain why multi-agent > monolithic
- [ ] Participant understands the three-agent pattern
- [ ] Participant can identify intent categories

**Intervention Points:**

- Common confusion: Agent vs. prompt engineering. Clarify the loop.
- This is a conceptual lab - exercises can be completed later
- Keep discussion focused on architecture, not implementation details

---

### 10:00 - 10:30 | Lab 02: Azure MCP Setup (30 min)

**Objectives:**

- Configure Model Context Protocol connection to Azure
- Verify Azure OpenAI and Azure AI Search connectivity
- Understand enterprise security context

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 10:00-10:05 | Brief intro to MCP and Azure integration |
| 10:05-10:25 | Participants configure connections (guided walkthrough) |
| 10:25-10:30 | Verify all connections; troubleshoot stragglers |

**Pacing Markers:**

- By 10:15 (midpoint): 60% should have Azure OpenAI connection verified
- By 10:25: 85% should have both OpenAI and Search connected
- By 10:30: 100% should be ready (or have noted issue for later)

**If Behind:**

- This lab is configuration-heavy; expect variance
- Have backup credentials ready for authentication issues
- If >30% struggling at 10:20, do group walkthrough on projector

**Key Checkpoints:**

- [ ] Azure OpenAI endpoint responds
- [ ] Azure AI Search returns sample query
- [ ] MCP configuration file is valid JSON

**Intervention Points:**

- Most common issue: Azure subscription permissions
- Watch for: Expired tokens or wrong region endpoints
- Escalate: Any persistent 403/401 errors to Azure admin immediately
- If Node engine errors appear for Azure MCP, move participants to Node 20 before re-running checks
- If CA blocks browser login, pivot to service principal auth immediately to preserve lab timing

---

### 10:30 - 11:15 | Lab 03: Spec-Driven Development (45 min)

**Objectives:**

- Learn to write specifications before code
- Practice prompt engineering for code generation
- Experience AI-assisted development workflow

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 10:30-10:40 | Introduce spec-driven methodology |
| 10:40-11:00 | Participants write spec for Escalation Detection Agent |
| 11:00-11:10 | Generate code from spec using GitHub Copilot |
| 11:10-11:15 | Share examples; discuss spec quality |

**Pacing Markers:**

- By 10:50 (midpoint): 50% should have draft spec written
- By 11:00: 80% should have spec ready for code generation
- By 11:10: 70% should have generated initial code

**If Behind:**

- Provide spec template at 10:50 for those struggling
- Focus on one strong spec rather than multiple weak ones
- Code generation can be demoed if time is tight

**Key Checkpoints:**

- [ ] Spec includes clear inputs, outputs, and behavior description
- [ ] Generated code matches spec intent (even if imperfect)
- [ ] Participant can iterate on spec to improve output

**Intervention Points:**

- Common mistake: Specs too vague ("make it good")
- Watch for: Over-engineering specs (analysis paralysis)
- Guide toward: Specific, testable requirements

---

### 11:15 - 11:30 | Break (15 min)

**Facilitator Actions:**

- Encourage participants to step away from screens
- Be available for 1:1 questions
- Assess energy level; adjust afternoon pacing if needed
- Update parking lot with any deferred questions

---

### 11:30 - 12:30 | Lab 04: Build RAG Pipeline (60 min)

**Objectives:**

- Implement complete Retrieval-Augmented Generation pipeline
- Connect vector search to language model
- Build RetrieveAgent with citations

**Note:** Azure AI Search index is **pre-populated** with 32 KB articles. Participants start at Step 4.

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 11:30-11:40 | RAG architecture overview (visual diagram) |
| 11:40-11:50 | Verify pre-created index with `verify_index.py` |
| 11:50-12:10 | Implement hybrid search tool |
| 12:10-12:25 | Build RetrieveAgent with citations |
| 12:25-12:30 | Quick demos; transition to lunch |

**Pacing Markers:**

| Checkpoint             | Time  | Expected Completion |
| ---------------------- | ----- | ------------------- |
| Index verified         | 11:50 | 100%                |
| Search tool working    | 12:10 | 70%                 |
| RetrieveAgent complete | 12:25 | 60%                 |

**Note:** Index is pre-created, so participants focus on search and generation only.

**If Behind:**

- At 11:55, if <70% have search working: provide search_tool.py solution
- At 12:15, if <50% have agent: do live coding demo
- Always preserve 5 min at end for quick demos

**Key Checkpoints:**

- [ ] Pre-created index verified (32 documents)
- [ ] Search query returns relevant chunks
- [ ] LLM generates response using retrieved context

**Intervention Points:**

- Biggest challenge: Debugging embedding dimension mismatches
- Watch for: Participants skipping validation steps
- Red flag: Anyone stuck on same error for >10 min
- Success signal: "Aha!" moments when search returns relevant content

---

### 12:30 - 1:00 | Lunch (30 min)

**Facilitator Actions:**

- Take a real break yourself
- Have informal conversations about morning learnings
- Don't troubleshoot during lunch (unless critical blocker)
- Reset room for afternoon if needed

---

### 1:00 - 2:30 | Lab 05: Agent Orchestration (90 min)

**Objectives:**

- Coordinate multiple agents in a pipeline
- Implement handoff protocols between agents
- Add session context for multi-turn conversations

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 1:00-1:15 | Orchestration patterns overview |
| 1:15-1:35 | Part A: Implement QueryAgent |
| 1:35-1:55 | Part B: Implement RouterAgent |
| 1:55-2:15 | Part C: Wire up the pipeline |
| 2:15-2:30 | Test multi-turn conversations |

**Pacing Markers:**

| Checkpoint          | Time | Expected Completion |
| ------------------- | ---- | ------------------- |
| QueryAgent working  | 1:35 | 70%                 |
| RouterAgent working | 1:55 | 60%                 |
| Pipeline connected  | 2:15 | 55%                 |
| Multi-turn tested   | 2:30 | 50%                 |

**If Behind:**

- At 1:40, if <50% have QueryAgent: provide solution snippet
- At 2:00, if <40% have RouterAgent: do live coding demo
- At 2:20, if significantly behind: focus on understanding flow over coding
- Ensure everyone understands the pipeline before moving on

**Key Checkpoints:**

- [ ] QueryAgent extracts intent and entities
- [ ] RouterAgent dispatches to correct ActionAgent
- [ ] Pipeline handles multi-turn conversations
- [ ] Session context persists across turns

**Intervention Points:**

- Common issue: Agents in infinite loops
- Watch for: Over-complicated orchestration logic
- Guide toward: Simple, debuggable patterns first
- Post-lunch energy dip: Consider 5-min energizer at 2:00

### Voice & Phone Live Demo (5–10 minutes)

**Setup (before boot camp):**
- Verify `VOICE_ENABLED=true` in backend `.env`
- Verify `PHONE_ENABLED=true` (or `MOCK_MODE=true` for mock)
- Open two browser tabs: main app + `/live` for LivePage
- Have RunbookPage (`/runbook`) open on your phone or second device (private — not projected)

**Demo Flow:**
1. **Browser Voice** (2 min): Click the mic button in the main UI. Ask "How do I reset my password?" Show the transcript appearing alongside the spoken response. Point out: "Same three agents. Same pipeline. Just a different input."
2. **Phone Call** (3 min): Switch to LivePage on the projector. Call +1 (913) 217-1946 from your phone. Walk through the RunbookPage questions in order. Audience sees real-time transcript bubbles, tool calls, and agent responses.
3. **Architecture Callback** (1 min): "Notice the phone call used the SAME knowledge base, the SAME routing, the SAME ticket creation. Voice and phone are just modalities—the intelligence layer is what you built in Labs 01–05."

**Contingencies:**
- **Voice fails:** "Voice requires Azure OpenAI Realtime deployment. In mock mode, you'll see simulated responses. The architecture is identical."
- **Phone fails:** "Phone requires Azure Communication Services. Let me show you the architecture diagram instead." Switch to workshop-site Voice & Accessibility tab.
- **High latency:** "Real-time audio has ~200ms latency through WebRTC. Phone adds ACS routing. This is production-grade, not a toy."

**Pacing:**
- 🟢 Green: Demo works perfectly, audience engaged → proceed
- 🟡 Yellow: Partial demo, some features down → show architecture diagram, explain what would happen
- 🔴 Red: Complete failure → skip, reference workshop-site slides, move to Lab 06

---

### 2:30 - 3:45 | Lab 06: Deploy with azd (75 min)

**Objectives:**

- Package application for Azure deployment
- Use Azure Developer CLI for infrastructure provisioning
- Deploy working agent to cloud

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 2:30-2:40 | Deployment architecture and azd overview |
| 2:40-2:55 | Configure azd environment and templates |
| 2:55-3:20 | Run `azd up` and handle provisioning |
| 3:20-3:40 | Test deployed application |
| 3:40-3:45 | Document deployed URLs; transition to wrap-up |

**Pacing Markers:**

| Checkpoint           | Time | Expected Completion |
| -------------------- | ---- | ------------------- |
| azd configured       | 2:55 | 80%                 |
| Provisioning started | 3:20 | 70%                 |
| Deployment complete  | 3:40 | 55%                 |
| Tested in cloud      | 3:45 | 50%                 |

**Note:** Deployment has high variance due to Azure subscription limits and quotas.

**If Behind:**

- At 3:00, if <60% configured: distribute pre-made azd config
- At 3:25, if many waiting on provisioning: show what successful deployment looks like
- If quota errors: have backup resource group or demo deployed instance
- Celebrate ANY successful deployment loudly

**Key Checkpoints:**

- [ ] `azd env` shows correct configuration
- [ ] `azd provision` completes without errors
- [ ] `azd deploy` pushes application code
- [ ] Deployed endpoint responds to requests

**Intervention Points:**

- Most common issue: Azure quota exceeded
- Watch for: Wrong region selection causing capacity errors
- Red flag: Subscription spending limits about to be hit
- Have Plan B: Demo from facilitator's pre-deployed instance

---

### 3:45 - 4:00 | Wrap-up & Lab 07 Intro (15 min)

**Objectives:**

- Celebrate accomplishments
- Preview stretch content for continued learning
- Gather feedback

**Facilitator Actions:**
| Time | Activity |
|------|----------|
| 3:45-3:50 | Group share-out: biggest learning, proudest moment |
| 3:50-3:55 | Lab 07 (stretch) introduction and resources |
| 3:55-4:00 | Feedback forms, final Q&A, thank you |

**No pacing markers needed** - this is flexible closing time.

**Key Checkpoints:**

- [ ] Every participant can articulate one thing they learned
- [ ] Stretch content links shared
- [ ] Feedback collected from >80% of participants
- [ ] Participants know how to continue learning

---

## Intervention Decision Framework

Use this framework to decide when to intervene:

### Green Zone - Productive Struggle

- Participant is engaged and making attempts
- Error messages are being read and researched
- Questions are specific and show understanding
- **Action:** Observe, encourage, let them work through it

### Yellow Zone - Consider Intervening

- Same error for 5+ minutes without progress
- Visible frustration or disengagement
- Asking very broad questions ("Why doesn't it work?")
- **Action:** Check in with open question, offer hint, pair with peer

### Red Zone - Immediate Intervention

- Technical blocker affecting multiple participants
- Participant visibly upset or shutting down
- Error that cannot be resolved without facilitator help
- 10+ minutes stuck on same issue
- **Action:** Direct assistance, provide solution, or note for post-session

### Intervention Techniques

1. **The Drive-By Check:** "How's it going? What are you working on?"
2. **The Rubber Duck:** "Talk me through what you've tried"
3. **The Breadcrumb:** "Have you looked at line 42?" (don't give answer)
4. **The Pair-Up:** "Alex just solved something similar - Alex, can you share?"
5. **The Reset:** "Let's close everything and start fresh from checkpoint X"
6. **The Demo:** "Watch me do this one, then you'll try the next"

---

## Contingency Plans

### If 30+ minutes behind schedule:

- Skip extension exercises in current and remaining labs
- Convert hands-on to live coding with participation
- Compress breaks (minimum 5 min for each scheduled break)
- Lab 07 becomes take-home only

### If Azure services have outage:

- Switch to local development mode (mock endpoints)
- Use cached responses for demo purposes
- Focus on code structure and patterns over working API calls
- Document issue for post-boot camp support

### If significant portion (>30%) struggling:

- Pause for group teaching moment
- Create impromptu help tables (those ahead help those behind)
- Simplify remaining exercises
- Ensure everyone completes core path even if reduced scope

### If Voice/Phone Demo fails:

- **Voice/Phone Demo Failure:** If Azure OpenAI Realtime or ACS is unavailable, switch to mock mode (`MOCK_MODE=true`) and demonstrate the mock responses. Emphasize that mock mode uses the same code paths—only the Azure service calls are simulated.

### If running ahead:

- Allow more exploration time
- Add extension exercises
- Deeper Q&A sessions
- Start Lab 07 in-session

---

## Facilitator Self-Care

- Take breaks when participants take breaks
- Stay hydrated
- Don't absorb participant frustration
- Celebrate small wins (yours and theirs)
- It's okay if not everyone finishes everything

---

## Post-Event Checklist

- [ ] Collect all feedback forms
- [ ] Note any Azure resources that need cleanup
- [ ] Document common issues for curriculum improvement
- [ ] Send follow-up email with resources and Lab 07 materials
- [ ] Thank yourself for facilitating!
