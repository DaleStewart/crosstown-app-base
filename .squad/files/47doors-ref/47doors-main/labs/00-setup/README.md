# 🚀 Lab 00 - Environment Setup (GitHub Codespaces)

| 📋 Attribute         | Value          |
| -------------------- | -------------- |
| ⏱️ **Duration**      | 30 minutes     |
| 📊 **Difficulty**    | ⭐ Beginner    |
| 🎯 **Prerequisites** | GitHub account |

---

## 📈 Progress Tracker

```
Lab Progress: [░░░░░░░░░░] 0% - Not Started

Checkpoints:
□ Step 1: Launch Codespaces
□ Step 2: Verify Environment
□ Step 3: Get Codespaces URLs
□ Step 4: Configure CORS
□ Step 5: Azure Credentials (Optional)
□ Step 6: Start Backend
□ Step 7: Make Port Public
□ Step 8: Test Health Endpoint
□ Step 9: Start Frontend
□ Step 10: Access Application
□ Step 11: Test Chat Interface
```

---

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

- 🖥️ Launch and configure your GitHub Codespaces development environment
- 🔑 Configure Azure credentials for the boot camp environment
- 🤖 Test GitHub Copilot functionality in Codespaces
- 🌐 Verify CORS configuration for Codespaces URLs
- ✅ Confirm your development environment is ready for the remaining labs

## 📋 Prerequisites

Before starting this lab, ensure you have:

| ✅ Requirement       | 📝 Details                                      |
| -------------------- | ----------------------------------------------- |
| 🐙 GitHub Account    | With access to the 47doors repository           |
| 🤖 GitHub Copilot    | Active subscription (required for labs)         |
| ☁️ Azure Credentials | Provided by your instructor for labs 04, 05, 07 |
| 🌐 Web Browser       | Chrome, Edge, or Firefox (latest version)       |
| 🎤 Microphone         | For optional voice exercises in Lab 05 — Chrome/Edge recommended |

> 💡 **Note:** All development will be done in GitHub Codespaces - no local installation required!

## 🤔 Why GitHub Codespaces?

GitHub Codespaces provides:

- ✅ **Pre-configured environment** - Python 3.11, Node.js 18, all dependencies ready
- ✅ **Consistent across all participants** - No "works on my machine" issues
- ✅ **Cloud-based** - Access from any device with a browser
- ✅ **Integrated with VS Code** - Full IDE experience in the browser
- ✅ **GitHub Copilot ready** - AI assistance built-in

---

## 📝 Step-by-Step Instructions

### 🔹 Step 1: Launch GitHub Codespaces

1. 🔗 Navigate to the [47doors repository](https://github.com/EstablishedCorp/47doors) on GitHub
2. 🟢 Click the green **Code** button
3. 📑 Select the **Codespaces** tab
4. ➕ Click **Create codespace on main**

Your Codespaces environment will launch with:

- 🐍 Python 3.11+ installed
- 📦 Node.js 18+ installed
- 📚 All backend and frontend dependencies pre-installed
- 🤖 VS Code with GitHub Copilot extension ready

### 🔹 Step 2: Verify Your Codespaces Environment

Once your Codespace loads, open a terminal and verify the environment:

```bash
# 🐍 Check Python version (should be 3.11+)
python --version

# 📦 Check Node.js version (should be 18+)
node --version

# 🔧 Check that backend dependencies are installed
cd backend
pip list | grep fastapi

# 🎨 Check that frontend dependencies are installed
cd ../frontend
npm list react
cd ..
```

✅ All commands should return without errors. If any issues occur, see the Troubleshooting section below.

### 🔹 Step 3: Get Your Codespaces URLs

GitHub Codespaces assigns unique URLs to your environment. You'll need these for CORS configuration.

**Option A: Using Environment Variable (Easiest)** 🌟

Your Codespace name is already available in the environment:

```bash
echo $CODESPACE_NAME
```

Your URLs will be:

- 🎨 Frontend: `https://$CODESPACE_NAME-5173.app.github.dev`
- 🔧 Backend: `https://$CODESPACE_NAME-8000.app.github.dev`

**Option B: From the Ports Tab**

1. 📑 Click the **PORTS** tab at the bottom of VS Code
2. 👀 You'll see ports 5173 (frontend) and 8000 (backend) once you start the services
3. 🔗 The URLs will appear in the **Forwarded Address** column

### 🔹 Step 4: Configure CORS for Codespaces

Update the backend `.env` file with your Codespaces URLs:

```bash
cd backend

# 📄 Copy the template if .env doesn't exist
cp .env.example .env

# ✏️ Edit the .env file
code .env
```

Update the `CORS_ORIGINS` line with your Codespaces URL:

```bash
# ⚠️ IMPORTANT: Replace <your-codespace-name> with your actual codespace name from $CODESPACE_NAME
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:3000","https://opulent-waddle-97v5gjxw4v5929ppj-5173.app.github.dev","https://opulent-waddle-97v5gjxw4v5929ppj-8000.app.github.dev"]
```

**Example:**

```bash
# 📝 If $CODESPACE_NAME is "cautious-space-goggles-7rq4qppvrr63wx6q"
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:3000","https://cautious-space-goggles-7rq4qppvrr63wx6q-5173.app.github.dev","https://cautious-space-goggles-7rq4qppvrr63wx6q-5174.app.github.dev"]
```

> ⚠️ **Note:** CORS configuration is critical! Without the correct Codespaces URL, the frontend won't be able to communicate with the backend.

### 🔹 Step 5: Configure Azure Credentials (Optional for Labs 00-03)

Labs 00-03 can run entirely in **mock mode** without Azure credentials. Labs 04, 05, and 07 require live Azure OpenAI.

When you reach Lab 04, your instructor will provide Azure credentials. Add them to your `.env` file:

```bash
# ☁️ Azure OpenAI Configuration (NOT needed for Labs 00-03)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# 🔍 Azure AI Search Configuration (NOT needed for Labs 00-03)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=kb-articles

# 🎭 For Labs 00-03, ensure mock mode is enabled (default)
MOCK_MODE=true
```

> 💰 **Cost-Saving Tip:** Keep `MOCK_MODE=true` until you reach Lab 04. Mock mode uses no Azure resources and costs nothing.

### Voice Configuration (Optional — used in Lab 05 extension)

```env
# Voice / Realtime API (required for browser voice)
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime
VOICE_ENABLED=true
REALTIME_VOICE=marin

# Phone / ACS (coach demo only — students don't need these)
PHONE_ENABLED=false
# AZURE_ACS_ENDPOINT=https://your-acs.communication.azure.com
# ACS_PHONE_NUMBER=+15551234567
```

> **Note:** Voice and phone features work in mock mode (`MOCK_MODE=true`) without any Azure credentials. Students can explore voice exercises using mock mode. Phone demo is coach-led.

### 🔹 Step 6: Start the Backend Server

Start the FastAPI backend server:

```bash
cd backend

# 🔌 Activate virtual environment (already created in Codespaces)
source .venv/bin/activate

# 🚀 Start the server (bind to 0.0.0.0 for Codespaces)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> ⚠️ **Important:** The `--host 0.0.0.0` flag is required for Codespaces to make the backend accessible via the forwarded port.

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 🔹 Step 7: Make Port 8000 Public (Critical!) 🔑

By default, Codespaces ports are private. You need to make port 8000 public for the frontend to access it:

**Option A: Using gh CLI (Recommended)** 🌟

```bash
gh codespace ports visibility 8000:public -c $CODESPACE_NAME
```

**Option B: Using VS Code Ports Tab**

1. 📑 Click the **PORTS** tab at the bottom of VS Code
2. 🔍 Find port **8000** in the list
3. 🖱️ Right-click on port 8000
4. 🌐 Select **Port Visibility** → **Public**

### 🔹 Step 8: Test the Backend Health Endpoint

Open a **new terminal** (keep the backend running in the first terminal) and test the health endpoint:

```bash
# 🔗 Get your backend URL
echo "https://$CODESPACE_NAME-8000.app.github.dev/api/health"

# 🧪 Test with curl
curl https://$CODESPACE_NAME-8000.app.github.dev/api/health
```

You should see a response like:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T22:20:12.504937Z",
  "services": {
    "llm": { "status": "up", "latency_ms": 5, "error": null },
    "ticketing": { "status": "up", "latency_ms": 10, "error": null },
    "knowledge_base": { "status": "up", "latency_ms": 15, "error": null },
    "session_store": { "status": "up", "latency_ms": 2, "error": null }
  }
}
```

### Verify Voice Availability (Optional)

```bash
curl http://localhost:8000/api/realtime/health
```

**Expected output (mock mode):**
```json
{"available": true, "mock_mode": true}
```

### 🔹 Step 9: Start the Frontend Application

In a **new terminal** (keep the backend running):

```bash
cd frontend

# ⚠️ CRITICAL: Verify VITE_API_BASE_URL is EMPTY in frontend/.env
# It MUST be empty so API calls use relative paths through the Vite proxy.
# Setting it to http://localhost:8000 will break the app in Codespaces!
grep VITE_API_BASE_URL .env
# Expected output: VITE_API_BASE_URL=    (empty value)

# 🚀 Start the development server
npm run dev
```

> ⚠️ **Common Pitfall:** If `VITE_API_BASE_URL` is set to `http://localhost:8000`, the browser
> will try to call `localhost:8000` directly — which is unreachable from outside the container.
> Leave it **empty** so the Vite dev server proxies `/api` requests to the backend automatically.

You should see:

```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 🔹 Step 10: Access the Application

1. 📑 Click the **PORTS** tab at the bottom of VS Code
2. 🔍 Find port **5173** (frontend)
3. 🌐 Click the **globe icon** to open the frontend in a new browser tab

Or construct the URL manually:

```
https://<your-codespace-name>-5173.app.github.dev
```

You should see the **47 Doors - University Support** interface with the logo. 🎉

### 🔹 Step 11: Test the Chat Interface

1. 💬 In the frontend, type a test message: `"I forgot my password"`
2. 📤 Click **Send** or press Enter
3. ✅ You should receive a response from the agent with:
   - 🎫 A ticket ID (e.g., `TKT-IT-20260203-0001`)
   - 🏢 Department routing (IT Support)
   - ⏱️ Estimated response time
   - 📚 Knowledge base articles

If you see a response, congratulations! Your environment is fully set up. 🎉🎊

---

## ✅ Deliverables Checklist

Before moving to the next lab, confirm the following:

- [ ] 🚀 GitHub Codespace launched successfully
- [ ] 🐍 Python 3.11+ and Node.js 18+ verified
- [ ] 📝 Codespace name retrieved (`$CODESPACE_NAME`)
- [ ] ⚙️ Backend `.env` configured with correct CORS origins
- [ ] 🌐 Port 8000 made public
- [ ] ✅ Backend server starts without errors
- [ ] 💚 `/api/health` endpoint returns healthy status
- [ ] 🎨 Frontend application loads in browser
- [ ] 💬 Chat interface sends and receives messages successfully
- [ ] 🚫 No CORS errors in browser console (press F12 → Console tab)
- [ ] 🤖 VS Code with GitHub Copilot extension is ready

---

## 🔧 Troubleshooting

### ❌ CORS Errors in Browser Console

**Problem:** Browser console shows "Access blocked by CORS policy"

**Solution:**

1. ✅ Check that port 8000 is set to **Public** (not Private)
2. ✅ Verify your CORS_ORIGINS in `backend/.env` includes your Codespaces URL
3. 🔄 Restart the backend server after changing `.env`
4. 🧹 Clear browser cache and reload

### ❌ Backend Won't Start

**Problem:** `uvicorn` command fails or shows errors

**Solution:**

```bash
# 📂 Make sure you're in the backend directory
cd backend

# 🔌 Activate virtual environment
source .venv/bin/activate

# 🔍 Check if virtual environment is active (should show .venv path)
which python

# 🐛 Try starting with verbose logging
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### ❌ Port 8000 Shows "Private" or Won't Go Public

**Problem:** Port visibility won't change to Public

**Solution:**

```bash
# 🔧 Use gh CLI to force public
gh codespace ports visibility 8000:public -c $CODESPACE_NAME

# ✅ Verify it worked
gh codespace ports -c $CODESPACE_NAME
```

### ❌ Frontend Shows "Failed to Fetch" or "Service temporarily unavailable"

**Problem:** Chat interface shows network errors, "Service temporarily unavailable", or browser console has `ERR_CONNECTION_REFUSED` to `localhost:8000`

**Solution:**

1. ✅ **Check `frontend/.env`** — `VITE_API_BASE_URL` must be **empty** (not `http://localhost:8000`)
   ```bash
   # Should show: VITE_API_BASE_URL=   (empty)
   grep VITE_API_BASE_URL frontend/.env
   ```
2. ✅ Verify backend is running (check terminal)
3. 🧪 Test health endpoint: `curl http://localhost:8000/api/health`
4. ⚙️ Check CORS_ORIGINS in backend/.env
5. 🌐 Ensure port 8000 is Public
6. 🔍 Open browser DevTools (F12) → Network tab to see actual error
7. 🔄 After any `.env` change, restart the Vite dev server and hard-refresh browser (Ctrl+Shift+R)

### ❌ Vite Proxy Returns 500 / Empty Response (IPv4/IPv6 Mismatch)

**Problem:** `curl http://localhost:5173/api/health` returns HTTP 500 with empty body, but `curl http://localhost:8000/api/health` works fine. The backend is healthy but all API calls through the frontend fail silently.

**Diagnosis:**

```bash
# Check which addresses each server is bound to
ss -tlnp | grep -E '8000|5173'
# If Vite shows [::1]:5173 (IPv6) and uvicorn shows 0.0.0.0:8000 (IPv4), this is the issue
```

**Solution:** Edit `frontend/vite.config.ts` and change the proxy target:

```typescript
// ❌ Wrong — localhost may resolve to IPv6 ::1
target: "http://localhost:8000";
// ✅ Correct — explicit IPv4
target: "http://127.0.0.1:8000";
```

Restart the Vite dev server after making this change.

### ❌ Codespace Runs Out of Resources

**Problem:** Codespace becomes slow or unresponsive

**Solution:**

- 🛑 Stop the backend and frontend servers (Ctrl+C in terminals)
- 🗑️ Close unused terminals
- 🔄 Rebuild Codespace: **Cmd/Ctrl+Shift+P** → **Codespaces: Rebuild Container**

### ❌ GitHub Copilot Not Suggesting

**Problem:** Copilot icon shows error or suggestions don't appear

**Solution:**

1. 👀 Check Copilot icon in bottom-right status bar
2. 🔐 Ensure you're signed in to GitHub (Cmd/Ctrl+Shift+P → **GitHub: Sign In**)
3. ✅ Verify your GitHub account has active Copilot subscription
4. 🔄 Reload VS Code window: **Cmd/Ctrl+Shift+P** → **Developer: Reload Window**

### ❌ Can't Find $CODESPACE_NAME

**Problem:** `echo $CODESPACE_NAME` returns empty

**Solution:**

```bash
# 💡 The variable should be set automatically, but if not:
# Look at your browser URL - the codespace name is in the URL
# Example: https://cautious-space-goggles-abc123-5173.app.github.dev
#          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#          This is your codespace name

# Or use the gh CLI
gh codespace list
```

---

## 📖 Understanding Codespaces Lifecycle

### ⏱️ Timeouts and Persistence

- **Default timeout:** 30 minutes of inactivity
- **Maximum timeout:** 4 hours (configurable in settings)
- **Storage:** All files persist between sessions
- **Costs:** Free tier includes 120 core hours/month for personal accounts

### 🔄 When Your Codespace Stops

Your Codespace will automatically stop after inactivity. To resume:

1. 🔗 Go to https://github.com/codespaces
2. 🖱️ Click on your stopped Codespace
3. ⏳ Wait for it to restart (takes 30-60 seconds)
4. 💾 Your files and configuration persist
5. 🚀 You'll need to restart the backend and frontend servers

### 🔁 Restarting After a Stop

```bash
# Terminal 1: 🔧 Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: 🎨 Start frontend
cd frontend
npm run dev
```

---

## ➡️ Next Steps

Once all checklist items are complete, proceed to:

**[Lab 01 - Understanding Agents](../01-understanding-agents/README.md)** 🤖

---

## 🆘 Need Help?

Raise your hand or ask in the boot camp chat channel. 💬

---

## 📚 Additional Resources

- 📖 [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- 🔗 [Codespaces Port Forwarding Guide](https://docs.github.com/en/codespaces/developing-in-codespaces/forwarding-ports-in-your-codespace)
- 🤖 [GitHub Copilot in Codespaces](https://docs.github.com/en/codespaces/developing-in-codespaces/using-github-copilot-in-codespaces)

---

## 📊 Version Matrix

| Component         | Required Version | Tested Version |
| ----------------- | ---------------- | -------------- |
| 🐍 Python         | 3.11+            | 3.12.10         |
| 📦 Node.js        | 18+              | 18.19.0        |
| 🚀 FastAPI        | 0.109+           | 0.109.2        |
| ⚛️ React          | 18+              | 18.2.0         |
| 🎨 Vite           | 5+               | 5.0.12         |
| 🤖 GitHub Copilot | Latest           | 1.x            |

---

<div align="center">

**Lab 00** | [Lab 01 →](../01-understanding-agents/README.md)

📅 Last Updated: 2026-02-04 | 📝 Version: 1.0.0

</div>
