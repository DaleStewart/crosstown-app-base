// Azure AI Foundry Hub + Project + Azure OpenAI
//
// Architecture:
//   Hub     — the organisational container; hosts shared infrastructure (storage, KV,
//             App Insights) and Azure service connections.  One hub per environment.
//   Project — the workload-scoped workspace; developers target its inference endpoint.
//             Apps call the Azure OpenAI resource directly; the Foundry project endpoint
//             is used for SDK-based orchestration (azure-ai-projects SDK).
//
// Model deployments live on the Azure OpenAI account (Microsoft.CognitiveServices/accounts
// kind=OpenAI).  The hub exposes them to the project via an implicit connection that azd
// wires through the AZURE_OPENAI_ENDPOINT output.

@description('Name of the AI Foundry hub workspace')
param hubName string

@description('Name of the AI Foundry project workspace')
param projectName string

@description('Name of the Azure OpenAI Cognitive Services account')
param aoaiAccountName string

@description('Name of the dedicated storage account required by the hub (3–24 alphanumeric)')
@minLength(3)
@maxLength(24)
param storageAccountName string

@description('Resource ID of the shared Key Vault (required by the hub workspace)')
param keyVaultId string

@description('Resource ID of the Application Insights component (wired into the hub for experiment tracking)')
param appInsightsId string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

// Storage account required by every ML/Foundry hub workspace
resource hubStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// Azure OpenAI resource — model deployments live here; the hub connects to it
resource aoaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aoaiAccountName
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: aoaiAccountName
    publicNetworkAccess: 'Enabled'
  }
}

// gpt-4o — Standard deployment, 10 K TPM (hackathon scale)
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: aoaiAccount
  name: 'gpt-4o'
  sku: { name: 'Standard', capacity: 10 }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
  }
}

// gpt-4o-realtime-preview — GlobalStandard, 10 K TPM; supports audio + WebSocket streaming
// dependsOn serialises deployments to avoid concurrent-update throttle on the same account
resource gpt4oRealtimeDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: aoaiAccount
  name: 'gpt-4o-realtime-preview'
  dependsOn: [gpt4oDeployment]
  sku: { name: 'GlobalStandard', capacity: 10 }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-realtime-preview'
      version: '2024-10-01'
    }
  }
}

// AI Foundry Hub (Microsoft.MachineLearningServices/workspaces kind=Hub)
// API 2024-04-01 — first GA release with kind=Hub / kind=Project support
resource hub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: hubName
  location: location
  tags: tags
  kind: 'Hub'
  identity: { type: 'SystemAssigned' }
  sku: { name: 'Basic', tier: 'Basic' }
  properties: {
    description: 'MTA AI Hackathon — Foundry hub'
    storageAccount: hubStorage.id
    keyVault: keyVaultId
    applicationInsights: appInsightsId
    publicNetworkAccess: 'Enabled'
  }
}

// AI Foundry Project — inherits hub connections including the AOAI account
resource project 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: projectName
  location: location
  tags: tags
  kind: 'Project'
  identity: { type: 'SystemAssigned' }
  sku: { name: 'Basic', tier: 'Basic' }
  properties: {
    description: 'MTA AI Hackathon — Foundry project'
    hubResourceId: hub.id
    publicNetworkAccess: 'Enabled'
  }
}

output hubId string = hub.id
output hubName string = hub.name
output projectId string = project.id
output projectName string = project.name
// AI Foundry project endpoint format: https://<location>.api.azureml.ms
// Apps use the azure-ai-projects SDK with this base URL + project name
output projectEndpoint string = 'https://${location}.api.azureml.ms'
output aoaiAccountId string = aoaiAccount.id
output aoaiAccountName string = aoaiAccount.name
output aoaiEndpoint string = aoaiAccount.properties.endpoint
output gpt4oChatDeployment string = gpt4oDeployment.name
output gpt4oRealtimeDeployment string = gpt4oRealtimeDeployment.name
