@description('Name of the Key Vault (3–24 chars, alphanumeric + hyphens)')
@minLength(3)
@maxLength(24)
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Application Insights connection string to store as a KV secret (referenced by container apps via secretRef)')
@secure()
param appInsightsConnectionString string

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    // RBAC mode — access controlled by Azure role assignments, not access policies
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    // purgeProtection: omitted to honor tenant Azure Policy (some tenants enforce purgeProtection=true; Azure defaults are safe).
    publicNetworkAccess: 'Enabled'
  }
}

// Store the App Insights connection string so container apps can reference it via secretRef
// without embedding the value in plain environment variables
resource appInsightsSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: vault
  name: 'appinsights-connection-string'
  properties: {
    value: appInsightsConnectionString
  }
}

output id string = vault.id
output name string = vault.name
output endpoint string = vault.properties.vaultUri
// URI without version — ACA always resolves the latest revision
output appInsightsSecretUri string = '${vault.properties.vaultUri}secrets/appinsights-connection-string'
