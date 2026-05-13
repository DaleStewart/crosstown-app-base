// Idle by design — Extension 09 wires this in.
// This module provisions the PostgreSQL Flexible Server skeleton but does not connect it
// to any application. Extension 09 adds the connection string, Entra role assignments,
// and the relevant env var injection into the orchestrator container app.

@description('Name of the PostgreSQL Flexible Server (3–63 chars)')
@minLength(3)
@maxLength(63)
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    // Burstable B1ms — smallest available tier, sufficient for hackathon skeleton
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    // Entra-only auth — no password stored or needed
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: subscription().tenantId
    }
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      // Public access enabled to allow Azure services (ACA) to connect;
      // firewall rule below restricts to Azure-internal IPs only
      publicNetworkAccess: 'Enabled'
    }
  }
}

// Allow Azure services to connect — uses the special 0.0.0.0 sentinel range
resource azureServicesFirewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: server
  name: 'AllowAllAzureServicesAndResourcesWithinAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: server
  name: 'mta_legacy'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

output id string = server.id
output name string = server.name
// fullyQualifiedDomainName is set by the service after provisioning
output host string = server.properties.fullyQualifiedDomainName
