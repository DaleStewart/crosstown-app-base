# azd Output Env Vars — `crosstown-dryrun-may15` — 2026-05-15 (sanitized)

Source: `azd env get-values` against env `crosstown-dryrun-may15` after `azd up` (provision + deploy) succeeded in swedencentral.

**Sanitization rule:** App Insights instrumentation key, ingestion endpoints, and any token/secret-bearing strings are redacted. Public ARM resource names, endpoint URLs, identity object ids, and resource group names are preserved (these are not secrets — they're addressable infra references).

---

## Identity

```
AZURE_ENV_NAME             = crosstown-dryrun-may15
AZURE_LOCATION             = swedencentral
AZURE_SUBSCRIPTION_ID      = 47156f11-2e05-4362-ac86-090b4b081b27
AZURE_TENANT_ID            = 9b7cbd77-6d6b-4879-8aba-63d7dfb18472
AZURE_PRINCIPAL_ID         = 0d7350a3-ff19-4108-b4de-27968717a7e0   # signed-in student user
AZURE_RESOURCE_GROUP       = rg-crosstown-dryrun-may15

AZURE_USER_ASSIGNED_IDENTITY_ID            = /subscriptions/47156f11-…/resourceGroups/rg-crosstown-dryrun-may15/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-mta-crosstown-dryrun-may15-yycemmso7sk7q
AZURE_USER_ASSIGNED_IDENTITY_CLIENT_ID     = cce9346a-6cd9-4b4f-a9f0-13630e23e34d
AZURE_USER_ASSIGNED_IDENTITY_PRINCIPAL_ID  = 74570ee2-4553-4c93-8bf3-75adbd7ae7c8
```

## Container Apps endpoints

```
FRONTEND_URL          = https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io
ORCHESTRATOR_URL      = https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io
LOG_ANALYST_URL       = http://log-analyst.internal.blackriver-0ab9be19.swedencentral.azurecontainerapps.io   # internal ingress only

AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN = blackriver-0ab9be19.swedencentral.azurecontainerapps.io
AZURE_CONTAINER_APPS_ENVIRONMENT_ID             = /subscriptions/47156f11-…/resourceGroups/rg-crosstown-dryrun-may15/providers/Microsoft.App/managedEnvironments/cae-crosstown-dryrun-may15-yycemmso7sk7q

AZURE_CONTAINER_REGISTRY_ENDPOINT = crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io
AZURE_CONTAINER_REGISTRY_NAME     = crcrosstowndryrunmay15yycemmso7sk7q
```

## Azure OpenAI / Foundry / Speech

```
AZURE_OPENAI_ENDPOINT             = https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT      = gpt-4.1
AZURE_OPENAI_REALTIME_DEPLOYMENT  = gpt-realtime-1.5

AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = https://swedencentral.api.azureml.ms
AZURE_AI_FOUNDRY_PROJECT_NAME     = mlw-proj-crosstown-dryrun-may15-

AZURE_SPEECH_ENDPOINT             = https://cog-spch-crosstown-dryrun-may15-yycemmso7sk7q.cognitiveservices.azure.com/
AZURE_SPEECH_REGION               = swedencentral

VOICE_PROVIDER                    = foundry_realtime
```

## AI Search

```
AZURE_SEARCH_ENDPOINT       = https://srch-crosstown-dryrun-may15-yycemmso7sk7q.search.windows.net
AZURE_SEARCH_INDEX_LOGS     = mta-logs        # currently empty — see Caveat #2 in azd-up-result-2026-05-15.md
AZURE_SEARCH_INDEX_RUNBOOKS = mta-runbooks    # currently empty
```

## Cosmos / Postgres / Key Vault

```
AZURE_COSMOS_ENDPOINT                = https://cosmos-crosstown-dryrun-may15-yycemmso7sk7q.documents.azure.com:443/
AZURE_COSMOS_DATABASE                = mta
AZURE_COSMOS_CONTAINER_INCIDENTS     = incidents
AZURE_COSMOS_CONTAINER_CONVERSATIONS = conversations

AZURE_POSTGRES_HOST = psql-crosstown-dryrun-may15-yycemmso7sk7q.postgres.database.azure.com
AZURE_POSTGRES_DB   = mta_legacy

AZURE_KEY_VAULT_NAME     = kv-crosstown-dryrun-may1
AZURE_KEY_VAULT_ENDPOINT = https://kv-crosstown-dryrun-may1.vault.azure.net/
```

## App Insights (sanitized)

```
APPLICATIONINSIGHTS_CONNECTION_STRING = InstrumentationKey=<REDACTED>;IngestionEndpoint=https://swedencentral-0.in.applicationinsights.azure.com/;LiveEndpoint=https://swedencentral.livediagnostics.monitor.azure.com/;ApplicationId=<REDACTED>
```

(Full connection string is in `azd env get-values` locally; redacted here because it contains the instrumentation GUID which is treated as a write key.)

## Container image refs (current revision)

```
SERVICE_FRONTEND_IMAGE_NAME      = crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/frontend-crosstown-dryrun-may15:azd-deploy-1778877487
SERVICE_LOG_ANALYST_IMAGE_NAME   = crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/log-analyst-crosstown-dryrun-may15:azd-deploy-1778877487
SERVICE_ORCHESTRATOR_IMAGE_NAME  = crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/orchestrator-crosstown-dryrun-may15:azd-deploy-1778877486
```

---

To regenerate on any machine:
```powershell
azd env select crosstown-dryrun-may15
azd env get-values
```
