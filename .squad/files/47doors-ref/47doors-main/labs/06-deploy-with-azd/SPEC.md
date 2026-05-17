# Lab 06 - Deploy with azd: Completion Specification

## What "Done" Looks Like

Lab 06 is complete when your AI agent application is successfully deployed to Azure using Azure Developer CLI (azd). You should be able to:

1. Run your application locally using Docker Compose and verify all services are healthy
2. Execute `azd up` to provision Azure infrastructure and deploy your containers
3. Access the deployed application via the Azure-provided URLs
4. Verify the health check endpoint responds with a healthy status
5. View application logs in Azure for monitoring and debugging

A successfully completed Lab 06 means your agent from Labs 04 and 05 is now running in production on Azure, accessible to users, and ready for real-world usage.

---

## Checkable Deliverables

### 1. Agent Deployed to Azure

**What it verifies:**
- Azure infrastructure is provisioned correctly
- Docker containers are built and pushed to Azure Container Registry
- Container Apps are running your application
- All environment variables and secrets are configured

**Acceptance Criteria:**
- [ ] `azd up` completes without errors
- [ ] Azure Container Registry contains your backend image
- [ ] Container App is in "Running" state
- [ ] Static Web App is deployed (if frontend included)
- [ ] Environment variables are set correctly in Container App
- [ ] Resource group contains all expected resources

**How to Test:**

```bash
# Verify azd deployment status
azd show

# Expected output shows all services with endpoints:
# Service           Endpoint
# backend           https://ca-backend-xxxx.azurecontainerapps.io
# frontend          https://xxx.azurestaticapps.net
```

```bash
# Verify container is running
az containerapp show \
  --name ca-backend \
  --resource-group rg-university-front-door-agent-dev \
  --query "properties.runningStatus"

# Expected: "Running"
```

```bash
# List all resources in the resource group
az resource list \
  --resource-group rg-university-front-door-agent-dev \
  --output table

# Expected: Container App, Container Registry, Log Analytics, etc.
```

**Verification Script:**

```bash
#!/bin/bash
# verify_deployment.sh

echo "=== Verifying Azure Deployment ==="

# Get environment values
BACKEND_URL=$(azd env get-value AZURE_CONTAINERAPP_URL 2>/dev/null)
RESOURCE_GROUP=$(azd env get-value AZURE_RESOURCE_GROUP 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo "FAIL: Backend URL not found. Run 'azd up' first."
    exit 1
fi

echo "Backend URL: $BACKEND_URL"

# Check container status
STATUS=$(az containerapp show \
  --name ca-backend \
  --resource-group $RESOURCE_GROUP \
  --query "properties.runningStatus" \
  -o tsv 2>/dev/null)

if [ "$STATUS" == "Running" ]; then
    echo "PASS: Container App is running"
else
    echo "FAIL: Container App status is $STATUS"
    exit 1
fi

echo "=== Deployment Verified ==="
```

---

### 2. Health Check Responds

**What it verifies:**
- Application is running and responding to requests
- Health check endpoint is properly implemented
- Container is healthy according to Azure's health probes
- Application can reach its dependencies (or fail gracefully)

**Acceptance Criteria:**
- [ ] `/api/health` endpoint returns HTTP 200
- [ ] Response includes status: "healthy"
- [ ] Response includes version information
- [ ] Response includes environment indicator
- [ ] Response time under 5 seconds
- [ ] Azure health probe reports container as healthy

**How to Test:**

```bash
# Get backend URL
BACKEND_URL=$(azd env get-value AZURE_CONTAINERAPP_URL)

# Test health endpoint
curl -s -w "\nHTTP Status: %{http_code}\nTime: %{time_total}s\n" \
  $BACKEND_URL/api/health

# Expected output:
# {"status": "healthy", "timestamp": "...", "services": {...}}
# HTTP Status: 200
# Time: 0.234s
```

```bash
# Test with timeout
curl --max-time 5 -s $BACKEND_URL/api/health | jq .

# Expected: JSON response within 5 seconds
```

**Verification Script:**

```python
# test_health.py
import requests
import sys

def test_health_endpoint(backend_url: str) -> bool:
    """Test the health endpoint."""
    health_url = f"{backend_url}/api/health"

    try:
        response = requests.get(health_url, timeout=5)

        # Check status code
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"

        # Check response body
        data = response.json()
        assert data.get("status") == "healthy", \
            f"Expected healthy status, got {data.get('status')}"

        # Check required fields
        assert "timestamp" in data, "Missing timestamp in response"
        assert "services" in data, "Missing services in response"

        # Check that all services are up
        for service_name, service_info in data.get("services", {}).items():
            assert service_info.get("status") == "up", \
                f"Service {service_name} is not up: {service_info}"

        print(f"PASS: Health check returned: {data}")
        return True

    except requests.exceptions.Timeout:
        print("FAIL: Health check timed out after 5 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"FAIL: Could not connect to {health_url}")
        return False
    except AssertionError as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    import os
    backend_url = os.environ.get("BACKEND_URL") or sys.argv[1]
    success = test_health_endpoint(backend_url)
    sys.exit(0 if success else 1)
```

**Test Cases:**

| Test | Expected Result |
|------|-----------------|
| GET /api/health | HTTP 200 with JSON body |
| Response has "status" | Value is "healthy" |
| Response has "timestamp" | ISO 8601 timestamp string |
| Response has "services" | Dictionary with service statuses |
| All services "status" | Value is "up" |
| Response time | Under 5 seconds |
| Repeated requests | Consistent healthy response |

---

## Verification Steps

### Step 1: Local Docker Verification

Before deploying to Azure, verify local Docker setup:

```bash
# Build and start containers
docker compose up -d --build

# Wait for health check
sleep 10

# Verify containers are healthy
docker compose ps

# Expected:
# NAME                STATUS          PORTS
# backend            Up (healthy)    0.0.0.0:8000->8000/tcp
# frontend           Up              0.0.0.0:3000->80/tcp

# Test local health endpoint
curl http://localhost:8000/api/health

# Expected: {"status": "healthy", ...}

# Clean up
docker compose down
```

### Step 2: azd Deployment Verification

```bash
# Login to Azure
azd auth login

# Deploy to Azure
azd up

# Expected output (summary):
# Provisioning Azure resources...
# ✓ Resource group created
# ✓ Container Registry created
# ✓ Container Apps Environment created
# ✓ Container App deployed
#
# Deployment complete!
# Backend URL: https://ca-backend-xxxx.azurecontainerapps.io
```

### Step 3: Production Health Verification

```bash
# Get the deployed URL
BACKEND_URL=$(azd env get-value AZURE_CONTAINERAPP_URL)

# Verify health check
curl -s $BACKEND_URL/api/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00.000Z",
#   "services": { "llm": {"status": "up"}, ... }
# }
```

### Step 4: Full Integration Verification

```bash
# Test the chat endpoint
curl -X POST $BACKEND_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": null}' | jq .

# Expected: Agent response with content and session_id
```

---

## Assessment Rubric

### Total Points: 15 (Deployment)

| Criteria | Points | Description |
|----------|--------|-------------|
| **Local Docker Test** | 3 | Application runs correctly in Docker Compose |
| **azd Deployment** | 5 | Successfully deploys to Azure with `azd up` |
| **Health Check** | 4 | Health endpoint responds correctly in production |
| **Monitoring Access** | 3 | Can view logs and verify container status |

### Detailed Scoring Guide

#### Local Docker Test (3 points)
- **3 points:** All containers build and run; health checks pass; services communicate correctly
- **2 points:** Containers run but minor issues (health check slow, some warnings)
- **1 point:** Containers build but don't run correctly together
- **0 points:** Docker build fails or containers won't start

#### azd Deployment (5 points)
- **5 points:** `azd up` succeeds; all resources created; no manual intervention needed
- **4 points:** Deployment succeeds with minor warnings
- **3 points:** Deployment requires one retry or manual fix
- **2 points:** Some resources deploy but others fail
- **0-1 points:** Deployment fails completely

#### Health Check (4 points)
- **4 points:** Health endpoint returns 200 with all required fields; response under 1 second
- **3 points:** Health endpoint works but missing some fields or slow (1-5 seconds)
- **2 points:** Health endpoint returns 200 but incorrect format
- **1 point:** Health endpoint exists but returns non-200 or times out
- **0 points:** Health endpoint not accessible

#### Monitoring Access (3 points)
- **3 points:** Can view container logs; understand log format; identify issues from logs
- **2 points:** Can access logs but limited understanding
- **1 point:** Can find logs in portal but can't filter/search
- **0 points:** Unable to access monitoring

---

## Common Failure Modes and Resolutions

### Docker Build Fails

**Symptom:** `docker compose build` exits with error

**Resolution:**
```bash
# Check build logs for specific error
docker compose build --no-cache 2>&1 | tee build.log

# Common fixes:
# 1. Missing requirements.txt
# 2. Incorrect COPY paths in Dockerfile
# 3. Network issues downloading packages

# Verify file structure
ls -la backend/
# Should include: Dockerfile, requirements.txt, app/
```

---

### azd up Fails with Permission Error

**Symptom:** "Authorization failed" or "Forbidden" during provisioning

**Resolution:**
```bash
# Re-authenticate
azd auth logout
azd auth login

# Verify subscription access
az account show
az account list-locations -o table

# Set correct subscription
az account set --subscription <subscription-id>
azd env set AZURE_SUBSCRIPTION_ID <subscription-id>
```

---

### Container Fails to Start in Azure

**Symptom:** Container App shows "Failed" or keeps restarting

**Resolution:**
```bash
# Check container logs
az containerapp logs show \
  --name ca-backend \
  --resource-group <resource-group> \
  --follow

# Common issues:
# 1. Missing environment variables
# 2. Port mismatch (should be 8000)
# 3. Health check failing

# Check environment variables
az containerapp show \
  --name ca-backend \
  --resource-group <resource-group> \
  --query "properties.template.containers[0].env"
```

---

### Health Check Times Out

**Symptom:** Health probe fails; container marked unhealthy

**Resolution:**

The default health endpoint checks all services which may cause timeouts. If you experience health check timeouts, you can either:
1. Increase the health probe timeout settings (see below)
2. Or create a simplified liveness probe that doesn't check external services

```python
# Alternative: Simple liveness endpoint in app/api/routes.py
# Add this alongside the full health check:

@router.get("/liveness")
async def liveness():
    """Fast liveness check - no external dependencies."""
    return {"status": "alive"}

# Then configure Azure Container Apps to use /api/liveness for liveness probes
# and /api/health for readiness probes
```

```bash
# Adjust health probe settings if needed
az containerapp update \
  --name ca-backend \
  --resource-group <resource-group> \
  --set configuration.ingress.probes.liveness.initialDelaySeconds=30
```

---

### Frontend Can't Reach Backend

**Symptom:** CORS errors or connection refused in browser

**Resolution:**
```python
# In backend app/main.py, configure CORS:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.azurestaticapps.net",
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

```bash
# Verify backend URL is set in frontend environment
az staticwebapp appsettings set \
  --name <static-web-app-name> \
  --setting-names VITE_API_BASE_URL=<backend-url>
```

---

## Success Checklist

Before marking Lab 06 complete, verify all items:

- [ ] Docker Compose builds without errors
- [ ] All containers start and show healthy status
- [ ] Local health endpoint returns HTTP 200
- [ ] `azd auth login` succeeds
- [ ] `azd up` completes without errors
- [ ] Azure Container App shows "Running" status
- [ ] Production health endpoint returns HTTP 200
- [ ] Health response includes status, version, and environment
- [ ] Can view container logs in Azure
- [ ] Can access the deployed frontend (if applicable)

**Estimated Time:** 90 minutes

**Points Possible:** 15 (Deployment)

**Prerequisites:**
- Lab 05 completed (working agent pipeline)
- Docker Desktop installed and running
- Azure subscription with Contributor access
- Azure CLI and azd CLI installed

**Next Step:** Boot Camp complete! Present your working AI agent to the group.
