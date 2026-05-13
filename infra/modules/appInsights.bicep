@description('Name of the Application Insights component')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Log Analytics workspace resource ID for workspace-based Application Insights')
param logAnalyticsWorkspaceId string

resource component 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspaceId
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

output id string = component.id
output name string = component.name
output connectionString string = component.properties.ConnectionString
output instrumentationKey string = component.properties.InstrumentationKey
