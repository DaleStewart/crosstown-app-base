targetScope = 'resourceGroup'

// ─────────────────────────────────────────────────────────────────────────────
// Parameters
// ─────────────────────────────────────────────────────────────────────────────

@description('Azure Developer CLI environment name — used as a short suffix throughout resource naming and as a tag value')
@minLength(1)
@maxLength(64)
param environmentName string

@description('Primary Azure region for all resources')
param location string = 'eastus2'

@description('Principal ID of the user running azd up; receives contributor-level data-plane roles for local dev')
param principalId string

// ─────────────────────────────────────────────────────────────────────────────
// Variables
// ─────────────────────────────────────────────────────────────────────────────

var abbrs = loadJsonContent('abbreviations.json')

// uniqueString already returns 13 chars; take() is explicit about the contract
var resourceToken = take(toLower(uniqueString(subscription().id, environmentName, resourceGroup().id)), 13)

var tags = { 'azd-env-name': environmentName }

// Placeholder image — azd replaces this with the real built image after first `azd build`
var placeholderImage = 'mcr.microsoft.com/k8se/quickstart:latest'

// ── Resource names ────────────────────────────────────────────────────────────
// Pattern: <abbr>-<env>-<token>  (truncated to provider limits where needed)

var logAnalyticsName   = '${abbrs.operationalInsightsWorkspaces}-${environmentName}-${resourceToken}'
var appInsightsName    = '${abbrs.insightsComponents}-${environmentName}-${resourceToken}'
// id- prefix is fixed per spec: id-mta-<env>-<token>
var identityName       = 'id-mta-${environmentName}-${resourceToken}'
// KV: 3–24 chars, alphanumeric + hyphens
var keyVaultName       = take('${abbrs.keyVaultsVaults}-${environmentName}-${resourceToken}', 24)
// ACR: 5–50 alphanumeric only (no hyphens)
var acrName            = take('${abbrs.containerRegistries}${replace(environmentName, '-', '')}${resourceToken}', 50)
var caEnvName          = '${abbrs.appManagedEnvironments}-${environmentName}-${resourceToken}'
// Foundry storage: 3–24 alphanumeric only
var foundryStorageName = take('${abbrs.storageStorageAccounts}${replace(environmentName, '-', '')}${resourceToken}', 24)
// AOAI Cognitive Services account: 2–64 chars
var aoaiName           = take('${abbrs.cognitiveServicesAccounts}-oai-${environmentName}-${resourceToken}', 64)
// AI Foundry Hub & Project workspaces (kind=Hub|Project): regex ^[a-zA-Z0-9][a-zA-Z0-9_-]{2,32}$ (33-char max).
// Wrap with take(..., 32) for 1-char safety margin; envName + resourceToken still combine for uniqueness.
var foundryHubName     = take('${abbrs.machineLearningServicesWorkspaces}-hub-${environmentName}-${resourceToken}', 32)
var foundryProjectName = take('${abbrs.machineLearningServicesWorkspaces}-proj-${environmentName}-${resourceToken}', 32)
// Search: 2–60 chars
var searchName         = take('${abbrs.searchSearchServices}-${environmentName}-${resourceToken}', 60)
// Cosmos: 3–44 chars, lowercase
var cosmosName         = take('${abbrs.documentDBDatabaseAccounts}-${environmentName}-${resourceToken}', 44)
// Postgres Flexible Server: 3–63 chars
var postgresName       = take('${abbrs.dbserversFlexible}-${environmentName}-${resourceToken}', 63)
// Speech account: 2–64 chars
var speechName         = take('${abbrs.cognitiveServicesAccounts}-spch-${environmentName}-${resourceToken}', 64)

// ─────────────────────────────────────────────────────────────────────────────
// Modules
// ─────────────────────────────────────────────────────────────────────────────

@description('Log Analytics workspace — telemetry sink for App Insights and ACA log shipping')
module logAnalytics 'modules/logAnalytics.bicep' = {
  name: 'logAnalytics'
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

@description('Application Insights — workspace-based, wired to Log Analytics')
module appInsights 'modules/appInsights.bicep' = {
  name: 'appInsights'
  params: {
    name: appInsightsName
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

@description('User-assigned managed identity — shared by all three Container Apps')
module identity 'modules/identity.bicep' = {
  name: 'identity'
  params: {
    name: identityName
    location: location
    tags: tags
  }
}

@description('Key Vault (RBAC mode) — stores the App Insights connection string for secretRef injection')
module keyVault 'modules/keyVault.bicep' = {
  name: 'keyVault'
  params: {
    name: keyVaultName
    location: location
    tags: tags
    appInsightsConnectionString: appInsights.outputs.connectionString
  }
}

@description('Container Registry (Basic SKU, admin disabled) — UAMI uses AcrPull for image pull')
module acr 'modules/containerRegistry.bicep' = {
  name: 'containerRegistry'
  params: {
    name: acrName
    location: location
    tags: tags
  }
}

@description('Container Apps Managed Environment — single env; dev vs demo is a separate azd environment, not a separate Bicep run')
module caEnv 'modules/containerAppsEnv.bicep' = {
  name: 'containerAppsEnv'
  params: {
    name: caEnvName
    location: location
    tags: tags
    logAnalyticsCustomerId: logAnalytics.outputs.customerId
    logAnalyticsPrimarySharedKey: logAnalytics.outputs.primarySharedKey
  }
}

@description('AI Foundry hub + project + Azure OpenAI account with gpt-4.1 and gpt-realtime-1.5 deployments')
module foundry 'modules/foundry.bicep' = {
  name: 'foundry'
  params: {
    hubName: foundryHubName
    projectName: foundryProjectName
    aoaiAccountName: aoaiName
    storageAccountName: foundryStorageName
    keyVaultId: keyVault.outputs.id
    appInsightsId: appInsights.outputs.id
    location: location
    tags: tags
  }
}

@description('Azure AI Search (Basic SKU, semantic search free tier) — endpoint only; index creation in scripts/load_search_index.py')
module search 'modules/search.bicep' = {
  name: 'search'
  params: {
    name: searchName
    location: location
    tags: tags
  }
}

@description('Cosmos DB for NoSQL (Serverless) — database mta with incidents and conversations containers')
module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmos'
  params: {
    name: cosmosName
    location: location
    tags: tags
  }
}

@description('PostgreSQL Flexible Server (Burstable B1ms, Entra-only auth) — idle skeleton; Extension 09 wires this in')
module postgres 'modules/postgres.bicep' = {
  name: 'postgres'
  params: {
    name: postgresName
    location: location
    tags: tags
  }
}

@description('Azure Speech Services (S0) — voice fallback path; accessed via managed identity')
module speech 'modules/speech.bicep' = {
  name: 'speech'
  params: {
    name: speechName
    location: location
    tags: tags
  }
}

// ── Shared secret definition reused by all three Container Apps ──────────────
// The App Insights connection string is stored in KV and injected via secretRef
// so it never appears in plain container environment variables.
var aiConnStringSecretName = 'appinsights-connection-string'

var aiConnStringKvSecret = [
  {
    name: aiConnStringSecretName
    keyVaultUrl: keyVault.outputs.appInsightsSecretUri
    identity: identity.outputs.id
  }
]

var aiConnStringEnvVar = [
  {
    name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    secretRef: aiConnStringSecretName
  }
]

// Common environment variables injected into every container app
var commonEnvVars = [
  { name: 'AZURE_CLIENT_ID',                      value: identity.outputs.clientId }
  { name: 'AZURE_OPENAI_ENDPOINT',                value: foundry.outputs.aoaiEndpoint }
  { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT',         value: foundry.outputs.gpt4oChatDeployment }
  { name: 'AZURE_SEARCH_ENDPOINT',                value: search.outputs.endpoint }
  { name: 'AZURE_SEARCH_INDEX_LOGS',              value: 'mta-logs' }
  { name: 'AZURE_SEARCH_INDEX_RUNBOOKS',          value: 'mta-runbooks' }
  { name: 'AZURE_COSMOS_ENDPOINT',                value: cosmos.outputs.endpoint }
  { name: 'AZURE_COSMOS_DATABASE',                value: 'mta' }
  { name: 'AZURE_COSMOS_CONTAINER_INCIDENTS',     value: 'incidents' }
  { name: 'AZURE_COSMOS_CONTAINER_CONVERSATIONS', value: 'conversations' }
]

// ── Container App: log-analyst ────────────────────────────────────────────────
// Internal (intra-env only), port 8001, CPU scale rule

@description('log-analyst Container App — internal ingress, CPU scale, azd service tag for azd discovery')
module logAnalystApp 'modules/containerApp.bicep' = {
  name: 'logAnalystApp'
  params: {
    name: 'log-analyst'
    location: location
    tags: union(tags, { 'azd-service-name': 'log-analyst' })
    containerAppsEnvironmentId: caEnv.outputs.id
    containerRegistryLoginServer: acr.outputs.loginServer
    image: placeholderImage
    targetPort: 8001
    external: false
    scaleRuleType: 'cpu'
    envVars: commonEnvVars
    secretEnvVars: aiConnStringEnvVar
    secrets: aiConnStringKvSecret
    userAssignedIdentityId: identity.outputs.id
  }
}

@description('service-advisor Container App — internal ingress, CPU scale, azd service tag for azd discovery')
module serviceAdvisorApp 'modules/containerApp.bicep' = {
  name: 'serviceAdvisorApp'
  params: {
    name: 'service-advisor'
    location: location
    tags: union(tags, { 'azd-service-name': 'service-advisor' })
    containerAppsEnvironmentId: caEnv.outputs.id
    containerRegistryLoginServer: acr.outputs.loginServer
    image: placeholderImage
    targetPort: 8002
    external: false
    scaleRuleType: 'cpu'
    envVars: commonEnvVars
    secretEnvVars: aiConnStringEnvVar
    secrets: aiConnStringKvSecret
    userAssignedIdentityId: identity.outputs.id
  }
}

// ── Container App: orchestrator ───────────────────────────────────────────────
// External ingress, port 8000, HTTP scale, transport=auto for WebSocket support.
// transport='auto' handles HTTP/1.1, HTTP/2, and WebSocket connections; there is
// no separate WebSocket flag in the 2024-03-01 ACA API.

@description('orchestrator Container App — external ingress with WebSocket (transport=auto), HTTP scale, azd service tag')
module orchestratorApp 'modules/containerApp.bicep' = {
  name: 'orchestratorApp'
  params: {
    name: 'orchestrator'
    location: location
    tags: union(tags, { 'azd-service-name': 'orchestrator' })
    containerAppsEnvironmentId: caEnv.outputs.id
    containerRegistryLoginServer: acr.outputs.loginServer
    image: placeholderImage
    targetPort: 8000
    external: true
    transport: 'auto'
    scaleRuleType: 'http'
    envVars: concat(commonEnvVars, [
      { name: 'LOG_ANALYST_URL',                   value: 'http://${logAnalystApp.outputs.fqdn}' }
      { name: 'SERVICE_ADVISOR_URL',               value: 'http://${serviceAdvisorApp.outputs.fqdn}' }
      { name: 'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT', value: foundry.outputs.projectEndpoint }
      { name: 'AZURE_AI_FOUNDRY_PROJECT_NAME',     value: foundry.outputs.projectName }
      { name: 'AZURE_OPENAI_REALTIME_DEPLOYMENT',  value: foundry.outputs.gpt4oRealtimeDeployment }
      { name: 'AZURE_SPEECH_ENDPOINT',             value: speech.outputs.endpoint }
      { name: 'AZURE_SPEECH_REGION',               value: speech.outputs.region }
      { name: 'VOICE_PROVIDER',                    value: 'foundry_realtime' }
    ])
    secretEnvVars: aiConnStringEnvVar
    secrets: aiConnStringKvSecret
    userAssignedIdentityId: identity.outputs.id
  }
}

// ── Container App: frontend ───────────────────────────────────────────────────
// External ingress, port 80, HTTP scale

@description('frontend Container App — external ingress, HTTP scale, azd service tag')
module frontendApp 'modules/containerApp.bicep' = {
  name: 'frontendApp'
  params: {
    name: 'frontend'
    location: location
    tags: union(tags, { 'azd-service-name': 'frontend' })
    containerAppsEnvironmentId: caEnv.outputs.id
    containerRegistryLoginServer: acr.outputs.loginServer
    image: placeholderImage
    targetPort: 80
    external: true
    scaleRuleType: 'http'
    envVars: [
      { name: 'AZURE_CLIENT_ID',  value: identity.outputs.clientId }
      { name: 'ORCHESTRATOR_URL', value: 'https://${orchestratorApp.outputs.fqdn}' }
    ]
    secretEnvVars: aiConnStringEnvVar
    secrets: aiConnStringKvSecret
    userAssignedIdentityId: identity.outputs.id
  }
}

// ── Role Assignments ──────────────────────────────────────────────────────────

@description('All Azure RBAC and Cosmos SQL role assignments for the UAMI and the deploying user')
module roleAssignments 'modules/roleAssignments.bicep' = {
  name: 'roleAssignments'
  params: {
    uamiPrincipalId: identity.outputs.principalId
    principalId: principalId
    acrName: acr.outputs.name
    keyVaultName: keyVault.outputs.name
    searchName: search.outputs.name
    cosmosAccountName: cosmos.outputs.name
    speechAccountName: speech.outputs.name
    appInsightsName: appInsights.outputs.name
    aoaiAccountName: foundry.outputs.aoaiAccountName
    foundryProjectName: foundry.outputs.projectName
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Outputs — consumed by azd as environment variables for the apps
// ─────────────────────────────────────────────────────────────────────────────

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = resourceGroup().name

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = acr.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = acr.outputs.name

output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = caEnv.outputs.id
output AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN string = caEnv.outputs.defaultDomain

output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name

output AZURE_USER_ASSIGNED_IDENTITY_ID string = identity.outputs.id
output AZURE_USER_ASSIGNED_IDENTITY_CLIENT_ID string = identity.outputs.clientId
output AZURE_USER_ASSIGNED_IDENTITY_PRINCIPAL_ID string = identity.outputs.principalId

output AZURE_AI_FOUNDRY_PROJECT_ENDPOINT string = foundry.outputs.projectEndpoint
output AZURE_AI_FOUNDRY_PROJECT_NAME string = foundry.outputs.projectName

output AZURE_OPENAI_ENDPOINT string = foundry.outputs.aoaiEndpoint
output AZURE_OPENAI_CHAT_DEPLOYMENT string = foundry.outputs.gpt4oChatDeployment
output AZURE_OPENAI_REALTIME_DEPLOYMENT string = foundry.outputs.gpt4oRealtimeDeployment

output AZURE_SEARCH_ENDPOINT string = search.outputs.endpoint
output AZURE_SEARCH_INDEX_LOGS string = 'mta-logs'
output AZURE_SEARCH_INDEX_RUNBOOKS string = 'mta-runbooks'

output AZURE_COSMOS_ENDPOINT string = cosmos.outputs.endpoint
output AZURE_COSMOS_DATABASE string = 'mta'
output AZURE_COSMOS_CONTAINER_INCIDENTS string = 'incidents'
output AZURE_COSMOS_CONTAINER_CONVERSATIONS string = 'conversations'

output AZURE_SPEECH_ENDPOINT string = speech.outputs.endpoint
output AZURE_SPEECH_REGION string = speech.outputs.region

output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString

output AZURE_POSTGRES_HOST string = postgres.outputs.host
output AZURE_POSTGRES_DB string = 'mta_legacy'

output LOG_ANALYST_URL string = 'http://${logAnalystApp.outputs.fqdn}'
output SERVICE_ADVISOR_URL string = 'http://${serviceAdvisorApp.outputs.fqdn}'
output ORCHESTRATOR_URL string = 'https://${orchestratorApp.outputs.fqdn}'
output FRONTEND_URL string = 'https://${frontendApp.outputs.fqdn}'

output VOICE_PROVIDER string = 'foundry_realtime'
