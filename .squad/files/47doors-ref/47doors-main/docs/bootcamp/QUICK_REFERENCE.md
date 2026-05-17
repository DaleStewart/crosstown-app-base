# 47 Doors Boot Camp - Quick Reference

A cheat sheet of commonly used commands, file locations, and reference tables.

---

## Key Commands

### Git

```bash
# Clone the repository
git clone https://github.com/your-org/47doors.git

# Check status
git status

# Stage and commit
git add <file>
git commit -m "Your message"

# Push changes
git push origin main

# Pull latest changes
git pull origin main

# Create a feature branch
git checkout -b feature/my-feature
```

### Docker

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View running containers
docker ps

# View logs
docker-compose logs -f

# Rebuild a specific service
docker-compose build backend
```

### Azure CLI (az)

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<subscription-id>"

# List resource groups
az group list --output table

# Create a resource group
az group create --name <name> --location eastus

# List Azure OpenAI deployments
az cognitiveservices account deployment list \
  --resource-group <rg> --name <account> --output table

# Get Azure OpenAI endpoint
az cognitiveservices account show \
  --resource-group <rg> --name <account> \
  --query "properties.endpoint" --output tsv
```

### Azure Developer CLI (azd)

```bash
# Login
azd auth login

# Initialize project
azd init

# Deploy to Azure
azd up

# Deploy only infrastructure
azd provision

# Deploy only application
azd deploy

# View environment variables
azd env get-values

# Tear down resources
azd down
```

### Python / pip

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Check code style
ruff check .
```

### Node.js / npm

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint
```

---

## Voice & Phone Quick Reference

### Voice Health Check
```bash
curl http://localhost:8000/api/realtime/health
```

### Phone Health Check
```bash
curl http://localhost:8000/api/phone/health
```

**Live Phone Number:** +1 (913) 217-1946 — Real ACS integration, production-verified on 2026-04-21

### Voice Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `VOICE_ENABLED` | Enable browser voice | `true` |
| `AZURE_OPENAI_REALTIME_DEPLOYMENT` | Realtime API deployment name | `gpt-realtime` |
| `REALTIME_VOICE` | Voice model (marin, cedar, alloy, shimmer, echo) | `marin` |
| `MAX_VOICE_SESSION_DURATION` | Max session in seconds | `600` |

### Phone Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `PHONE_ENABLED` | Enable phone integration | `true` |
| `AZURE_ACS_ENDPOINT` | ACS resource endpoint | Yes (production) |
| `ACS_PHONE_NUMBER` | E.164 phone number (+1-913-217-1946) | Yes (production) |
| `PHONE_CALLBACK_BASE_URL` | Public HTTPS callback URL | Yes (production) |

### Key Voice/Phone URLs
| URL | Purpose |
|-----|---------|
| `/api/realtime/health` | Voice availability check |
| `/api/realtime/session` | Create ephemeral voice token |
| `/api/phone/health` | Phone availability check |
| `/api/phone/incoming` | Event Grid webhook (ACS) |
| `/api/phone/transcripts/stream` | SSE live transcript stream |
| `/ws/acs-media` | ACS media WebSocket bridge |
| `/live` | Audience-facing call transcript view |
| `/runbook` | Presenter's demo script (private) |

### Architecture Flows

**Voice:**
```
Browser mic → WebRTC → Azure OpenAI Realtime → Tool calls → 3-agent pipeline → Spoken + text response
```

**Phone:**
```
Caller → PSTN → ACS → Event Grid → Backend → WS bridge → Azure OpenAI Realtime → 3-agent pipeline → Audio → Caller
```

---

## File Locations by Lab

| Lab | Key Files |
|-----|-----------|
| **00-setup** | `labs/00-setup/verify_environment.py`, `labs/00-setup/.env.template` |
| **01-understanding-agents** | `labs/01-understanding-agents/exercises/01a-intent-classification.md`, `labs/01-understanding-agents/exercises/01b-prompt-engineering.md` |
| **02-azure-mcp-setup** | `labs/02-azure-mcp-setup/start/mcp-config.json.template`, `labs/02-azure-mcp-setup/solution/mcp-config.json` |
| **03-spec-driven-development** | `labs/03-spec-driven-development/templates/spec-template.md`, `labs/03-spec-driven-development/templates/constitution-template.md` |
| **04-build-rag-pipeline** | `labs/04-build-rag-pipeline/start/search_tool.py`, `labs/04-build-rag-pipeline/start/retrieve_agent.py` |
| **05-agent-orchestration** | `labs/05-agent-orchestration/start/query_agent.py`, `labs/05-agent-orchestration/start/router_agent.py`, `labs/05-agent-orchestration/start/action_agent.py` |
| **06-deploy-with-azd** | `labs/06-deploy-with-azd/infra/main.bicep`, `labs/06-deploy-with-azd/exercises/06a-local-docker.md` |

### Project Structure

```
47doors/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── agents/         # QueryAgent, RouterAgent, ActionAgent
│   │   ├── api/            # REST endpoints
│   │   ├── models/         # Pydantic schemas
│   │   └── services/       # Azure integrations
│   └── tests/
├── frontend/                # React TypeScript frontend
│   └── src/
│       ├── components/
│       └── services/
├── labs/                    # Boot Camp lab exercises
├── infra/                   # Azure Bicep templates
├── docs/                    # Documentation
└── docker-compose.yml
```

---

## Common Azure CLI Commands

```bash
# Search Service
az search service create --name <name> --resource-group <rg> --sku basic
az search admin-key show --service-name <name> --resource-group <rg>

# Cosmos DB
az cosmosdb create --name <name> --resource-group <rg>
az cosmosdb keys list --name <name> --resource-group <rg>

# Container Apps
az containerapp create --name <name> --resource-group <rg> \
  --environment <env-name> --image <image>
az containerapp logs show --name <name> --resource-group <rg>

# Key Vault
az keyvault create --name <name> --resource-group <rg>
az keyvault secret set --vault-name <name> --name <secret-name> --value <value>
az keyvault secret show --vault-name <name> --name <secret-name>
```

---

## GitHub Copilot Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Accept suggestion | `Tab` | `Tab` |
| Dismiss suggestion | `Esc` | `Esc` |
| Next suggestion | `Alt + ]` | `Option + ]` |
| Previous suggestion | `Alt + [` | `Option + [` |
| Open Copilot Chat | `Ctrl + Shift + I` | `Cmd + Shift + I` |
| Inline Chat | `Ctrl + I` | `Cmd + I` |

### Copilot Chat Commands

```
@workspace   - Ask about your entire codebase
@terminal    - Ask about terminal commands
@azure       - Query Azure resources (with MCP)
/explain     - Explain selected code
/fix         - Fix issues in selected code
/tests       - Generate tests for selected code
/doc         - Generate documentation
```

---

## Intent Categories

These are the 7 intent categories used in the 47 Doors agent:

| Intent | Description | Example Triggers |
|--------|-------------|------------------|
| `financial_aid` | FAFSA, scholarships, grants, tuition assistance | "FAFSA", "scholarship", "grant", "financial aid" |
| `registration` | Course enrollment, transcripts, graduation | "register", "enroll", "transcript", "graduation" |
| `housing` | Dormitories, roommates, move-in/move-out | "dorm", "roommate", "housing", "residence hall" |
| `it_support` | Password resets, email, Canvas/LMS problems | "password", "email", "Canvas", "login", "WiFi" |
| `academic_advising` | Degree requirements, major/minor, course planning | "major", "minor", "degree", "advisor", "prerequisite" |
| `student_accounts` | Bills, refunds, payment plans, account holds | "bill", "payment", "refund", "balance", "hold" |
| `general` | Catch-all for ambiguous or escalation queries | Complaints, multiple intents, human escalation |

---

## Department Routing Table

| Intent | Primary Department | Fallback | Ticket Prefix |
|--------|-------------------|----------|---------------|
| `financial_aid` | Financial Aid Office | Student Services | `TKT-FA-` |
| `registration` | Registrar | Academic Affairs | `TKT-REG-` |
| `housing` | Housing & Residence Life | Student Affairs | `TKT-HOU-` |
| `it_support` | IT Help Desk | General Support | `TKT-IT-` |
| `academic_advising` | Academic Advising Center | Department Advisor | `TKT-ADV-` |
| `student_accounts` | Bursar / Student Accounts | Financial Aid | `TKT-ACC-` |
| `general` | General Support / Escalation | Human Agent | `TKT-GEN-` |

---

## Agent Pipeline Flow

```
UserQuery --> QueryAgent --> RouterAgent --> ActionAgent --> Response
    ^                                                            |
    |                                                            |
    +------------------- Session Context ------------------------+
```

| Agent | Input | Output | Responsibility |
|-------|-------|--------|----------------|
| **QueryAgent** | Raw user message + session | StructuredQuery (intent, entities) | Parse, extract, classify |
| **RouterAgent** | StructuredQuery | RoutingDecision (target agent, params) | Route to correct ActionAgent |
| **ActionAgent** | RoutingDecision + session | AgentResponse (content, sources) | Execute task, generate response |

---

## Environment Variables Reference

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=knowledge-base

# Cosmos DB (optional)
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE=support-agent

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Useful URLs (Local Development)

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| API Documentation (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/api/health |
| LivePage (phone demo audience view) | http://localhost:5173/live |
| RunbookPage (presenter demo script) | http://localhost:5173/runbook |

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Port 8000 in use | `netstat -ano \| findstr :8000` then `taskkill /PID <pid> /F` |
| Python not found | Ensure `.venv` is activated |
| npm install fails | Delete `node_modules/` and `package-lock.json`, retry |
| Azure CLI not authenticated | Run `az login` |
| Docker not starting | Ensure Docker Desktop is running |
| Copilot not suggesting | Check Copilot icon in VS Code status bar |
