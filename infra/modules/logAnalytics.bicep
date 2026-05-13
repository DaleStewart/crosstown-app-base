@description('Name of the Log Analytics workspace')
param name string

@description('Azure region for the workspace')
param location string

@description('Resource tags')
param tags object = {}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

output id string = workspace.id
output name string = workspace.name
output customerId string = workspace.properties.customerId

@description('Primary shared key — consumed only by containerAppsEnv for log shipping; not surfaced to app outputs')
@secure()
output primarySharedKey string = workspace.listKeys().primarySharedKey
