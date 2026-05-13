@description('Name of the Speech Services Cognitive Services account')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

resource speech 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'SpeechServices'
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
    // Access controlled via RBAC (Cognitive Services Speech User role on UAMI)
    // Keys are not used; disableLocalAuth can be enabled post-hackathon
  }
}

output id string = speech.id
output name string = speech.name
output endpoint string = speech.properties.endpoint
// Region is the same as the deployment location; explicit output for app config
output region string = location
