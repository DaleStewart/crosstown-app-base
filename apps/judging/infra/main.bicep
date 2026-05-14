targetScope = 'resourceGroup'

@minLength(3)
@maxLength(20)
param name string = 'mtahack'

param location string = 'eastus2'

@description('azd environment name; injected automatically by azd.')
param environmentName string

@description('Entra tenant GUID used for SWA AAD identity provider.')
param tenantId string = subscription().tenantId

@description('Comma-separated list of admin emails (lowercased server-side).')
param adminEmails string = ''

var tags = {
  'azd-env-name': environmentName
  workload: 'mta-judging'
}

var resourceToken = uniqueString(subscription().id, resourceGroup().id, environmentName)
var cosmosAccountName = toLower('${name}-cosmos-${resourceToken}')
var swaName = toLower('${name}-swa-${resourceToken}')
var databaseName = 'mtahack'

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosAccountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    disableLocalAuth: false
    // SECURITY (H2): Cosmos firewall left Enabled because SWA managed Functions
    // use dynamic outbound IPs that aren't expressible as a fixed allowlist, and
    // Cosmos doesn't accept the AzureCloud service tag in ipRules. networkAclBypass
    // permits trusted Azure services (e.g. portal / deploymentScripts) while the
    // empty ipRules array forces explicit firewall posture instead of an open net.
    // TODO: tighten with SWA outbound IPs at deploy time (or move to VNet + PE).
    publicNetworkAccess: 'Enabled'
    networkAclBypass: 'AzureServices'
    networkAclBypassResourceIds: []
    ipRules: []
  }
}

resource sqlDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmos
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

var containerNames = [
  'teams'
  'scores'
  'events'
]

resource sqlContainers 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = [for c in containerNames: {
  parent: sqlDb
  name: c
  properties: {
    resource: {
      id: c
      partitionKey: {
        paths: [ '/track' ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [ { path: '/*' } ]
        excludedPaths: [ { path: '/"_etag"/?' } ]
      }
    }
  }
}]

resource swa 'Microsoft.Web/staticSites@2023-12-01' = {
  name: swaName
  location: location
  tags: union(tags, {
    'azd-service-name': 'web'
  })
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    // SECURITY (H3): config managed via Bicep only
    allowConfigFileUpdates: false
    stagingEnvironmentPolicy: 'Enabled'
    provider: 'Custom'
  }
}

// SECURITY (M4): connection string fetched server-side inside the staticSites/config
// resource and never surfaced via module outputs or top-level deployment outputs, so
// it is not rendered into the deployment template / ARM deployment history. The
// listConnectionStrings() call resolves at deploy time against the Cosmos account's
// data-plane keys and is written directly to the SWA app settings store.
// Future hardening: replace with a Key Vault secret + @Microsoft.KeyVault(...)
// reference, or switch Cosmos to disableLocalAuth=true with AAD RBAC.
resource swaSettings 'Microsoft.Web/staticSites/config@2023-12-01' = {
  parent: swa
  name: 'appsettings'
  properties: {
    COSMOS_CONNECTION_STRING: cosmos.listConnectionStrings().connectionStrings[0].connectionString
    ADMIN_EMAILS: adminEmails
    AAD_TENANT_ID: tenantId
  }
}

output STATIC_WEB_APP_NAME string = swa.name
output STATIC_WEB_APP_DEFAULT_HOSTNAME string = swa.properties.defaultHostname
output COSMOS_ACCOUNT_NAME string = cosmos.name
