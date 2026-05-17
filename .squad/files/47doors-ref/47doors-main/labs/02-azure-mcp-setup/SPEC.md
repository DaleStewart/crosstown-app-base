# Lab 02 - Azure MCP Setup: Completion Specification

## What "Done" Looks Like

Lab 02 is complete when you have a fully configured Model Context Protocol (MCP) server that enables natural language interactions with Azure resources. You should be able to:

1. Query Azure resources using @azure mentions in your AI assistant
2. List, describe, and explore Azure resources through natural language commands
3. Have a properly configured MCP settings file that persists across sessions
4. Understand the MCP architecture and how it bridges AI assistants with Azure services

A successfully completed Lab 02 means you have established the foundational infrastructure for AI-powered Azure resource management and can proceed to building more complex integrations in subsequent labs.

---

## Checkable Deliverables

### 1. MCP Server Responds to @azure Queries

**What it verifies:**
- MCP server is properly installed and running
- Azure authentication is correctly configured
- The AI assistant can communicate with the MCP server
- Basic Azure queries return meaningful responses

**Acceptance Criteria:**
- [ ] MCP server process starts without errors
- [ ] @azure queries are recognized and routed to the MCP server
- [ ] Server responds within 10 seconds for basic resource queries
- [ ] Error messages are clear and actionable when issues occur
- [ ] Server handles authentication failures gracefully

**How to Test:**
```bash
# Start the MCP server (if not auto-started)
# Then test with a basic query in your AI assistant:

@azure What subscriptions do I have access to?
```

**Expected Behavior:**
- The assistant acknowledges the @azure mention
- A list of accessible Azure subscriptions is returned
- Each subscription shows its name and ID
- Response time is under 10 seconds

**Verification Command:**
```bash
# Check MCP server status
# The exact command depends on your MCP implementation
mcp status

# Or check logs for successful connections
cat ~/.mcp/logs/azure-mcp.log | tail -20
```

---

### 2. Can List Azure Resources via Natural Language

**What it verifies:**
- Natural language processing correctly interprets resource queries
- Azure Resource Manager API integration is working
- Results are formatted in a human-readable manner
- Multiple resource types can be queried

**Acceptance Criteria:**
- [ ] Can list all resource groups in a subscription
- [ ] Can list resources within a specific resource group
- [ ] Can filter resources by type (e.g., "show me all storage accounts")
- [ ] Can describe individual resources with details
- [ ] Results include relevant metadata (name, type, location, tags)
- [ ] Handles empty results gracefully ("No resources found matching...")

**How to Test:**
```bash
# Test these natural language queries in your AI assistant:

# Query 1: List resource groups
@azure List all resource groups in my subscription

# Query 2: List resources in a group
@azure What resources are in the "rg-dev-eastus" resource group?

# Query 3: Filter by resource type
@azure Show me all storage accounts

# Query 4: Describe a specific resource
@azure Describe the storage account named "mystorageaccount"

# Query 5: Search across subscriptions
@azure Find all resources tagged with "environment=production"
```

**Expected Output Examples:**

*Resource Groups Query:*
```
Found 5 resource groups in subscription "My Subscription":

1. rg-dev-eastus (East US)
   - Resources: 12
   - Tags: environment=dev

2. rg-prod-westus (West US 2)
   - Resources: 28
   - Tags: environment=prod, team=platform

3. rg-shared-services (Central US)
   - Resources: 8
   - Tags: environment=shared
...
```

*Resource Details Query:*
```
Storage Account: mystorageaccount

- Resource Group: rg-dev-eastus
- Location: East US
- SKU: Standard_LRS
- Kind: StorageV2
- Created: 2024-01-15
- Tags:
  - environment: dev
  - owner: team-alpha
- Endpoints:
  - Blob: https://mystorageaccount.blob.core.windows.net/
  - File: https://mystorageaccount.file.core.windows.net/
```

---

### 3. Configuration Saved Correctly

**What it verifies:**
- MCP configuration persists across sessions
- Azure credentials are securely stored
- Settings file follows the correct schema
- Configuration can be validated programmatically

**Acceptance Criteria:**
- [ ] MCP configuration file exists in the expected location
- [ ] Configuration includes Azure subscription ID
- [ ] Configuration includes authentication method settings
- [ ] Sensitive values are not stored in plain text (use environment variables or secure storage)
- [ ] Configuration survives terminal/IDE restart
- [ ] Configuration can be validated with a health check command

**Configuration File Locations:**

```bash
# Check for MCP configuration in standard locations:

# Claude Code settings
cat ~/.claude/settings.json | grep -A 10 "mcp"

# Or project-level settings
cat .claude/settings.local.json | grep -A 10 "mcp"

# MCP-specific configuration
cat ~/.mcp/config.json
```

**Required Configuration Schema:**
```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}",
        "AZURE_TENANT_ID": "${AZURE_TENANT_ID}"
      }
    }
  }
}
```

**Security Checklist:**
- [ ] No API keys or secrets stored directly in configuration files
- [ ] Environment variables used for sensitive values
- [ ] Configuration file has appropriate permissions (not world-readable)
- [ ] Azure CLI or managed identity used for authentication where possible

**How to Verify:**
```bash
# Verify configuration exists and is valid JSON
cat ~/.claude/settings.json | jq '.mcpServers.azure'

# Verify environment variables are set (not the values, just existence)
echo "AZURE_SUBSCRIPTION_ID is ${AZURE_SUBSCRIPTION_ID:+set}"
echo "AZURE_TENANT_ID is ${AZURE_TENANT_ID:+set}"

# Test configuration by restarting and querying
# Close and reopen your terminal/IDE, then:
@azure List my subscriptions
```

---

## Verification Steps

### Step 1: Environment Verification

```bash
# 1. Verify Azure CLI is installed and authenticated
az --version
az account show

# 2. Verify Node.js is available (for npx)
node --version
npm --version

# 3. Verify environment variables
printenv | grep AZURE_
```

**Expected Results:**
- Azure CLI version 2.50+ installed
- Logged into Azure with `az login`
- Node.js 18+ installed
- Required environment variables are set

---

### Step 2: MCP Server Health Check

```bash
# Start the MCP server manually to verify it works
npx -y @azure/mcp-server --health-check

# Or check server logs
tail -f ~/.mcp/logs/azure-mcp.log
```

**Expected Results:**
- Server starts without errors
- Health check returns OK status
- No authentication errors in logs

---

### Step 3: Integration Test

Perform these tests in sequence in your AI assistant:

| Test | Query | Expected Result |
|------|-------|-----------------|
| 1. Basic connectivity | `@azure ping` | Server responds with status |
| 2. List subscriptions | `@azure list subscriptions` | At least one subscription returned |
| 3. List resource groups | `@azure list resource groups` | Resource groups listed with details |
| 4. Query specific resource | `@azure describe resource group rg-dev-eastus` | Detailed resource group info |
| 5. Error handling | `@azure describe nonexistent-resource-12345` | Clear error message, not a crash |

---

### Step 4: Persistence Test

1. Close your terminal/IDE completely
2. Reopen your terminal/IDE
3. Run: `@azure list subscriptions`
4. Verify the query works without reconfiguration

**Pass Criteria:** Query works immediately without any setup steps

---

## Assessment Rubric

### Total Points: 12

| Criteria | Points | Description |
|----------|--------|-------------|
| **MCP Server Operational** | 4 | Server starts, responds to queries, handles errors |
| **Natural Language Queries** | 4 | Can list, filter, and describe Azure resources |
| **Configuration Correct** | 2 | Settings persist, secure, follow schema |
| **Documentation** | 2 | Setup steps documented for future reference |

### Detailed Scoring Guide

#### MCP Server Operational (4 points)
- **4 points:** Server runs reliably, fast responses, graceful error handling
- **3 points:** Server works but occasional timeouts or unclear errors
- **2 points:** Server starts but some queries fail
- **1 point:** Server starts but most queries fail
- **0 points:** Server fails to start

#### Natural Language Queries (4 points)
- **4 points:** All 5 test queries work correctly with formatted output
- **3 points:** 4/5 queries work, minor formatting issues
- **2 points:** 3/5 queries work
- **1 point:** Only basic queries work
- **0 points:** Natural language queries not functional

#### Configuration Correct (2 points)
- **2 points:** Config persists, secure, validates successfully
- **1 point:** Config works but has security issues or doesn't persist
- **0 points:** Configuration missing or invalid

#### Documentation (2 points)
- **2 points:** Clear setup steps documented in exercises folder
- **1 point:** Partial documentation
- **0 points:** No documentation

---

## Common Failure Modes and Resolutions

### MCP Server Fails to Start

**Symptom:** Error when starting MCP server or no response to @azure queries

**Resolution:**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear npm cache and retry
npm cache clean --force
npx -y @azure/mcp-server

# Check for port conflicts
lsof -i :3000  # Or whatever port MCP uses
```

---

### Authentication Errors

**Symptom:** "Unauthorized" or "Authentication failed" errors

**Resolution:**
```bash
# Re-authenticate with Azure CLI
az login

# Verify correct subscription is selected
az account list --output table
az account set --subscription "Your Subscription Name"

# Check service principal if using one
az ad sp show --id $AZURE_CLIENT_ID
```

---

### Configuration Not Loading

**Symptom:** MCP server doesn't recognize Azure configuration

**Resolution:**
```bash
# Verify configuration file location
ls -la ~/.claude/settings.json
ls -la .claude/settings.local.json

# Validate JSON syntax
cat ~/.claude/settings.json | jq .

# Check file permissions
chmod 600 ~/.claude/settings.json
```

---

### Slow Response Times

**Symptom:** Queries take more than 10 seconds

**Resolution:**
1. Check network connectivity to Azure
2. Verify subscription has resources (empty subscriptions are fast)
3. Use more specific queries to reduce result set
4. Check MCP server resource usage (memory, CPU)

```bash
# Test direct Azure API response time
time az group list --output none

# If Azure CLI is fast but MCP is slow, issue is with MCP server
```

---

### Environment Variables Not Set

**Symptom:** "Missing required configuration" errors

**Resolution:**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"

# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Verify
echo $AZURE_SUBSCRIPTION_ID
```

---

## Success Checklist

Before proceeding to Lab 03, ensure all items are checked:

- [ ] MCP server starts without errors
- [ ] @azure queries receive responses within 10 seconds
- [ ] Can list subscriptions via natural language
- [ ] Can list resource groups via natural language
- [ ] Can list resources filtered by type
- [ ] Can describe individual resources
- [ ] Configuration file exists and is valid
- [ ] Configuration persists across restarts
- [ ] No secrets stored in plain text
- [ ] Setup steps documented in exercises folder

**Estimated Time:** 1-2 hours

**Points Possible:** 12

**Prerequisites:**
- Azure subscription with at least one resource group
- Azure CLI installed and authenticated
- Node.js 18+ installed

**Next Step:** Proceed to Lab 03 - Spec-Driven Development
