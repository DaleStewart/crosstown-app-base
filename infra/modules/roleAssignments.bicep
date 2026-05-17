// All RBAC role assignments are collected here for auditability.
// Two types:
//   1. Azure RBAC (Microsoft.Authorization/roleAssignments) — most resources
//   2. Cosmos DB data-plane SQL role (Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments)
//
// Assignments are created for:
//   • uamiPrincipalId — the shared user-assigned managed identity (runtime access)
//   • principalId     — the deploying user (local dev / azd up access)

@description('Principal ID of the user-assigned managed identity')
param uamiPrincipalId string

@description('Principal ID of the deploying user (for local-dev role assignments)')
param principalId string

@description('Principal type of the deploying identity ("User" for local azd up; "ServicePrincipal" for CI). Defaults to "User" for backwards compatibility.')
@allowed([
  'User'
  'ServicePrincipal'
])
param principalType string = 'User'

@description('Name of the Container Registry')
param acrName string

@description('Name of the Key Vault')
param keyVaultName string

@description('Name of the AI Search service')
param searchName string

@description('Name of the Cosmos DB account')
param cosmosAccountName string

@description('Name of the Speech Services account')
param speechAccountName string

@description('Name of the Application Insights component')
param appInsightsName string

@description('Name of the Azure OpenAI Cognitive Services account')
param aoaiAccountName string

@description('Name of the AI Foundry project workspace')
param foundryProjectName string

// ── Built-in role definition IDs (subscription-scoped resource IDs) ──────────
var roles = {
  acrPull:                     subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  acrPush:                     subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8311e382-0749-4cb8-b61a-304f252e45ec')
  cognitiveServicesUser:       subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
  cognitiveServicesSpeechUser: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'f2dc8367-1007-4938-bd23-fe263f013447')
  searchIndexDataContributor:  subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
  searchServiceContributor:    subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
  keyVaultSecretsUser:         subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
  keyVaultSecretsOfficer:      subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  monitoringMetricsPublisher:  subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '3913510d-42f4-4e42-8a64-420c390055eb')
  azureAIDeveloper:            subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '64702f94-c441-49e6-a78b-ef80e0188fee')
}

// ── Existing resource references ─────────────────────────────────────────────

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource searchService 'Microsoft.Search/searchServices@2023-11-01' existing = {
  name: searchName
}

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' existing = {
  name: cosmosAccountName
}

resource speechAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: speechAccountName
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource aoaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: aoaiAccountName
}

// API 2024-04-01 — AI Foundry hub/project workspace
resource foundryProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' existing = {
  name: foundryProjectName
}

// ── UAMI role assignments ─────────────────────────────────────────────────────

resource uamiAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, uamiPrincipalId, roles.acrPull)
  scope: acr
  properties: {
    roleDefinitionId: roles.acrPull
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiCognitiveServicesUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aoaiAccount.id, uamiPrincipalId, roles.cognitiveServicesUser)
  scope: aoaiAccount
  properties: {
    roleDefinitionId: roles.cognitiveServicesUser
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiSpeechUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(speechAccount.id, uamiPrincipalId, roles.cognitiveServicesSpeechUser)
  scope: speechAccount
  properties: {
    roleDefinitionId: roles.cognitiveServicesSpeechUser
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiSearchIndexDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, uamiPrincipalId, roles.searchIndexDataContributor)
  scope: searchService
  properties: {
    roleDefinitionId: roles.searchIndexDataContributor
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiSearchServiceContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, uamiPrincipalId, roles.searchServiceContributor)
  scope: searchService
  properties: {
    roleDefinitionId: roles.searchServiceContributor
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiKeyVaultSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, uamiPrincipalId, roles.keyVaultSecretsUser)
  scope: keyVault
  properties: {
    roleDefinitionId: roles.keyVaultSecretsUser
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiMonitoringMetricsPublisher 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appInsights.id, uamiPrincipalId, roles.monitoringMetricsPublisher)
  scope: appInsights
  properties: {
    roleDefinitionId: roles.monitoringMetricsPublisher
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource uamiAzureAIDeveloper 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundryProject.id, uamiPrincipalId, roles.azureAIDeveloper)
  scope: foundryProject
  properties: {
    roleDefinitionId: roles.azureAIDeveloper
    principalId: uamiPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Cosmos DB data-plane SQL role — not an Azure RBAC role; uses Cosmos-specific assignment
// Built-in Data Contributor role definition ID: 00000000-0000-0000-0000-000000000002
resource uamiCosmosSqlRole 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-05-15' = {
  name: guid(cosmosAccount.id, uamiPrincipalId, '00000000-0000-0000-0000-000000000002')
  parent: cosmosAccount
  properties: {
    roleDefinitionId: '${cosmosAccount.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
    principalId: uamiPrincipalId
    scope: cosmosAccount.id
  }
}

// ── Deploying-user role assignments (local dev / azd up) ─────────────────────

resource userAcrPush 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, principalId, roles.acrPush)
  scope: acr
  properties: {
    roleDefinitionId: roles.acrPush
    principalId: principalId
    principalType: principalType
  }
}

resource userCognitiveServicesUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aoaiAccount.id, principalId, roles.cognitiveServicesUser)
  scope: aoaiAccount
  properties: {
    roleDefinitionId: roles.cognitiveServicesUser
    principalId: principalId
    principalType: principalType
  }
}

resource userSearchIndexDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, principalId, roles.searchIndexDataContributor)
  scope: searchService
  properties: {
    roleDefinitionId: roles.searchIndexDataContributor
    principalId: principalId
    principalType: principalType
  }
}

resource userKeyVaultSecretsOfficer 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, principalId, roles.keyVaultSecretsOfficer)
  scope: keyVault
  properties: {
    roleDefinitionId: roles.keyVaultSecretsOfficer
    principalId: principalId
    principalType: principalType
  }
}

// Cosmos DB data-plane SQL role for deploying user
resource userCosmosSqlRole 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-05-15' = {
  name: guid(cosmosAccount.id, principalId, '00000000-0000-0000-0000-000000000002')
  parent: cosmosAccount
  properties: {
    roleDefinitionId: '${cosmosAccount.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
    principalId: principalId
    scope: cosmosAccount.id
  }
}
