# 47 Doors Boot Camp Troubleshooting Guide

Quick reference for coaches to resolve common participant issues. Each fix should take under 5 minutes.

---

## Lab 00: Environment Setup

### Python Version Mismatch

- **Symptom**: `SyntaxError` or `ModuleNotFoundError` when running Python scripts; error messages about unsupported Python version
- **Cause**: Participant has Python < 3.11 installed or system defaults to an older version
- **Quick Fix**:
  1. Check version: `python --version` or `python3 --version`
  2. If < 3.11, install Python 3.11+ from python.org
  3. On Windows, ensure Python 3.11+ is first in PATH
  4. Use `py -3.11` on Windows to specify version explicitly

### Node.js Version Too Old

- **Symptom**: `npm install` fails with syntax errors; ES module errors; `ERR_REQUIRE_ESM`
- **Cause**: Node.js version < 18 installed
- **Quick Fix**:
  1. Check version: `node --version`
  2. Install Node 18+ via nvm: `nvm install 18 && nvm use 18`
  3. Or download directly from nodejs.org

### Azure CLI Not Authenticated

- **Symptom**: `AADSTS` errors; "Please run 'az login'" messages; 401 Unauthorized from Azure services
- **Cause**: Azure CLI session expired or never authenticated
- **Quick Fix**:
  1. Run `az login` and complete browser authentication
  2. Verify with `az account show`
  3. If wrong subscription: `az account set --subscription "<subscription-name>"`

### Docker Not Running

- **Symptom**: "Cannot connect to Docker daemon"; "docker: command not found"; container commands fail
- **Cause**: Docker Desktop not started or not installed
- **Quick Fix**:
  1. Start Docker Desktop application
  2. Wait for it to fully initialize (icon stops animating)
  3. Verify with `docker ps`
  4. On Windows, ensure WSL 2 backend is enabled in Docker settings

### .env File Missing or Misconfigured

- **Symptom**: `KeyError` for environment variables; "API key not found"; connection strings empty
- **Cause**: `.env` file missing, not copied from template, or has incorrect values
- **Quick Fix**:
  1. Copy template: `cp .env.example .env`
  2. Fill in required values from Azure portal
  3. Ensure no trailing spaces or quotes around values
  4. Restart the application/terminal to reload environment

### Frontend Returns 502 or "Service temporarily unavailable" in Codespaces

- **Symptom**: Chat returns "Service temporarily unavailable"; browser console shows `ERR_CONNECTION_REFUSED` to `localhost:8000`; HTTP 502 on the forwarded port 5173 URL
- **Cause**: `VITE_API_BASE_URL` in `frontend/.env` is set to `http://localhost:8000`. In Codespaces, the browser runs outside the container and cannot reach `localhost:8000` directly.
- **Quick Fix**:
  1. Edit `frontend/.env` and clear the value: `VITE_API_BASE_URL=` (leave empty)
  2. Restart the Vite dev server: kill the terminal running `npm run dev` and relaunch it
  3. Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R)
  4. With `VITE_API_BASE_URL` empty, API calls use relative paths (`/api/...`) and are proxied by Vite to the backend

### Vite Proxy Returns 500 with Empty Body (IPv4/IPv6 Mismatch)

- **Symptom**: `curl http://localhost:5173/api/health` returns HTTP 500 with empty body, but `curl http://localhost:8000/api/health` works fine; backend is healthy but frontend API calls fail silently
- **Cause**: Vite listens on IPv6 (`::1:5173`) and its proxy resolves `localhost` to IPv6, but uvicorn binds to IPv4 (`0.0.0.0:8000`). The proxy cannot connect.
- **Diagnosis**: Run `ss -tlnp | grep -E '8000|5173'` — if Vite shows `[::1]:5173` and uvicorn shows `0.0.0.0:8000`, this is the issue.
- **Quick Fix**:
  1. In `frontend/vite.config.ts`, change the proxy target from `http://localhost:8000` to `http://127.0.0.1:8000`
  2. Restart the Vite dev server
  3. Verify: `curl -s http://localhost:5173/api/health` should now return `{"status":"healthy",...}`

### Virtual Environment Not Activated

- **Symptom**: `ModuleNotFoundError` for installed packages; wrong Python interpreter used
- **Cause**: Participant installed packages but forgot to activate venv
- **Quick Fix**:
  1. Windows: `.venv\Scripts\activate`
  2. macOS/Linux: `source .venv/bin/activate`
  3. Verify prompt shows `(.venv)` prefix

---

## Lab 01: Intent Classification

### Intent Classification Returns Wrong Category

- **Symptom**: User queries consistently misclassified; "greeting" detected for technical questions
- **Cause**: System prompt lacks clear intent definitions or examples are ambiguous
- **Quick Fix**:
  1. Review the system prompt for clarity
  2. Add explicit examples for each intent category
  3. Use format: "If user asks about X, classify as Y"
  4. Test with edge cases before proceeding

### Classification Confidence Too Low

- **Symptom**: Model returns low confidence scores; frequently falls back to default intent
- **Cause**: Intent categories overlap or prompt doesn't request confidence scoring
- **Quick Fix**:
  1. Reduce number of intent categories (aim for 5-7 distinct intents)
  2. Add "confidence" field to expected JSON response
  3. Include instruction: "Return confidence between 0 and 1"

### Prompt Returns Unstructured Text

- **Symptom**: Model returns prose instead of JSON; parsing errors in code
- **Cause**: Missing structured output instructions in prompt
- **Quick Fix**:
  1. Add explicit JSON format instruction at end of prompt
  2. Include example JSON structure in the prompt
  3. Use: "Respond ONLY with valid JSON, no additional text"
  4. Consider using `response_format={"type": "json_object"}` if available

### API Rate Limiting

- **Symptom**: 429 errors; "Rate limit exceeded"; requests failing intermittently
- **Cause**: Too many requests in short time window
- **Quick Fix**:
  1. Add delay between requests: `time.sleep(1)`
  2. Implement exponential backoff
  3. Check Azure OpenAI quota in portal and increase if needed

---

## Lab 02: MCP Integration

### MCP Server Not Responding

- **Symptom**: Timeout errors; "Connection refused"; MCP client hangs
- **Cause**: MCP server not started, wrong port, or crashed
- **Quick Fix**:
  1. Check if server process is running
  2. Verify port matches client configuration
  3. Check server logs for startup errors
  4. Restart server: kill process and relaunch

### @azure Queries Return Empty Results

- **Symptom**: Queries with @azure prefix return nothing; "No results found"
- **Cause**: Azure resource context not properly configured or permissions missing
- **Quick Fix**:
  1. Verify Azure subscription is set: `az account show`
  2. Check resource group exists and has resources
  3. Ensure service principal has Reader role on resources
  4. Test Azure CLI directly: `az resource list`

### MCP Tool Calls Failing Silently

- **Symptom**: Tool appears to execute but returns null/undefined; no error messages
- **Cause**: Tool handler not returning result properly or async issues
- **Quick Fix**:
  1. Add console.log/print statements in tool handler
  2. Ensure tool returns a value (not just executes)
  3. Check for unhandled promise rejections
  4. Wrap handler in try/catch and log errors

### VS Code Extension Not Detecting MCP

- **Symptom**: MCP features unavailable in VS Code; extension shows disconnected
- **Cause**: Extension not configured or server URL incorrect
- **Quick Fix**:
  1. Open VS Code settings (Ctrl/Cmd + ,)
  2. Search for "MCP" settings
  3. Verify server URL matches running server
  4. Reload VS Code window (Ctrl/Cmd + Shift + P → "Reload Window")

  ### AADSTS53003 During Azure Login
  - **Symptom**: Login page shows "You don't have access to this resource" with error code `53003`; `az login` and `azd auth login` fail in Codespaces
  - **Cause**: Tenant Conditional Access blocks user-interactive Azure CLI login in the current context
  - **Quick Fix**:
    1. Use service principal auth instead of browser login:
    ```bash
    az login --service-principal -u <AZURE_CLIENT_ID> -p <AZURE_CLIENT_SECRET> --tenant <AZURE_TENANT_ID>
    az account set --subscription <AZURE_SUBSCRIPTION_ID>
    azd auth login --client-id <AZURE_CLIENT_ID> --client-secret <AZURE_CLIENT_SECRET> --tenant-id <AZURE_TENANT_ID> --no-prompt
    ```

    2. Ensure the SP has RBAC on subscription/resource group

  ### Azure MCP Package Requires Node 20+
  - **Symptom**: `npx -y @azure/mcp@latest --version` fails with engine mismatch on Node 18
  - **Cause**: `@azure/mcp` currently requires Node.js >= 20
  - **Quick Fix**:
    1. Switch Node version:
    ```bash
    source /usr/local/share/nvm/nvm.sh
    nvm install 20
    nvm use 20
    ```

    2. Retry MCP checks and Lab 02 verification

---

## Lab 03: Spec-Driven Development

### Spec File Not Being Used

- **Symptom**: Copilot generates generic code; ignores project-specific requirements
- **Cause**: Spec file not in workspace or not referenced in prompt
- **Quick Fix**:
  1. Ensure spec file is in workspace root or clearly visible
  2. Reference spec explicitly: "Following the spec in SPEC.md..."
  3. Open spec file in a tab before prompting Copilot
  4. Include key requirements directly in the prompt

### Copilot Generates Outdated Syntax

- **Symptom**: Code uses deprecated APIs; Python 2 syntax; old React patterns
- **Cause**: Copilot defaulting to common patterns from training data
- **Quick Fix**:
  1. Specify version in prompt: "Using Python 3.11+ syntax..."
  2. Add type hints to existing code as context
  3. Include modern example in prompt
  4. Reject suggestion and rephrase with version constraint

### Generated Code Doesn't Match Architecture

- **Symptom**: Code structure differs from project patterns; wrong folder placement
- **Cause**: Copilot lacks context about project architecture
- **Quick Fix**:
  1. Show existing similar file as context
  2. Describe architecture in prompt: "Following the repository pattern..."
  3. Start typing the expected structure, let Copilot complete
  4. Break into smaller prompts matching existing patterns

### Copilot Suggests Incomplete Functions

- **Symptom**: Functions missing error handling, edge cases, or return statements
- **Cause**: Prompt too brief or Copilot hit token limit
- **Quick Fix**:
  1. Add explicit requirements: "Include error handling for..."
  2. Generate in smaller pieces
  3. Use follow-up prompt: "Add error handling to the above function"
  4. Write function signature with detailed docstring first

---

## Lab 04: RAG with Azure AI Search

### Search Index Not Found

- **Symptom**: `ResourceNotFoundError`; "Index 'X' does not exist"
- **Cause**: Index not created, wrong name, or different Azure region
- **Quick Fix**:
  1. Verify index name in Azure portal matches code
  2. Check search service endpoint URL is correct
  3. Create index if missing: run indexing script
  4. Ensure search service is in expected resource group

### Embedding Generation Fails

- **Symptom**: "Model not found"; embedding API returns errors; dimension mismatch
- **Cause**: Wrong embedding model name or model not deployed
- **Quick Fix**:
  1. Verify embedding deployment name in Azure OpenAI Studio
  2. Match deployment name exactly (case-sensitive)
  3. Check model is deployed and running (not just created)
  4. Ensure embedding dimensions match index configuration

### Search Returns No Results

- **Symptom**: Empty results array; zero documents returned for valid queries
- **Cause**: Index empty, query syntax wrong, or field names mismatch
- **Quick Fix**:
  1. Verify documents were indexed: check document count in portal
  2. Test simple query in Azure portal search explorer
  3. Check searchable fields are marked correctly in index schema
  4. Try broader query or remove filters temporarily

### Search Results Not Relevant

- **Symptom**: Results returned but don't match query intent; low quality answers
- **Cause**: Poor chunking strategy, missing semantic ranking, or weak embeddings
- **Quick Fix**:
  1. Enable semantic ranking if not active
  2. Review chunk size (aim for 500-1000 tokens)
  3. Ensure chunk overlap (10-20% recommended)
  4. Add metadata filtering to narrow scope

### Vector Search Dimension Error

- **Symptom**: "Vector dimension mismatch"; index rejects documents
- **Cause**: Embedding model dimensions don't match index vector field config
- **Quick Fix**:
  1. Check embedding model dimensions (ada-002 = 1536, text-embedding-3-small = 1536)
  2. Verify index vector field has matching dimensions
  3. If mismatch, recreate index with correct dimensions
  4. Re-embed all documents with correct model

---

## Lab 05: Multi-Agent Pipeline

### Pipeline Not Connected

- **Symptom**: First agent runs but subsequent agents never execute; pipeline hangs
- **Cause**: Agent output not being passed as input to next agent; async issues
- **Quick Fix**:
  1. Add logging between agent calls to trace flow
  2. Verify output format matches expected input
  3. Check for `await` on async agent calls
  4. Ensure pipeline orchestrator handles agent results

### Agents Not Communicating

- **Symptom**: Each agent works independently but doesn't receive context from others
- **Cause**: Context/memory not shared between agents; isolated state
- **Quick Fix**:
  1. Implement shared context object passed through pipeline
  2. Use explicit handoff messages between agents
  3. Add previous agent's output to next agent's prompt
  4. Consider message queue or shared memory store

### Context Lost Between Steps

- **Symptom**: Later agents "forget" earlier conversation; repeated questions
- **Cause**: Context window overflow or context not being accumulated
- **Quick Fix**:
  1. Implement sliding window context management
  2. Summarize earlier context before passing forward
  3. Use explicit memory/state object throughout pipeline
  4. Reduce per-agent response verbosity

### Agent Produces Wrong Output Format

- **Symptom**: Downstream agent can't parse upstream output; type errors
- **Cause**: Inconsistent output schemas between agents
- **Quick Fix**:
  1. Define explicit output schema for each agent
  2. Add output validation/parsing between agents
  3. Use structured output (JSON mode) for all agents
  4. Add fallback handling for malformed outputs

### Infinite Loop in Agent Chain

- **Symptom**: Pipeline never completes; same agents called repeatedly
- **Cause**: Loop detection missing; termination condition not met
- **Quick Fix**:
  1. Add maximum iteration counter
  2. Implement explicit "DONE" signal from final agent
  3. Track visited states to detect cycles
  4. Add timeout for entire pipeline execution

---

## Lab 06: Deployment

### Docker Build Fails

- **Symptom**: `docker build` errors; "COPY failed"; dependency installation fails
- **Cause**: Missing files in build context, wrong paths, or base image issues
- **Quick Fix**:
  1. Verify all files referenced in COPY exist
  2. Check `.dockerignore` isn't excluding needed files
  3. Run `docker build` from correct directory (where Dockerfile is)
  4. Try `docker build --no-cache` to force fresh build

### azd Deployment Errors

- **Symptom**: `azd up` fails; provisioning errors; "deployment failed"
- **Cause**: Azure resource conflicts, quota limits, or template errors
- **Quick Fix**:
  1. Check `azd` logs: `azd show --debug`
  2. Verify subscription has quota for resources
  3. Ensure unique resource names (add random suffix)
  4. Delete failed resources and retry: `azd down && azd up`

### Missing Subscription Provider Registration

- **Symptom**: `azd up` fails with `MissingSubscriptionRegistration` for `Microsoft.App` or `Microsoft.Web`
- **Cause**: Required resource providers are not registered for the subscription
- **Quick Fix**:
  1. Ask a subscription admin to run:
     ```bash
     az provider register -n Microsoft.App --subscription <SUB_ID> --wait
     az provider register -n Microsoft.Web --subscription <SUB_ID> --wait
     ```
  2. Retry `azd up` after registration reaches `Registered`

### Cosmos DB Capacity Error by Region

- **Symptom**: Cosmos deployment fails with `ServiceUnavailable` / high demand in region
- **Cause**: Subscription region access or temporary capacity constraints
- **Quick Fix**:
  1. Use an allowed Cosmos region (for example `canadacentral`)
  2. Keep app hosting region unchanged if needed; set Cosmos location separately in Bicep
  3. If blocked during labs, deploy in mock mode first, then re-enable Cosmos in an allowed region

### Health Check Fails After Deploy

- **Symptom**: Container starts but health check fails; app marked unhealthy
- **Cause**: App not listening on expected port, slow startup, or crash on init
- **Quick Fix**:
  1. Check container logs: `az containerapp logs show`
  2. Verify app listens on port 80 or configured port
  3. Increase health check timeout/interval
  4. Test locally with same environment variables

### Environment Variables Not Set in Azure

- **Symptom**: App crashes with "key not found"; works locally but not in Azure
- **Cause**: Secrets/env vars not configured in Azure resource
- **Quick Fix**:
  1. Add secrets via Azure portal or CLI
  2. For Container Apps: `az containerapp secret set`
  3. Reference secrets in container env config
  4. Redeploy after adding secrets

### Container Runs Out of Memory

- **Symptom**: Container killed; "OOMKilled" status; app crashes under load
- **Cause**: Memory limits too low for application
- **Quick Fix**:
  1. Increase memory allocation in container config
  2. For Container Apps: modify `resources.cpu` and `resources.memory`
  3. Optimize application memory usage if limits can't increase
  4. Check for memory leaks in application code

---

## Lab 07: Custom MCP Server

### MCP Tools Not Registered

- **Symptom**: Tools don't appear in available tools list; "tool not found" errors
- **Cause**: Tool registration code not executed or schema invalid
- **Quick Fix**:
  1. Verify tool registration runs at server startup
  2. Check tool schema matches MCP specification
  3. Add logging to confirm registration code executes
  4. Ensure tool name doesn't conflict with built-in tools

### VS Code Not Recognizing Custom Server

- **Symptom**: Custom server not listed; default server used instead
- **Cause**: Server configuration not added to VS Code settings
- **Quick Fix**:
  1. Add server to VS Code settings.json under MCP config
  2. Specify correct command to start server
  3. Ensure server executable path is correct
  4. Restart VS Code after config changes

### Server Crashes on Tool Invocation

- **Symptom**: Server process exits when tool is called; connection lost
- **Cause**: Unhandled exception in tool handler
- **Quick Fix**:
  1. Add try/catch around entire tool handler
  2. Return error response instead of crashing
  3. Check server logs for stack trace
  4. Validate input parameters before processing

### Tool Response Not Displaying

- **Symptom**: Tool executes but response not shown to user; silent completion
- **Cause**: Response format incorrect or missing content field
- **Quick Fix**:
  1. Ensure response includes required `content` field
  2. Format as MCP-compliant response object
  3. Check response isn't being filtered/blocked
  4. Add logging to verify response is being sent

### Custom Tool Schema Validation Fails

- **Symptom**: Tool rejected at registration; schema errors in logs
- **Cause**: Tool definition doesn't match MCP JSON schema requirements
- **Quick Fix**:
  1. Review MCP tool schema specification
  2. Ensure all required fields present (name, description, inputSchema)
  3. Validate JSON schema syntax
  4. Use MCP SDK's built-in schema helpers if available

---

## Voice & Phone Troubleshooting

### Voice: Mic button not appearing
**Symptom:** VoiceMicButton not rendered or hidden
**5-min fix:**
1. Check `VOICE_ENABLED=true` in `.env`
2. Check browser supports `navigator.mediaDevices.getUserMedia` (requires HTTPS or localhost)
3. Check `/api/realtime/health` returns `{"available": true}`
4. If mock mode: verify `MOCK_MODE=true` — mock realtime service always reports available

### Voice: "VoiceUnavailableError" on session creation
**Symptom:** POST /api/realtime/session returns 503
**5-min fix:**
1. Check `AZURE_OPENAI_REALTIME_DEPLOYMENT` is set and matches your Azure deployment name
2. Verify deployment exists: `az cognitiveservices account deployment list --name <account> --resource-group <rg>`
3. Check managed identity has `Cognitive Services OpenAI User` role
4. Fallback: set `MOCK_MODE=true` to use mock realtime service

### Voice: WebRTC connection fails
**Symptom:** State stuck on "Connecting", never reaches "Listening"
**5-min fix:**
1. Check browser console for ICE/SDP errors
2. Ensure no corporate firewall blocking WebRTC (TURN/STUN on ports 3478/443)
3. Try a different browser (Chrome/Edge recommended, Firefox WebRTC support varies)
4. Check ephemeral token hasn't expired (60s TTL) — if session creation is slow, token may expire before SDP exchange

### Phone: Verify Production Connection

**Phone Bridge Status:** ✅ **LIVE** — Production-verified 2026-04-21 (revision azd-1776792457)
**Live Number:** +1 (913) 217-1946 — Real ACS integration with Realtime API backend

**Verification steps (2 min):**
1. Call +1 (913) 217-1946 from any phone
2. You should hear the agent greeting within 3–5 seconds
3. Open `/live` in your browser while the call is active
4. Verify you see **bidirectional transcripts**: caller speech AND agent responses rendering in real time
5. Ask "How do I reset my password?" and wait 2–3 seconds for response (same 3-agent pipeline as browser voice)

**Expected signals on `/live`:**
- "Caller:" messages appear as you speak
- Tool calls show routing, knowledge base search, and ticket creation
- "Agent:" responses appear 2–3 seconds after you finish speaking

**If call doesn't connect:**
1. Verify backend is running: `curl http://localhost:8000/api/phone/health`
2. Check `PHONE_ENABLED=true` in `.env`
3. Verify `AZURE_ACS_ENDPOINT` and `ACS_PHONE_NUMBER` are configured (production only; skip for mock mode)
4. For local dev with mock mode: set `MOCK_MODE=true` — simulated events still appear on `/live`

**If transcripts not appearing on `/live`:**
1. Check SSE connection: open browser DevTools → Network → filter for "transcripts/stream"
2. Should show long-running HTTP response with `text/event-stream`
3. Check for CORS issues if frontend and backend are on different domains

---

## General Tips for Coaches

1. **Start with the basics**: Always verify environment setup first (Python, Node, Azure CLI, Docker)
2. **Check the logs**: Most issues leave traces in application or service logs
3. **Isolate the problem**: Test components individually before debugging integration
4. **Verify credentials**: Many issues stem from expired or incorrect authentication
5. **Restart cleanly**: Sometimes a clean restart resolves transient issues
6. **Check network**: Firewalls and proxies can block Azure service connections
7. **Read error messages carefully**: They often contain the exact solution

---

## Quick Reference: Common Error Messages

| Error Message           | Likely Cause                             | First Step                               |
| ----------------------- | ---------------------------------------- | ---------------------------------------- |
| `AADSTS700016`          | Wrong Azure tenant                       | `az logout && az login`                  |
| `Connection refused`    | Service not running                      | Start the service/server                 |
| `ModuleNotFoundError`   | Package not installed or venv not active | Activate venv, pip install               |
| `401 Unauthorized`      | Invalid or expired credentials           | Re-authenticate                          |
| `429 Too Many Requests` | Rate limiting                            | Add delays, check quotas                 |
| `ResourceNotFoundError` | Resource doesn't exist                   | Verify resource name/region              |
| `ECONNREFUSED`          | Port not listening                       | Check service is running on correct port |
| `JSON parse error`      | Malformed response                       | Check prompt for JSON instructions       |
