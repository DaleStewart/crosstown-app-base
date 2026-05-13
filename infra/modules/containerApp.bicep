// Generic, parameterised Container App — called once per service from main.bicep.
// Adding a new specialist service later requires one additional module call with the
// appropriate targetPort, external, envVars, and scaleRuleType.
//
// WebSocket note: transport='auto' enables HTTP/1.1, HTTP/2, and WebSocket connections
// transparently.  The 2024-03-01 ACA API has no explicit WebSocket toggle — 'auto'
// is the recommended setting for any app that uses WS (e.g., the orchestrator).

@description('Name of the Container App (must match the azd-service-name tag value)')
param name string

@description('Azure region')
param location string

@description('Resource tags — must include azd-service-name for azd service discovery')
param tags object = {}

@description('Resource ID of the Container Apps Managed Environment')
param containerAppsEnvironmentId string

@description('Login server of the Container Registry (used in the registries pull config)')
param containerRegistryLoginServer string

@description('Full image reference including registry host and tag')
param image string

@description('Port the container process listens on')
param targetPort int

@description('Expose ingress externally (internet-facing). Set false for internal-only services.')
param external bool = false

@description('Ingress transport mode. auto supports HTTP/1.1, HTTP/2, and WebSockets.')
@allowed(['auto', 'http', 'http2'])
param transport string = 'auto'

@description('Plain environment variables [{name: string, value: string}]')
param envVars array = []

@description('Secret-backed environment variables [{name: string, secretRef: string}]')
param secretEnvVars array = []

@description('App secrets as Key Vault references [{name: string, keyVaultUrl: string, identity: string}]')
param secrets array = []

@description('Resource ID of the user-assigned managed identity (ACR pull + data-plane access)')
param userAssignedIdentityId string

@description('CPU allocation as a decimal string (e.g. "0.5")')
param cpu string = '0.5'

@description('Memory allocation')
param memory string = '1Gi'

@description('Minimum number of replicas')
param minReplicas int = 1

@description('Maximum number of replicas')
param maxReplicas int = 3

@description('Scale rule type: http (orchestrator/frontend) or cpu (log-analyst)')
@allowed(['http', 'cpu'])
param scaleRuleType string = 'http'

var httpScaleRule = {
  name: 'http-scale-rule'
  http: {
    metadata: {
      concurrentRequests: '10'
    }
  }
}

var cpuScaleRule = {
  name: 'cpu-scale-rule'
  custom: {
    type: 'cpu'
    metadata: {
      type: 'Utilization'
      value: '70'
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: external
        targetPort: targetPort
        transport: transport
        // Allow HTTP for internal services (intra-env traffic); external apps enforce HTTPS
        allowInsecure: !external
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: userAssignedIdentityId
        }
      ]
      secrets: secrets
    }
    template: {
      containers: [
        {
          name: 'main'
          image: image
          resources: {
            // json() converts the string param to the decimal the ARM API expects
            cpu: json(cpu)
            memory: memory
          }
          env: concat(envVars, secretEnvVars)
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: scaleRuleType == 'http' ? [httpScaleRule] : [cpuScaleRule]
      }
    }
  }
}

output id string = app.id
output name string = app.name
output fqdn string = app.properties.configuration.ingress.fqdn
output uri string = '${external ? 'https' : 'http'}://${app.properties.configuration.ingress.fqdn}'
