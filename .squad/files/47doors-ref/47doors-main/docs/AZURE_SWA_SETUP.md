# ☁️ Azure Static Web Apps — Setup Guide

Move the 47 Doors runbook from GitHub Pages to Azure Static Web Apps with built-in Microsoft (Azure AD) authentication.

---

## 📋 Prerequisites

```bash
# Ensure Azure CLI is installed and you're logged in
az login
az account set --subscription 28fbebcb-147f-4171-aeb4-6bac79cfb589
```

---

## 🚀 Step 1 — Create the Azure Static Web App

```bash
az staticwebapp create \
  --name swa-47doors-runbook \
  --resource-group rg-47doors-voice \
  --location eastus2 \
  --source https://github.com/msftsean/47doors \
  --branch 002-voice-interaction \
  --app-location "docs" \
  --output-location "" \
  --login-with-github
```

> **Note:** `--login-with-github` will open a browser to authorize the GitHub integration and automatically configure the deployment token as a GitHub Actions secret.

---

## 🔑 Step 2 — Get the Deployment Token (manual alternative)

If you prefer to set the secret manually:

```bash
# Get the deployment token
az staticwebapp secrets list \
  --name swa-47doors-runbook \
  --resource-group rg-47doors-voice \
  --query "properties.apiKey" \
  --output tsv
```

Copy the output — that's your `AZURE_STATIC_WEB_APPS_API_TOKEN`.

---

## 🔐 Step 3 — Add the GitHub Secret (if not auto-configured)

```bash
# Using GitHub CLI
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN \
  --repo msftsean/47doors \
  --body "<paste-token-here>"
```

Or go to: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

---

## 🔒 Step 4 — Configure Azure AD App Registration

The `staticwebapp.config.json` references `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET`. Set these as application settings:

```bash
# Create an App Registration (or use existing)
APP_ID=$(az ad app create \
  --display-name "47doors-runbook" \
  --sign-in-audience AzureADandPersonalMicrosoftAccount \
  --query appId \
  --output tsv)

# Create a client secret
CLIENT_SECRET=$(az ad app credential reset \
  --id "$APP_ID" \
  --query password \
  --output tsv)

# Add app settings to the SWA
az staticwebapp appsettings set \
  --name swa-47doors-runbook \
  --resource-group rg-47doors-voice \
  --setting-names \
    AZURE_CLIENT_ID="$APP_ID" \
    AZURE_CLIENT_SECRET="$CLIENT_SECRET"
```

---

## 🌐 Step 5 — Get the Live URL

```bash
az staticwebapp show \
  --name swa-47doors-runbook \
  --resource-group rg-47doors-voice \
  --query "defaultHostname" \
  --output tsv
```

The site will be live at `https://<random-name>.azurestaticapps.net` 🎉

---

## 📴 Step 6 — Disable GitHub Pages (optional)

GitHub Pages and SWA can coexist, but if you want to consolidate:

1. Go to **GitHub repo → Settings → Pages**
2. Under **Source**, select **None**
3. Click **Save**

---

## ✅ Verification

```bash
# Check deployment status
az staticwebapp show \
  --name swa-47doors-runbook \
  --resource-group rg-47doors-voice \
  --query "{status:repositoryUrl, hostname:defaultHostname}" \
  --output table
```

Visit your SWA URL — you should be redirected to Microsoft login. After signing in with your Microsoft/Entra account, the runbook loads with your name shown in the top-right nav bar.

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| Auth loop / 401 on login route | Ensure `/.auth/login/aad` has `"anonymous"` role in routes |
| `AZURE_CLIENT_ID` not found | Run Step 4 to set app settings |
| Deployment token invalid | Regenerate token and update GitHub secret |
| GitHub Pages still serving | Disable Pages in repo Settings (Step 6) |
