@description('Name of the Azure AI Search service (2–60 chars)')
@minLength(2)
@maxLength(60)
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

// API 2023-11-01 — first stable release that exposes the semanticSearch property
resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    // 'free' tier semantic search is supported on Basic SKU at no extra charge
    semanticSearch: 'free'
    // Keyless auth — RBAC only. Bearer tokens via DefaultAzureCredential.
    // Setting disableLocalAuth=true forces Azure to flip authOptions away
    // from the default 'apiKeyOnly' mode (which rejects AAD tokens entirely).
    // Honors architecture mandate: "Auth is keyless ... Never add API-key auth".
    disableLocalAuth: true
  }
}

output id string = search.id
output name string = search.name
// Construct endpoint — the property is not exposed directly by the ARM resource
output endpoint string = 'https://${search.name}.search.windows.net'
