@description('Name of the Cosmos DB account (3–44 chars, lowercase alphanumeric + hyphens)')
@minLength(3)
@maxLength(44)
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
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
    databaseAccountOfferType: 'Standard'
    // EnableServerless: pay-per-request — ideal for hackathon bursty workloads
    capabilities: [
      { name: 'EnableServerless' }
    ]
    enableAutomaticFailover: false
    disableKeyBasedMetadataWriteAccess: false
    publicNetworkAccess: 'Enabled'
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: account
  name: 'mta'
  properties: {
    resource: {
      id: 'mta'
    }
  }
}

resource incidentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'incidents'
  properties: {
    resource: {
      id: 'incidents'
      partitionKey: {
        paths: ['/incidentId']
        kind: 'Hash'
      }
    }
  }
}

resource conversationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'conversations'
  properties: {
    resource: {
      id: 'conversations'
      partitionKey: {
        paths: ['/conversationId']
        kind: 'Hash'
      }
    }
  }
}

output id string = account.id
output name string = account.name
output endpoint string = account.properties.documentEndpoint
