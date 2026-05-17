# 47 Doors Boot Camp Assessment Rubric

**Total Points: 125**
**Passing Score: 75 points**
**Certificate Threshold: 75 points (core labs only — the 10 bonus voice/phone points do not change the passing threshold)**

---

## Overview

This rubric provides standardized assessment criteria for the 47 Doors boot camp. Coaches should use this rubric to evaluate participant progress and provide consistent feedback across all teams.

### Scoring Summary

| Criterion | Points | Labs Assessed |
|-----------|--------|---------------|
| Environment Setup | 10 | Lab 00 |
| Intent Classification | 15 | Lab 01 |
| Azure MCP Setup | 5 | Lab 02 |
| Spec-Driven Development | 10 | Lab 03 |
| RAG Pipeline | 25 | Lab 04 |
| Agent Orchestration | 25 | Lab 05 |
| Deployment | 15 | Lab 06 |
| MCP Server (stretch) | 10 | Lab 07 |
| Voice & Phone Extensions (bonus) | 10 | Post-Lab 05 |

**Note:** The MCP Server criterion (Lab 07) is a stretch goal. Participants can earn a certificate with 75 points from core labs (00-06) without completing the stretch goal.

---

## Criterion 1: Environment Setup (10 points)

**Lab Assessed:** Lab 00

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 10 | All tools installed and configured correctly; environment fully functional |
| Proficient | 8 | All required tools working with minor configuration issues |
| Developing | 5 | Most tools installed but some configuration problems persist |
| Beginning | 3 | Partial setup with significant gaps |
| Not Attempted | 0 | No evidence of environment setup |

### Level Descriptions

**Exemplary (10 points)**
- Python 3.11+ installed and verified
- Node.js 18+ installed and verified
- All required VS Code extensions installed
- Azure CLI authenticated and configured
- Virtual environment created and activated
- All dependencies installed without errors
- Can run sample "hello world" scripts in both Python and TypeScript

**Proficient (8 points)**
- All required tools installed
- Minor issues that don't block progress (e.g., warnings during install)
- Environment functional for lab work

**Developing (5 points)**
- Most tools installed but missing 1-2 components
- Some configuration issues that may cause intermittent problems
- Requires coach assistance to complete certain tasks

**Beginning (3 points)**
- Partial installation only
- Multiple missing or misconfigured components
- Cannot proceed without significant help

**Not Attempted (0 points)**
- No evidence of setup work

### Evidence Required
- Screenshot of terminal showing Python and Node.js versions
- Screenshot of VS Code with required extensions visible
- Output of `az account show` command
- Successful execution of provided test scripts

---

## Criterion 2: Intent Classification (15 points)

**Lab Assessed:** Lab 01

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 15 | Robust intent classifier with high accuracy and edge case handling |
| Proficient | 12 | Working classifier with good accuracy on standard inputs |
| Developing | 8 | Basic classifier that handles common cases |
| Beginning | 4 | Partial implementation with significant limitations |
| Not Attempted | 0 | No evidence of implementation |

### Level Descriptions

**Exemplary (15 points)**
- Intent classifier correctly identifies 90%+ of test cases
- Handles ambiguous inputs gracefully with confidence scoring
- Implements fallback behavior for unknown intents
- Code is well-structured with clear separation of concerns
- Includes input validation and error handling
- Can explain the classification approach and trade-offs

**Proficient (12 points)**
- Intent classifier correctly identifies 75%+ of test cases
- Handles most standard inputs correctly
- Basic error handling implemented
- Code is readable and functional

**Developing (8 points)**
- Intent classifier works for obvious cases (50%+ accuracy)
- Limited handling of edge cases
- Some hardcoding or brittle logic
- Minimal error handling

**Beginning (4 points)**
- Partial implementation that demonstrates understanding of concepts
- Does not function end-to-end
- Missing significant components

**Not Attempted (0 points)**
- No classifier code submitted

### Evidence Required
- Source code for intent classification module
- Demo showing classification of at least 5 different intents
- Test output showing accuracy metrics
- Brief explanation of approach (verbal or written)

---

## Criterion 3: Azure MCP Setup (5 points)

**Lab Assessed:** Lab 02

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 5 | MCP server fully configured with working Azure integration |
| Proficient | 4 | MCP server configured with minor issues |
| Developing | 3 | Partial MCP configuration; basic functionality working |
| Beginning | 1 | MCP server installed but not properly configured |
| Not Attempted | 0 | No evidence of MCP setup |

### Level Descriptions

**Exemplary (5 points)**
- Azure MCP Server installed and running
- VS Code settings properly configured for MCP
- `@azure` queries return expected Azure resource information
- Can query subscriptions, resource groups, and resources
- Connection to Azure CLI credentials working correctly

**Proficient (4 points)**
- MCP server installed and VS Code configured
- Most `@azure` queries working
- Minor configuration issues that don't block progress

**Developing (3 points)**
- MCP server installed
- Some configuration incomplete
- Basic queries work but advanced features fail

**Beginning (1 point)**
- MCP server package installed
- Configuration not complete or not working
- No successful `@azure` queries demonstrated

**Not Attempted (0 points)**
- No evidence of MCP setup work

### Evidence Required
- Screenshot of VS Code settings showing MCP configuration
- Output of `npx @azure/mcp-server --version`
- Demo of successful `@azure List my subscriptions` query
- Demo of at least one resource group or resource query

---

## Criterion 4: Spec-Driven Development (10 points)

**Lab Assessed:** Lab 03

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 10 | Complete spec and constitution with excellent code generation |
| Proficient | 8 | Solid spec and constitution with successful code generation |
| Developing | 5 | Basic spec completed; limited code generation success |
| Beginning | 3 | Partial spec or constitution with understanding of concepts |
| Not Attempted | 0 | No evidence of spec-driven development |

### Level Descriptions

**Exemplary (10 points)**
- Complete SPEC.md following the template structure
- User stories covering all relevant perspectives (student, advisor, system)
- Detailed functional requirements with clear acceptance criteria
- Measurable success criteria defined
- Complete constitution.md with guardrails and principles
- FERPA and accessibility considerations addressed
- Successfully generated code from spec using GitHub Copilot
- Generated code matches spec requirements

**Proficient (8 points)**
- Complete SPEC.md with all major sections
- User stories cover primary perspectives
- Functional requirements clearly stated
- Constitution includes core principles and boundaries
- Code generated from spec is functional

**Developing (5 points)**
- SPEC.md partially complete
- Some user stories and requirements defined
- Constitution has basic principles
- Attempted code generation with mixed results

**Beginning (3 points)**
- Started spec or constitution document
- Demonstrates understanding of spec-driven methodology
- Document structure present but content incomplete
- No successful code generation from spec

**Not Attempted (0 points)**
- No evidence of spec or constitution work

### Evidence Required
- Completed SPEC.md file for Escalation Detection Agent
- Completed constitution.md with guardrails
- Demo of code generation using spec as Copilot context
- Brief explanation of how spec guided the code generation

---

## Criterion 5: RAG Pipeline (25 points)

**Lab Assessed:** Lab 04

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 25 | Complete RAG pipeline with optimized retrieval and generation |
| Proficient | 20 | Functional RAG pipeline with good relevance |
| Developing | 15 | Basic RAG implementation with room for improvement |
| Beginning | 8 | Partial implementation showing understanding of concepts |
| Not Attempted | 0 | No evidence of RAG implementation |

### Level Descriptions

**Exemplary (25 points)**
- Document ingestion pipeline properly chunks and indexes content
- Embeddings generated and stored in Azure AI Search
- Retrieval returns highly relevant results for queries
- Generation incorporates retrieved context effectively
- Implements citation/source attribution
- Handles queries with no relevant results gracefully
- Response quality is high with minimal hallucination
- Performance is acceptable (< 5 second response time)

**Proficient (20 points)**
- Complete RAG pipeline from ingestion to generation
- Retrieval returns relevant results most of the time
- Generation uses context but may occasionally miss nuance
- Basic error handling for edge cases
- Response time is reasonable

**Developing (15 points)**
- RAG pipeline functions end-to-end
- Retrieval sometimes returns irrelevant results
- Generation works but context integration could be improved
- Limited handling of edge cases
- Some performance issues

**Beginning (8 points)**
- Individual components (embedding, search, generation) partially working
- Pipeline not fully integrated
- Demonstrates understanding of RAG concepts
- Cannot process queries end-to-end reliably

**Not Attempted (0 points)**
- No RAG implementation evidence

### Evidence Required
- Source code for complete RAG pipeline
- Demo of document ingestion process
- Demo of at least 3 queries with retrieved context shown
- Screenshot of Azure AI Search index
- Sample responses showing source attribution

---

## Criterion 6: Agent Orchestration (25 points)

**Lab Assessed:** Lab 05

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 25 | Sophisticated multi-agent system with effective coordination |
| Proficient | 20 | Working agent orchestration with good task delegation |
| Developing | 15 | Basic orchestration with limited agent coordination |
| Beginning | 8 | Partial implementation showing understanding of agent concepts |
| Not Attempted | 0 | No evidence of agent orchestration |

### Level Descriptions

**Exemplary (25 points)**
- Multiple specialized agents with clear responsibilities
- Orchestrator effectively routes tasks to appropriate agents
- Agents communicate and share context appropriately
- Handles complex multi-step tasks requiring multiple agents
- Implements proper state management across agent interactions
- Error recovery and fallback mechanisms in place
- Can explain agent architecture and design decisions

**Proficient (20 points)**
- Multiple agents working together
- Orchestrator routes most tasks correctly
- Handles standard multi-step workflows
- Basic state management implemented
- Some error handling

**Developing (15 points)**
- Agent structure defined but coordination is basic
- Orchestrator works for simple cases
- Limited multi-step capability
- State management issues may cause inconsistencies

**Beginning (8 points)**
- Single agent or minimal agent structure
- Demonstrates understanding of orchestration concepts
- Cannot handle complex workflows
- Significant gaps in implementation

**Not Attempted (0 points)**
- No agent orchestration evidence

### Evidence Required
- Source code for agent definitions and orchestrator
- Architecture diagram showing agent interactions
- Demo of multi-step task execution
- Logs or trace output showing agent coordination
- Explanation of design decisions

---

## Criterion 7: Deployment (15 points)

**Lab Assessed:** Lab 06

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 15 | Production-ready deployment with proper configuration |
| Proficient | 12 | Successful deployment with minor issues |
| Developing | 8 | Partial deployment or significant configuration gaps |
| Beginning | 4 | Attempted deployment with limited success |
| Not Attempted | 0 | No deployment evidence |

### Level Descriptions

**Exemplary (15 points)**
- Application successfully deployed to Azure
- All services provisioned and configured correctly
- Environment variables and secrets properly managed
- Application accessible via public endpoint
- Health checks and monitoring configured
- Infrastructure as Code (Bicep/ARM) templates complete
- Can redeploy from scratch using provided scripts

**Proficient (12 points)**
- Application deployed and functional
- Most services configured correctly
- Minor issues that don't affect core functionality
- Application accessible and usable

**Developing (8 points)**
- Partial deployment completed
- Some services running but integration issues
- Application partially functional
- Manual steps required that should be automated

**Beginning (4 points)**
- Attempted deployment with limited success
- Some Azure resources created
- Application not fully functional in cloud

**Not Attempted (0 points)**
- No deployment evidence

### Evidence Required
- URL of deployed application (or screenshot if URL expired)
- Screenshot of Azure Portal showing deployed resources
- Infrastructure as Code templates (Bicep or ARM)
- Demo of application running in Azure
- Deployment logs or CI/CD pipeline output

---

## Criterion 8: MCP Server - Stretch Goal (10 points)

**Lab Assessed:** Lab 07

**Note:** This is a stretch goal. Points earned here are bonus and can push total score above 90 (from core labs), but are not required for certification.

### Point Breakdown

| Level | Points | Description |
|-------|--------|-------------|
| Exemplary | 10 | Fully functional MCP server with custom tools |
| Proficient | 8 | Working MCP server with standard implementation |
| Developing | 5 | Basic MCP server with limited functionality |
| Beginning | 2 | Partial implementation showing understanding |
| Not Attempted | 0 | No MCP server evidence |

### Level Descriptions

**Exemplary (10 points)**
- MCP server fully implemented and running
- Custom tools defined and functional
- Server properly integrated with main application
- Handles tool invocations correctly
- Error handling and validation implemented
- Documentation for custom tools provided

**Proficient (8 points)**
- MCP server running with standard tools
- Integration with main application working
- Handles most tool invocations correctly
- Basic error handling

**Developing (5 points)**
- MCP server starts and responds
- Limited tool functionality
- Integration issues with main application

**Beginning (2 points)**
- Partial MCP server code
- Demonstrates understanding of MCP concepts
- Server not fully functional

**Not Attempted (0 points)**
- No MCP server evidence

### Evidence Required
- Source code for MCP server
- Demo of MCP server handling tool requests
- Integration test showing end-to-end tool invocation
- List of implemented tools with descriptions

---

### Voice & Phone Extensions (Bonus: 10 points)

| Criterion | Points | Evidence |
|-----------|--------|----------|
| Browser voice session created (mock or live) | 3 | Screenshot of VoiceMicButton in Listening state, or `/api/realtime/health` returning available |
| Voice transcript displayed alongside spoken response | 3 | Screenshot showing dual-modality output (text + voice indicator) |
| Explained ephemeral token pattern and why 60s TTL | 2 | Written explanation or verbal explanation to coach |
| Identified what's shared between text/voice/phone pipelines | 2 | Answer: same 3-agent pipeline, same tools, same knowledge base |

**Note:** Voice/phone exercises are bonus only. Students should not attempt these until Labs 00–05 are complete. Mock mode is acceptable for full credit—the architecture understanding matters more than live Azure connectivity.

---

## Scoring Guidelines

### Calculating Final Score

1. **Core Labs (00-06):** Sum points from criteria 1-7 (maximum 105 points)
2. **Stretch Goal (Lab 07):** Add points from criterion 8 (maximum 10 points)
3. **Voice & Phone Extensions (Bonus):** Add points from criterion 9 (maximum 10 points)
4. **Total:** Sum of all earned points (maximum 125 points)

### Passing and Certification

| Score Range | Result |
|-------------|--------|
| 75-125 | Pass - Certificate Awarded |
| 65-74 | Near Pass - May resubmit specific labs |
| Below 65 | Not Passing - Significant work needed |

### Certificate Requirements

To receive a 47 Doors Boot Camp completion certificate, participants must:

1. **Achieve a minimum score of 75 points** from any combination of labs
2. **Complete all core labs (00-06)** with at least a "Beginning" score in each
3. **Demonstrate understanding** through verbal explanation or documentation
4. **Submit all required evidence** for assessed labs

### Handling Stretch Goal Scoring

The MCP Server (Lab 07) is designed as a stretch goal to challenge advanced participants:

- **Not required for certification:** Participants can earn a certificate with 75+ points from core labs alone
- **Bonus points:** Stretch goal and voice/phone bonus points can push total score above 105
- **Maximum display score:** While mathematically possible to earn 125 points, certificates will show "125" as the maximum
- **Recognition:** Participants who complete the stretch goal receive special recognition (e.g., "With Distinction" notation)
- **Voice/Phone bonus:** The 10 voice/phone bonus points do not change the 75-point passing threshold. These are purely additive for participants who explore the voice modality

### Special Circumstances

**Team Submissions:**
- All team members receive the same score unless individual contributions are clearly distinguishable
- Coaches may adjust individual scores if one team member clearly contributed more/less

**Partial Completion:**
- Award points based on the highest level fully achieved
- Do not average between levels
- When in doubt, award the lower level and provide specific feedback

**Technical Difficulties:**
- If a participant experienced documented technical issues beyond their control, coaches may:
  - Allow additional time
  - Accept alternative evidence
  - Adjust expectations proportionally

---

## Feedback Guidelines

When providing assessment feedback:

1. **Be specific:** Reference exact code, output, or behaviors observed
2. **Be constructive:** Focus on what can be improved, not just what's wrong
3. **Celebrate successes:** Acknowledge what was done well
4. **Provide next steps:** Give actionable recommendations for improvement
5. **Be encouraging:** Remember this is a learning experience

### Sample Feedback Template

```
## Assessment Feedback for [Participant/Team Name]

### Overall Score: [X]/125

### Breakdown:
- Environment Setup (Lab 00): [X]/10
- Intent Classification (Lab 01): [X]/15
- Azure MCP Setup (Lab 02): [X]/5
- Spec-Driven Development (Lab 03): [X]/10
- RAG Pipeline (Lab 04): [X]/25
- Agent Orchestration (Lab 05): [X]/25
- Deployment (Lab 06): [X]/15
- MCP Server (Lab 07 - stretch): [X]/10
- Voice & Phone Extensions (bonus): [X]/10

### Strengths:
- [Specific strength 1]
- [Specific strength 2]

### Areas for Improvement:
- [Specific area 1 with recommendation]
- [Specific area 2 with recommendation]

### Certificate Status: [Awarded/Not Yet - Resubmission Needed]
```

---

## Appendix: Quick Reference Checklist

### Environment Setup (Lab 00) - 10 pts
- [ ] Python 3.11+ verified
- [ ] Node.js 18+ verified
- [ ] VS Code extensions installed
- [ ] Azure CLI configured
- [ ] Virtual environment working
- [ ] Test scripts execute

### Intent Classification (Lab 01) - 15 pts
- [ ] Classifier code submitted
- [ ] Demo of 5+ intents
- [ ] Accuracy metrics shown
- [ ] Edge cases handled

### Azure MCP Setup (Lab 02) - 5 pts
- [ ] MCP server installed
- [ ] VS Code settings configured
- [ ] `@azure` queries working
- [ ] Azure CLI credentials connected

### Spec-Driven Development (Lab 03) - 10 pts
- [ ] SPEC.md completed
- [ ] User stories defined
- [ ] Constitution.md with guardrails
- [ ] Code generated from spec

### RAG Pipeline (Lab 04) - 25 pts
- [ ] Document ingestion working
- [ ] Azure AI Search index populated
- [ ] Retrieval returns relevant results
- [ ] Generation uses context
- [ ] Sources attributed

### Agent Orchestration (Lab 05) - 25 pts
- [ ] Multiple agents defined
- [ ] Orchestrator routes correctly
- [ ] Multi-step tasks work
- [ ] State managed properly
- [ ] Architecture documented

### Deployment (Lab 06) - 15 pts
- [ ] App deployed to Azure
- [ ] Public endpoint accessible
- [ ] IaC templates complete
- [ ] Secrets managed properly

### MCP Server (Lab 07) - 10 pts (stretch)
- [ ] Server running
- [ ] Custom tools defined
- [ ] Integration working
- [ ] Tool invocations handled

### Voice & Phone Extensions (Bonus) - 10 pts
- [ ] Browser voice session created
- [ ] Voice transcript displayed
- [ ] Ephemeral token pattern explained
- [ ] Shared pipeline components identified
