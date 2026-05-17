# GitHub OAuth Setup for the Judging SWA

GitHub OAuth is built into Azure Static Web Apps — no app registration or tenant configuration required. Microsoft employees already have GitHub accounts.

## Setup (post-provision)

1. **Azure Portal** → Static Web App (`mtahack-swa-5vqz4ojvidqwi`)
2. **Configuration** → **Application settings**
3. **+ Add** → name `ADMIN_USERS`, value = comma-separated GitHub usernames (lowercase, e.g., `segayle,alice,bob`)
4. **Save**

That's it. GitHub OAuth is automatically enabled in `staticwebapp.config.json`.

## Testing

1. Open https://mango-hill-0ee13cb0f.7.azurestaticapps.net/judge.html in an **incognito window**.
2. You should be redirected to GitHub login.
3. Sign in with your GitHub account.
4. You'll be redirected back to `/judge.html`.
5. If your GitHub username is in `ADMIN_USERS`, you can also access `/admin.html`.

## Admin allowlist

Edit `ADMIN_USERS` (not `ADMIN_EMAILS`) on the SWA → **Application settings**:
- **Format:** Comma-separated GitHub usernames, lowercase: `segayle,otheradmin,alice`
- **Example:** For user `https://github.com/segayle`, add `segayle` to the list
- Admin users can access `/admin.html` and all admin API routes (`/api/lock`, `/api/export`, etc.)

## Cleanup

If you previously had `AAD_CLIENT_ID`, `AAD_CLIENT_SECRET`, and `AAD_TENANT_ID` app settings, you can safely delete them — they are no longer referenced.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Redirect loop or "Page not found" after login | GitHub identity not syncing to SWA | Wait 10–20s, try incognito again, or clear cookies |
| Admin role not granted | GitHub username not in `ADMIN_USERS` | Check the exact username (lowercase) in GitHub profile → add to `ADMIN_USERS` |
| Still seeing old AAD login prompt | Browser cache | Clear cookies and cache, or use incognito |
