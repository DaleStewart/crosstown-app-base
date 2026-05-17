# AAD wiring for the live SWA

The judging app is deployed at:

> **https://mango-hill-0ee13cb0f.7.azurestaticapps.net/**

The frontend trusts SWA's built-in AAD provider, which expects two app settings — `AAD_CLIENT_ID` and `AAD_CLIENT_SECRET` — pointing at an Entra app registration in the Microsoft tenant (`72f988bf-86f1-41af-91ab-2d7cd011db47`). Until those are set, sign-in won't work.

Do this in the **Azure portal**, signed in with your `@microsoft.com` account.

## A. Create an Entra app registration

1. Portal → **Microsoft Entra ID → App registrations → + New registration**
2. **Name:** `MTA Hackathon Judging`
3. **Supported account types:** *Accounts in this organizational directory only (Microsoft only — single tenant)*
4. **Redirect URI:** *Web* → `https://mango-hill-0ee13cb0f.7.azurestaticapps.net/.auth/login/aad/callback`
5. Click **Register**
6. Copy the **Application (client) ID** — you'll paste it into the SWA in step C.

## B. Create a client secret

1. Same app → **Certificates & secrets → + New client secret**
2. **Description:** `swa-aad`
3. **Expires:** 90 days (the hackathon is days away; this is plenty)
4. Click **Add**
5. **Copy the `Value` immediately** — Entra hides it on the next page load and won't show it again.

## C. Add the two settings to the SWA

1. Portal → Static Web App **`mtahack-swa-5vqz4ojvidqwi` → Configuration → Application settings**
2. **+ Add** → name `AAD_CLIENT_ID`, value = the Application (client) ID from step A
3. **+ Add** → name `AAD_CLIENT_SECRET`, value = the secret value from step B
4. **Save**

App-setting changes don't require a redeploy.

## D. Verify

1. Open a **private/incognito** window
2. Navigate to `https://mango-hill-0ee13cb0f.7.azurestaticapps.net/judge.html`
3. You should be redirected to the Microsoft sign-in page
4. Sign in with your `@microsoft.com` account
5. After sign-in, you should land back on `/judge.html` and see the team picker

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `AADSTS50011: The reply URL specified in the request does not match` | Redirect URI typo in step A.4 | Edit the app registration → Authentication → fix the URI |
| `AADSTS500011: The resource principal named ... was not found` | Single-tenant restriction blocking your account | Make sure you signed in with the `@microsoft.com` account (not a guest tenant) |
| Stays on the SWA without redirecting | App settings not saved | Re-check `AAD_CLIENT_ID` and `AAD_CLIENT_SECRET` on the SWA |
| Signed in but `/admin.html` shows 401 | `ADMIN_EMAILS` env var doesn't include your email | Portal → SWA → Configuration → confirm `ADMIN_EMAILS` contains your email (lowercase) |
| 500 from `/api/*` after sign-in | Cosmos connection string missing | Confirm `COSMOS_CONNECTION_STRING` is set on the SWA (azd should have done this) |
