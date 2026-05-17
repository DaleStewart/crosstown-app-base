# 47 Doors Boot Camp - Coach Talking Points

Prepared messaging for phase transitions and key concepts throughout the boot camp day.

---

## 1. Opening (Welcome)

### Key Message

Welcome to 47 Doors! Today you'll build a production-ready multi-agent AI system from scratch—not just learn concepts, but ship working code that demonstrates the future of enterprise AI architecture.

### Supporting Points

- **What you'll build**: A complete multi-agent system with RAG, tool use, orchestration, and cloud deployment
- **Why multi-agent**: Single LLM calls hit walls fast—real applications need specialized agents working together, each with focused capabilities
- **The progression**: Each lab builds on the last, from basic chat to deployed enterprise solution
- **Hands-on focus**: Less lecture, more coding—you'll have working code at each checkpoint
- **Success looks like**: By end of day, you'll have a deployed Azure application you can demo and extend

### Common Questions to Anticipate

- _"Do I need Azure experience?"_ — No, we'll guide you through setup. Basic Python/TypeScript helps but isn't required.
- _"Can I use my own OpenAI key?"_ — We're using Azure OpenAI for enterprise features, but concepts transfer to any provider.
- _"What if I fall behind?"_ — Each lab has checkpoint code. You can always catch up and rejoin.
- _"Will I get the code afterward?"_ — Yes, the full repository is yours to keep and extend.

---

## 2. Lab 01 → Lab 02 Transition

### Key Message

You've built a working chat agent—now let's give it superpowers. MCP (Model Context Protocol) is how we connect AI to the real world through standardized tool interfaces.

### Supporting Points

- **Why MCP matters**: It's the USB standard for AI tools—write once, use everywhere
- **From chat to action**: Your agent can now DO things, not just talk about them
- **Standardization wins**: MCP tools work across Claude, GPT, and other models without rewriting
- **Building blocks**: Each tool you add multiplies what your agent can accomplish
- **Real-world parallel**: Think of MCP like APIs for humans—structured ways to interact with systems

### Common Questions to Anticipate

- _"How is MCP different from function calling?"_ — MCP is a protocol/standard; function calling is one implementation. MCP provides discovery, schemas, and cross-platform compatibility.
- _"Do I need to build my own MCP servers?"_ — Not today—we'll use existing ones. Lab 07 (stretch) covers building custom servers.
- _"What tools are available?"_ — Filesystem, web search, databases, APIs—the ecosystem is growing rapidly.
- _"What if Azure login is blocked by policy?"_ — We have a service-principal fallback path that keeps you moving without browser-based auth.

---

## 3. Lab 02 → Lab 03 Transition

### Key Message

Tools give agents capability, but specifications and constitutions give them purpose and boundaries. Spec-driven development means your agent knows WHAT to do, and constitutional AI ensures it does so safely.

### Supporting Points

- **Specs are contracts**: Clear specifications prevent agents from going off-script or hallucinating capabilities
- **Constitution as guardrails**: Define what your agent should and shouldn't do before it can surprise you
- **Testability**: Specs let you verify agent behavior systematically, not just hope it works
- **Enterprise requirement**: No production AI system ships without clear behavioral boundaries
- **Iterate safely**: Change specs to change behavior—much safer than prompt engineering alone

### Common Questions to Anticipate

- _"Isn't this just a system prompt?"_ — Specs are more structured and testable. They define behavior contractually, not just suggestively.
- _"How strict are constitutional constraints?"_ — They're guidelines the model follows strongly, but not hard blocks. Defense in depth matters.
- _"Can agents override their constitution?"_ — Well-designed constitutions are very difficult to bypass, but security requires multiple layers.

---

## 4. Pre-Lunch Motivation (Before Lab 04)

### Key Message

RAG is where the magic happens—this is how your agent becomes an expert on YOUR data. The next lab is the technical heart of the boot camp, and it's worth the deep dive.

### Supporting Points

- **RAG = Real value**: Generic LLMs are commodities; RAG on your data is your competitive advantage
- **Beyond keyword search**: Semantic search understands meaning, not just matching words
- **Chunking strategy matters**: How you split documents dramatically affects retrieval quality
- **Azure AI Search power**: Enterprise-grade vector search with hybrid capabilities
- **Foundation for everything**: Every subsequent lab builds on the retrieval system you create here

### Common Questions to Anticipate

- _"Why not just put everything in the context window?"_ — Cost, latency, and context limits. RAG scales to millions of documents.
- _"How do I know if retrieval is working well?"_ — We'll cover evaluation metrics. Relevance scoring tells you retrieval quality.
- _"What about hallucination?"_ — Good RAG reduces hallucination by grounding responses in retrieved facts.
- _"Can I use my own documents?"_ — Absolutely! The system works with any text content.

---

## 5. Post-Lunch Energy (Before Lab 05)

### Key Message

You have agents, tools, specs, and retrieval—now orchestration ties it all together. This is where your system becomes more than the sum of its parts.

### Supporting Points

- **Almost there**: One lab to orchestration, one to deployment—you're on the home stretch
- **Orchestration = intelligence**: Deciding which agent handles what, when to retrieve, how to combine results
- **Patterns matter**: Router, chain, parallel execution—each pattern solves different problems
- **Error handling**: Real systems need graceful degradation when components fail
- **This is the architecture**: What you build here is how production multi-agent systems actually work

### Common Questions to Anticipate

- _"How do I decide which orchestration pattern to use?"_ — Start simple (router), add complexity only when needed. We'll discuss tradeoffs.
- _"What about latency with multiple agents?"_ — Parallel execution and caching help. We'll cover optimization strategies.
- _"How do agents communicate?"_ — Through the orchestrator—it manages context and routes messages.

---

## 6. Lab 05 → Lab 06 Transition

### Key Message

Deployment makes it real—code on your laptop doesn't help anyone. Azure gives you enterprise infrastructure, security, and scalability without the ops burden.

### Supporting Points

- **From prototype to production**: Same code, now running in the cloud with real infrastructure
- **Azure benefits**: Managed identity, private endpoints, monitoring, scaling—enterprise requirements handled
- **Infrastructure as Code**: Bicep templates mean reproducible, version-controlled deployments
- **Security by default**: Azure OpenAI and AI Search integrate with enterprise security controls
- **Demo-ready**: After this lab, you can show your system to stakeholders with a real URL

### Common Questions to Anticipate

- _"How much will this cost?"_ — We're using free tiers and minimal resources. Pennies for the boot camp.
- _"Can I deploy to AWS/GCP instead?"_ — Concepts transfer; specific services differ. Today we focus on Azure.
- _"What about CI/CD?"_ — Great next step! The Bicep templates work with any CI/CD system.
- _"How do I clean up resources?"_ — We'll cover resource group deletion at the end.
- _"What if deployment fails due provider registration or region capacity?"_ — We use a decision tree: register providers, switch to non-interactive auth, and move Cosmos to an allowed region.

### Coach Script for Deployment Blockers (30-second version)

"If your deployment fails, that's normal in enterprise subscriptions. First, we switch to service-principal auth. Second, we verify provider registration. Third, if Cosmos capacity is constrained, we move Cosmos to an allowed region like `canadacentral` while keeping your app region unchanged. You can still complete the lab objective with a backend-first deployment path."

---

## Voice & Phone Demo Transition

**Key message:** "Everything you just built—the intent classifier, the router, the action agents, the RAG pipeline—it all works over voice too. Same pipeline, different input modality. And now the phone integration is production-ready and proven."

**Talking points:**
- "The phone integration proves this architecture scales beyond the browser. A caller dials a real phone number (+1-913-217-1946), and the same three-agent pipeline answers."
- "Notice what DIDN'T change: the agent prompts, the routing logic, the knowledge base. That's the power of separating interface from intelligence."
- "Voice uses ephemeral tokens with 60-second TTL—no persistent credentials in the browser. The backend uses managed identity to Azure OpenAI."
- "Raw audio is never stored. Only PII-filtered transcripts are published to the transcript bus. This is a Constitution Principle III requirement."
- "This backend stack is production-verified: ACS Call Automation → WebSocket bridge (managed identity auth) → Azure OpenAI Realtime API direct WS (verified 2026-04-21)."

---

## 7. Closing & Stretch Goal Intro

### Key Message

You did it—you built and deployed a production multi-agent AI system in one day. That's not a toy; that's a foundation you can extend into real applications.

### Supporting Points

- **Celebrate the accomplishment**: Multi-agent RAG with cloud deployment is genuinely sophisticated
- **What you built**: Chat agent → MCP tools → Specs/Constitution → RAG → Orchestration → Azure deployment
- **Stretch goal (Lab 07)**: Building your own MCP server takes you from consumer to producer of AI tools
- **Take it further**: Add more agents, connect more data sources, build domain-specific tools
- **Community continues**: Slack channel, GitHub repo, office hours—keep building together

### Common Questions to Anticipate

- _"What should I build next?"_ — Connect to your real data sources. Build tools for your actual workflows.
- _"How do I learn more about MCP?"_ — Anthropic's MCP documentation, plus the stretch lab if you have time.
- _"Can I use this at work?"_ — Yes! The architecture patterns are production-ready. Adapt to your security requirements.
- _"Where do I get help after today?"_ — GitHub issues, community Slack, and documentation in the repo.

---

## Quick Reference: Timing Cues

| Transition       | Approximate Time | Energy Level              |
| ---------------- | ---------------- | ------------------------- |
| Opening          | 9:00 AM          | High excitement           |
| Lab 01 → 02      | 10:00 AM         | Building momentum         |
| Lab 02 → 03      | 10:30 AM         | Deepening understanding   |
| Break (→ Lab 04) | 11:15 AM         | Refresh before deep dive  |
| Lunch (→ Lab 05) | 12:30 PM         | Re-fuel                   |
| Lab 05 → 06      | 2:30 PM          | Home stretch energy       |
| Voice & Phone Demo | After Lab 05 | 5–10 min | Browser voice + phone call with LivePage |
| Closing          | 4:00 PM          | Celebration + inspiration |

---

## Coach Tips

- **Read the room**: Adjust depth based on participant experience level
- **Encourage questions**: Transitions are natural pause points for clarification
- **Celebrate progress**: Each lab completion is a real accomplishment
- **Stay positive on struggles**: Getting stuck is part of learning—normalize it
- **Point to resources**: The repo has extensive documentation for self-service help
