# ☁️ Lab 02 - Azure MCP Setup

| 📋 Attribute         | Value             |
| -------------------- | ----------------- |
| ⏱️ **Duration**      | 30 minutes        |
| 📊 **Difficulty**    | ⭐⭐ Intermediate |
| 🎯 **Prerequisites** | Lab 00 completed  |

---

## 📈 Progress Tracker

```
Lab Progress: [░░░░░░░░░░] 0% - Not Started

Checkpoints:
□ Step 1: Verify Azure CLI Authentication
□ Step 2: Install Azure MCP Server
□ Step 3: Configure VS Code Settings
□ Step 4: Add MCP Configuration
□ Step 5: Restart VS Code
□ Step 6: Test Azure Queries in Agent Mode
```

---

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

1. ⚙️ **Configure Azure MCP Server for Copilot** - Set up the Model Context Protocol server to enable natural language interactions with Azure resources
2. 💬 **Test natural language Azure queries** - Use natural language Azure queries in Copilot Agent Mode to interact with your Azure environment through Copilot

---

## 🤔 What is MCP (Model Context Protocol)?

The **Model Context Protocol (MCP)** is an open standard that enables AI assistants like GitHub Copilot to interact with external tools and data sources. Think of MCP as a universal adapter that allows AI models to:

- 🔍 **Query external systems** - Access databases, APIs, and cloud resources
- ⚡ **Execute actions** - Perform operations on your behalf (with your permission)
- 📚 **Retrieve context** - Pull in relevant information to inform AI responses

### 🌟 Why MCP Matters for Azure Development

Without MCP, asking Copilot "What resources are in my resource group?" would require you to:

1. 💻 Open a terminal
2. ⌨️ Run `az resource list --resource-group myRG`
3. 📋 Parse the JSON output
4. 📝 Copy relevant information back to your conversation

With Azure MCP Server configured, you can simply ask "What resources are in my resource group?" in Copilot Agent Mode and get a natural language response directly in VS Code. 🎉

### 🏗️ MCP Architecture

```
+------------------+       +------------------+       +------------------+
|   GitHub         |       |   Azure MCP      |       |   Azure          |
|   Copilot        | <---> |   Server         | <---> |   Resource       |
|   (VS Code)      |  MCP  |   (Local)        |  REST |   Manager        |
+------------------+       +------------------+       +------------------+
                                    |
                                    v
                           +------------------+
                           |   Azure CLI      |
                           |   Credentials    |
                           +------------------+
```

The Azure MCP Server acts as a bridge between Copilot and Azure, translating natural language queries into Azure API calls and formatting responses for human consumption.

---

## 📝 Step-by-Step Instructions

### 🔹 Step 1: Verify Azure CLI Authentication

Before installing the MCP server, ensure you are authenticated with Azure CLI:

```bash
# 👀 Check current login status
az account show

# 🔐 If not logged in, authenticate
az login

# 📋 Verify the correct subscription is selected
az account list --output table
```

If interactive login is blocked by Conditional Access (`AADSTS53003`), use service principal auth:

```bash
az login --service-principal \
  -u <AZURE_CLIENT_ID> \
  -p <AZURE_CLIENT_SECRET> \
  --tenant <AZURE_TENANT_ID>

az account set --subscription <AZURE_SUBSCRIPTION_ID>
```

✅ You should see your subscription listed with `IsDefault` set to `True`.

### 🔹 Step 2: Install Azure MCP Server

The Azure MCP server package currently requires **Node.js 20+**.

```bash
# ✅ Ensure Node 20+ is active
source /usr/local/share/nvm/nvm.sh
nvm install 20
nvm use 20
node --version
```

Install and verify the MCP package via `npx`:

```bash
# ✅ Check that the MCP server is accessible
npx -y @azure/mcp@latest --version
```

You should see a version number (e.g., `1.x.x`). 🎉

### 🔹 Step 3: Configure VS Code Settings

Open VS Code settings to enable MCP support for GitHub Copilot.

1. 🖥️ Open VS Code
2. ⌨️ Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
3. 🔍 Type "Preferences: Open Settings (JSON)" and select it
4. ➕ Add the following configuration:

```json
{
  "github.copilot.chat.experimental.mcp.enabled": true,
  "github.copilot.chat.experimental.mcp.servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest"],
      "env": {}
    }
  }
}
```

> 💡 **Note:** The MCP feature may be in preview. Check the GitHub Copilot documentation for the latest configuration syntax.

### 🔹 Step 4: Add MCP Configuration to Copilot Settings

For project-specific MCP configuration, create or update the `.vscode/mcp.json` file in your workspace:

```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest"]
    }
  }
}
```

This configuration tells Copilot to use the Azure MCP Server when you make Azure tools available in Copilot Agent Mode.

### 🔹 Step 5: Restart VS Code

After making configuration changes:

1. ❌ Close VS Code completely
2. 🔄 Reopen VS Code
3. ⌨️ Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
4. 🔧 Run "Developer: Reload Window" if the MCP server doesn't initialize

### 🔹 Step 6: Test Azure Queries in Agent Mode

Open GitHub Copilot Chat in VS Code and test the following queries:

#### 🧪 Basic Connectivity Test

```
List my subscriptions
```

**Expected Response:** A list of Azure subscriptions associated with your account. ✅

#### 📁 Resource Group Query

```
What resource groups exist in my subscription?
```

**Expected Response:** A list of resource groups with their names and locations. ✅

#### 📦 Resource Inventory

```
List all resources in the [your-resource-group] resource group
```

**Expected Response:** A detailed list of Azure resources including their types, names, and locations. ✅

#### 🔍 Service-Specific Queries

Try these additional queries to explore MCP capabilities:

```
What App Services do I have deployed?
```

```
Show me the configuration for my OpenAI resource
```

```
What is the pricing tier of my Azure AI Search service?
```

---

## ✅ Deliverables Checklist

Before moving to the next lab, confirm the following:

- [ ] 🔐 Azure CLI is authenticated (`az account show` returns your account)
- [ ] 📦 Azure MCP Server is installed (`npx -y @azure/mcp@latest --version` returns a version)
- [ ] ⚙️ VS Code settings include MCP configuration
- [ ] ✅ Asking "List my Azure subscriptions" in Agent Mode returns results
- [ ] 💬 Natural language Azure queries in Agent Mode return relevant resource information

---

## 🔧 Troubleshooting

### ❌ MCP Server Not Found

**Problem:** `npx -y @azure/mcp@latest --version` returns an engine or command error

**Solution:**

1. ✅ Verify npm is installed: `npm --version`
2. ✅ Verify Node.js version is 20+: `node --version`
3. 🔄 Activate Node 20 with `nvm use 20`
4. 🌐 Verify npm registry/network connectivity

### ❌ AADSTS53003 During Login

**Problem:** Browser login succeeds but Azure CLI access is denied with error code `53003`

**Solution:**

1. Use service principal auth (Step 1 fallback)
2. Ensure the SP has RBAC on subscription/resource group
3. Use non-interactive azd auth:

```bash
azd auth login --client-id <AZURE_CLIENT_ID> --client-secret <AZURE_CLIENT_SECRET> --tenant-id <AZURE_TENANT_ID> --no-prompt
```

### ❌ Azure Queries Don't Work in Agent Mode

**Problem:** Copilot doesn't invoke Azure MCP tools

**Solution:**

1. 💾 Verify VS Code settings are saved correctly
2. 🔄 Reload VS Code window: `Ctrl+Shift+P` > "Developer: Reload Window"
3. 📦 Check that the GitHub Copilot extension is up to date
4. ✅ Ensure you have GitHub Copilot Chat enabled (not just Copilot completions)

### ❌ Authentication Errors

**Problem:** Azure queries return "Authentication failed" or "Access denied"

**Solution:**

1. 🔐 Re-authenticate with Azure CLI: `az login`
2. ✅ Verify correct subscription: `az account set --subscription "Your Subscription Name"`
3. 🔑 Check that your account has Reader permissions on the resources you're querying
4. ⏱️ Ensure your Azure CLI token hasn't expired: `az account get-access-token`

### ❌ MCP Server Crashes or Times Out

**Problem:** Queries hang or the MCP server crashes

**Solution:**

1. 📋 Check VS Code Output panel for MCP-related errors
2. 🔍 Run the MCP server manually to see error output:
   ```bash
   npx -y @azure/mcp@latest
   ```
3. 🌐 Ensure you have a stable network connection to Azure
4. ⏱️ Try increasing timeout in VS Code settings if available

### ❌ Copilot Chat Not Available

**Problem:** GitHub Copilot Chat panel doesn't appear

**Solution:**

1. 🔑 Verify you have a GitHub Copilot subscription with Chat access
2. 📦 Install the "GitHub Copilot Chat" extension separately if needed
3. 🔐 Sign out and back into GitHub in VS Code
4. 🔍 Check the VS Code Extensions panel for any Copilot errors

### ❌ Queries Return Empty or Incorrect Results

**Problem:** Azure queries work but return unexpected data

**Solution:**

1. ✅ Verify you're querying the correct subscription: `az account show`
2. 📦 Check that resources exist in the queried scope
3. 🔍 Try more specific queries with resource group names
4. 🔑 Ensure your account has appropriate RBAC permissions

### ❌ Windows-Specific Issues

**Problem:** MCP server doesn't start on Windows

**Solution:**

1. 🔧 Run VS Code as Administrator (temporarily, for testing)
2. 🔥 Check Windows Firewall isn't blocking the connection
3. 💻 Try using Command Prompt instead of PowerShell
4. ✅ Verify Node.js is in your system PATH: `where node`

---

## 🌟 How MCP Enhances Your Workflow

With Azure MCP configured, you can now:

| 🔧 Traditional Workflow    | 🚀 MCP-Enhanced Workflow   |
| -------------------------- | -------------------------- |
| 🌐 Open Azure Portal       | 💬 Ask in Copilot Agent Mode |
| 🖱️ Navigate through menus  | 🗣️ Natural language query  |
| 📋 Copy/paste resource IDs | 📝 Get inline responses    |
| 🔄 Switch between tools    | 🖥️ Stay in your IDE        |
| 📊 Manual JSON parsing     | 🤖 AI-formatted answers    |

### 💡 Example Workflow Integration

When building your AI agents in later labs, you can use MCP to:

```
What is the endpoint URL for my Azure OpenAI resource?
```

Then immediately use that information in your code without leaving VS Code. 🎉

---

## ➡️ Next Steps

Once the MCP server successfully invokes Azure MCP tools in Agent Mode, proceed to:

**[Lab 03 - Spec-Driven Development](../03-spec-driven-development/README.md)** 📝

In the next lab, you will learn how to write specifications that guide AI-assisted code generation.

---

## 🆘 Need Help?

Raise your hand or ask in the boot camp chat channel. 💬

---

## 📊 Version Matrix

| Component            | Required Version  | Tested Version |
| -------------------- | ----------------- | -------------- |
| 📦 Node.js           | 20+               | 20.20.0        |
| ☁️ Azure CLI         | 2.60+             | 2.77.0         |
| 🔌 Azure MCP Package | @azure/mcp latest | latest   |
| 🤖 GitHub Copilot    | Latest            | 1.x            |
| 🖥️ VS Code           | 1.85+             | 1.99+         |

---

<div align="center">

[← Lab 01](../01-understanding-agents/README.md) | **Lab 02** | [Lab 03 →](../03-spec-driven-development/README.md)

📅 Last Updated: 2026-02-26 | 📝 Version: 1.1.0

</div>
