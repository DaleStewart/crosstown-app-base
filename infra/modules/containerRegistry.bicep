@description('Name of the Container Registry (5–50 alphanumeric chars, no hyphens)')
@minLength(5)
@maxLength(50)
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    // Admin user disabled — UAMI uses AcrPull role for image pull
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

output id string = registry.id
output name string = registry.name
output loginServer string = registry.properties.loginServer
