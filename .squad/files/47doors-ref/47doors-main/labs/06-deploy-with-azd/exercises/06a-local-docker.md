# Exercise 06a: Local Docker Testing

**Duration:** 30 minutes
**Objective:** Verify your application runs correctly in Docker containers before deploying to Azure

---

## Overview

Before deploying to Azure, it's critical to verify your application works correctly in Docker containers. This exercise walks you through building, running, and testing your containerized application locally.

---

## Prerequisites

- [ ] Docker Desktop installed and running
- [ ] Lab 05 code complete (working agent pipeline)
- [ ] Terminal access to project root directory

---

## Task 1: Verify Docker Installation (5 minutes)

### 1.1 Check Docker Version

Open a terminal and verify Docker is installed:

```bash
docker --version
```

**Expected output:**

```
Docker version 24.x.x, build xxxxxxx
```

### 1.2 Verify Docker is Running

```bash
docker info
```

**Expected:** Output showing Docker server information (no errors about daemon not running).

### 1.3 Check Docker Compose

```bash
docker compose version
```

**Expected output:**

```
Docker Compose version v2.x.x
```

**Checkpoint:** All three commands succeed without errors.

---

## Task 2: Review Configuration Files (5 minutes)

### 2.1 Examine the Backend Dockerfile

Open `backend/Dockerfile` and verify it contains:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Security: non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Verify Requirements File

Ensure `backend/requirements.txt` exists and includes necessary dependencies:

```bash
cat backend/requirements.txt
```

**Expected:** File exists with FastAPI, uvicorn, pydantic, etc.

> ⚠️ Keep `backend/requirements.txt` deploy-safe. If an optional package cannot be resolved from PyPI, Docker builds in `azd up` will fail. Move non-essential tooling dependencies to a separate dev requirements file when needed.

### 2.3 Review docker-compose.yml

Open `docker-compose.yml` in the project root:

```yaml
version: "3.8"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - MOCK_MODE=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Checkpoint:** All configuration files exist and appear correct.

---

## Task 3: Build Docker Containers (10 minutes)

### 3.1 Build All Services

From the project root directory:

```bash
docker compose build
```

**Expected output:**

```
[+] Building 45.2s (12/12) FINISHED
 => [backend internal] load build definition from Dockerfile
 => [backend] FROM docker.io/library/python:3.11-slim
 => [backend] COPY requirements.txt .
 => [backend] RUN pip install --no-cache-dir -r requirements.txt
 => [backend] COPY . .
 => [backend] exporting to image
 => => naming to docker.io/library/47doors-backend
```

### 3.2 Verify Image Created

```bash
docker images | grep 47doors
```

**Expected:** Shows the backend (and frontend if applicable) images.

### 3.3 Troubleshooting Build Failures

If the build fails, check:

1. **Missing files:**

   ```bash
   ls -la backend/
   # Verify: Dockerfile, requirements.txt, app/ directory
   ```

2. **Syntax errors in Dockerfile:**

   ```bash
   docker build -t test-backend ./backend 2>&1 | head -50
   ```

3. **Network issues:**
   ```bash
   # Try with different network mode
   docker compose build --no-cache
   ```

**Checkpoint:** `docker compose build` completes without errors.

---

## Task 4: Run and Test Containers (10 minutes)

### 4.1 Start the Containers

```bash
# Start in detached mode
docker compose up -d

# Watch the startup logs
docker compose logs -f
```

Press `Ctrl+C` to stop watching logs (containers keep running).

### 4.2 Check Container Status

```bash
docker compose ps
```

**Expected output:**

```
NAME                    STATUS              PORTS
47doors-backend-1      Up (healthy)        0.0.0.0:8000->8000/tcp
```

Note: It may take 30-60 seconds for the health check to pass and show "(healthy)".

### 4.3 Test Health Endpoint

```bash
curl http://localhost:8000/api/health
```

**Expected response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "services": {
    "llm": { "status": "up", "latency_ms": 5 },
    "ticketing": { "status": "up", "latency_ms": 3 },
    "knowledge_base": { "status": "up", "latency_ms": 2 },
    "session_store": { "status": "up", "latency_ms": 1 }
  }
}
```

The key field to verify is `"status": "healthy"`. The individual service statuses will show "up" when running in mock mode.

### 4.4 Test API Documentation

Open your browser and navigate to:

- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health

### 4.5 Test Chat Endpoint (if implemented)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": null}'
```

**Expected:** JSON response with agent reply.

### Verify Voice & Phone Services (Optional)

After `docker compose up`, verify voice and phone endpoints are available:

```bash
# Voice endpoint
curl http://localhost:8000/api/realtime/health

# Phone endpoint
curl http://localhost:8000/api/phone/health
```

In mock mode, both should return `{"available": true, "mock_mode": true}`.

### 4.6 View Container Logs

```bash
# View recent logs
docker compose logs backend --tail 50

# Follow logs in real-time
docker compose logs -f backend
```

### 4.7 Troubleshooting Container Issues

If containers fail to start:

```bash
# Check container logs for errors
docker compose logs backend

# Check if port is in use
netstat -an | grep 8000
# or on Windows:
netstat -an | findstr 8000

# Restart with fresh containers
docker compose down
docker compose up -d
```

**Checkpoint:** Health endpoint returns `{"status": "healthy", ...}`.

---

## Task 5: Clean Up (5 minutes)

### 5.1 Stop Containers

```bash
docker compose down
```

### 5.2 Verify Containers Stopped

```bash
docker compose ps
```

**Expected:** No containers listed.

### 5.3 (Optional) Remove Images

Only if you need to rebuild from scratch:

```bash
docker compose down --rmi all
```

---

## Verification Checklist

Before proceeding to Exercise 06b, confirm:

- [ ] `docker --version` shows Docker is installed
- [ ] `docker compose version` shows Compose is available
- [ ] `docker compose build` completes without errors
- [ ] `docker compose up -d` starts containers
- [ ] `docker compose ps` shows healthy containers
- [ ] `curl http://localhost:8000/api/health` returns healthy status
- [ ] API documentation accessible at http://localhost:8000/docs
- [ ] `docker compose down` cleans up containers

---

## Common Issues and Solutions

### Issue: "Cannot connect to Docker daemon"

```bash
# Windows: Start Docker Desktop
# macOS: Start Docker Desktop
# Linux: Start the Docker service
sudo systemctl start docker
```

### Issue: "Port 8000 already in use"

```bash
# Find what's using the port
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Kill the process or change the port in docker-compose.yml
```

### Issue: "Container exits immediately"

```bash
# Check exit code and logs
docker compose logs backend

# Common causes:
# - Missing environment variables
# - Application error on startup
# - Incorrect CMD in Dockerfile
```

### Issue: "Health check failing"

```bash
# Check if the health endpoint works inside the container
docker compose exec backend curl http://localhost:8000/api/health

# If this fails, check the application logs
docker compose logs backend --tail 100
```

---

## Summary

You have successfully:

1. Verified Docker installation
2. Reviewed Dockerfile and docker-compose.yml configurations
3. Built Docker images for your application
4. Started and tested containers locally
5. Verified health check functionality

Your application is now ready for cloud deployment. Proceed to Exercise 06b to deploy to Azure.

---

## Next Steps

Continue to **[Exercise 06b: Azure Deployment](./06b-azure-deployment.md)** to deploy your containerized application to Azure using azd.
