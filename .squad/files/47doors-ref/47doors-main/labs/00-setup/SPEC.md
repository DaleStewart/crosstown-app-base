# Lab 00 - Environment Setup: Completion Specification

## What "Done" Looks Like

Lab 00 is complete when your development environment is fully configured and all verification checks pass. You should be able to:

1. Run the verification script without errors
2. Have Azure credentials configured (or mock mode enabled)
3. Successfully hit the backend health endpoint
4. Interact with VS Code Copilot using prompts

A successfully completed Lab 00 means you are ready to proceed to Lab 01 and beyond.

---

## Checkable Deliverables

### 1. verify_environment.py Passes All Checks

**What it verifies:**
- Python 3.11+ is installed
- Node.js 18+ is installed
- Required Python packages are installed (FastAPI, Pydantic, etc.)
- Required npm packages are available
- Git is configured
- VS Code is available on PATH
- Docker is installed (optional but recommended)

**Acceptance Criteria:**
- [ ] Script exits with code 0 (success)
- [ ] All required tools show green checkmarks
- [ ] No critical errors are reported
- [ ] Python version is 3.11 or higher
- [ ] Node.js version is 18 or higher

**How to Run:**
```bash
cd labs/00-setup
python verify_environment.py
```

**Expected Output:**
```
[PASS] Python 3.11.x detected
[PASS] Node.js 18.x detected
[PASS] Git configured (user: <your-name>)
[PASS] VS Code detected
[PASS] Required Python packages installed
[PASS] Required npm packages available
[INFO] Docker available (optional)

Environment verification complete: ALL CHECKS PASSED
```

---

### 2. .env Configured with Azure Endpoints (or Mock Mode)

**What it verifies:**
- .env file exists in the project root or labs/00-setup directory
- Required environment variables are set
- Azure endpoints are valid URLs (if not in mock mode)

**Acceptance Criteria (Azure Mode):**
- [ ] `AZURE_OPENAI_ENDPOINT` is set to a valid Azure OpenAI endpoint URL
- [ ] `AZURE_OPENAI_API_KEY` is set (non-empty)
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME` is set (e.g., `gpt-4o`)
- [ ] `AZURE_SEARCH_ENDPOINT` is set to a valid Azure AI Search endpoint URL
- [ ] `AZURE_SEARCH_API_KEY` is set (non-empty)
- [ ] `USE_MOCK_MODE=false`

**Acceptance Criteria (Mock Mode):**
- [ ] `USE_MOCK_MODE=true` is set in .env
- [ ] Other Azure variables can be left as placeholder values
- [ ] Mock services will be used for all AI operations

**How to Verify:**
```bash
# Copy template and configure
cp .env.template .env

# Edit .env with your credentials (or set USE_MOCK_MODE=true)

# Verify by checking the file exists and has content
cat .env | grep -E "(AZURE_OPENAI|USE_MOCK)"
```

**Expected Configuration (Mock Mode):**
```env
USE_MOCK_MODE=true
ENVIRONMENT=development
```

**Expected Configuration (Azure Mode):**
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
USE_MOCK_MODE=false
```

---

### 3. Can Hit /api/health Endpoint Successfully

**What it verifies:**
- FastAPI backend starts without errors
- All service dependencies are available
- Health check returns expected response

**Acceptance Criteria:**
- [ ] Backend server starts on port 8000 (or configured port)
- [ ] GET request to `/api/health` returns HTTP 200
- [ ] Response JSON contains `status: "healthy"` or `status: "degraded"` (if some services unavailable)
- [ ] Response includes service health for: `llm`, `ticketing`, `knowledge_base`, `session_store`
- [ ] Response includes a valid `timestamp`

**How to Test:**
```bash
# Terminal 1: Start the backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Test the health endpoint
curl http://localhost:8000/api/health
```

**Expected Response (Mock Mode):**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T12:00:00Z",
  "services": {
    "llm": {"status": "up", "latency_ms": 1, "error": null},
    "ticketing": {"status": "up", "latency_ms": 1, "error": null},
    "knowledge_base": {"status": "up", "latency_ms": 1, "error": null},
    "session_store": {"status": "up", "latency_ms": 1, "error": null}
  }
}
```

**Alternative Test with Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/health")
assert response.status_code == 200
data = response.json()
assert data["status"] in ["healthy", "degraded"]
print("Health check passed!")
```

---

### 4. VS Code Copilot Extension Responds to Prompts

**What it verifies:**
- GitHub Copilot extension is installed in VS Code
- Copilot is authenticated and active
- Copilot Agent Mode (Chat) is functional

**Acceptance Criteria:**
- [ ] GitHub Copilot extension installed and enabled
- [ ] Copilot icon visible in VS Code status bar (not showing error state)
- [ ] Opening Copilot Chat (Ctrl+Shift+I or Cmd+Shift+I) shows the chat panel
- [ ] Typing a prompt like "Explain what FastAPI is" returns a response
- [ ] Code completions appear when typing in a Python file

**How to Verify:**

1. **Check Extension Installation:**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "GitHub Copilot"
   - Verify both "GitHub Copilot" and "GitHub Copilot Chat" are installed

2. **Test Code Completion:**
   - Open any Python file
   - Type `def calculate_` and pause
   - Copilot should suggest a completion (shown in gray text)

3. **Test Copilot Chat:**
   - Open Copilot Chat panel (Ctrl+Shift+I or View > Chat)
   - Type: "What is the purpose of the /api/health endpoint in a REST API?"
   - Verify you receive a coherent response

4. **Test Agent Mode (if available):**
   - In Copilot Chat, try using @workspace to ask about the codebase
   - Example: "@workspace What agents are defined in this project?"

**Expected Behavior:**
- Copilot responds within a few seconds
- Responses are relevant to the prompt
- No authentication errors appear

---

## Common Failure Modes and Resolutions

### Python Version Issues

**Symptom:** `verify_environment.py` reports Python version < 3.11

**Resolution:**
```bash
# Check current version
python --version

# Install Python 3.11+ from python.org or use pyenv
pyenv install 3.11.7
pyenv local 3.11.7

# Or use Windows installer from python.org
```

---

### Node.js Version Issues

**Symptom:** Node.js version < 18 detected

**Resolution:**
```bash
# Check current version
node --version

# Install Node.js 18+ using nvm (recommended)
nvm install 18
nvm use 18

# Or download from nodejs.org
```

---

### Missing Python Dependencies

**Symptom:** Import errors when starting backend

**Resolution:**
```bash
cd backend
pip install -r requirements.txt

# Or with a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

### .env File Not Found

**Symptom:** Backend fails to start with configuration errors

**Resolution:**
```bash
# Copy template to .env
cp labs/00-setup/.env.template .env

# Or for backend
cp labs/00-setup/.env.template backend/.env

# Edit with your preferred editor
code .env
```

---

### Azure Authentication Errors

**Symptom:** 401 Unauthorized errors when calling Azure services

**Resolution:**
1. Verify API key is correct (no extra spaces or newlines)
2. Verify endpoint URL is complete (includes `https://`)
3. Check that the deployment name matches your Azure OpenAI deployment
4. Ensure your Azure subscription is active
5. **Fallback:** Set `USE_MOCK_MODE=true` to continue without Azure

```bash
# Quick test of Azure credentials
curl -H "api-key: YOUR_KEY" \
  "https://YOUR-RESOURCE.openai.azure.com/openai/deployments?api-version=2025-01-01-preview"
```

---

### Health Endpoint Returns 503/Unhealthy

**Symptom:** `/api/health` returns `status: "unhealthy"`

**Resolution:**
1. Check which service is down in the response JSON
2. For LLM service issues:
   - Verify `AZURE_OPENAI_*` environment variables
   - Or enable `USE_MOCK_MODE=true`
3. For other services: Mock services should work by default
4. Check backend logs for specific error messages

```bash
# View backend logs
cd backend
uvicorn app.main:app --reload --log-level debug
```

---

### VS Code Copilot Not Working

**Symptom:** Copilot icon shows error or no suggestions appear

**Resolution:**

1. **Not Signed In:**
   - Click the Copilot icon in the status bar
   - Select "Sign in to GitHub"
   - Complete OAuth flow

2. **Subscription Required:**
   - Copilot requires a paid subscription or education access
   - Check github.com/features/copilot for subscription status

3. **Extension Disabled:**
   - Go to Extensions panel
   - Find GitHub Copilot and ensure it's enabled
   - Restart VS Code

4. **Network Issues:**
   - Check firewall/proxy settings
   - Copilot requires access to api.github.com

5. **Rate Limited:**
   - Wait a few minutes and try again
   - Check for any GitHub status issues

---

### Port Already in Use

**Symptom:** `Address already in use` error when starting backend

**Resolution:**
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill the process or use a different port
uvicorn app.main:app --port 8001

# Update API_PORT in .env if using different port
```

---

### Docker Not Available (Optional)

**Symptom:** Docker commands fail

**Resolution:**
- Docker is optional for Lab 00-05
- Docker Desktop must be running (check system tray)
- For Labs 06+, Docker is required for deployment

```bash
# Verify Docker is running
docker --version
docker ps
```

---

## Success Checklist

Before proceeding to Lab 01, ensure all items are checked:

- [ ] `verify_environment.py` passes all checks
- [ ] `.env` file is configured (mock mode or Azure credentials)
- [ ] Backend starts without errors (`uvicorn app.main:app`)
- [ ] `GET /api/health` returns HTTP 200 with healthy/degraded status
- [ ] VS Code Copilot extension is installed and responding
- [ ] You can open Copilot Chat and receive responses

**Estimated Time:** 30 minutes

**Next Step:** Proceed to Lab 01 - Understanding AI Agents
