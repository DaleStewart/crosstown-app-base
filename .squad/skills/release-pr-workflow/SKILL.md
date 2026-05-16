# Skill: Release PR Workflow — Squad Branching & Commit Patterns

**Scope:** Operations & CI/CD — squad members preparing branches for PR + merge.  
**Lead:** Okoye  
**Status:** Extracted 2026-05-15 (spec-kit commit 7c063c5)

## Overview

Guidelines for structuring git branches, staging files, and committing work in the squad environment where multiple agents work in parallel and some files (decisions, inbox) have ownership lanes.

## Branch Naming Conventions

### Pattern: `squad/<scope-type>-<descriptor>-<version>`

**Issue-driven work:**
```
squad/42-realtime-model-swap    (issue #42, descriptive slug, no version)
```

**Tool/infrastructure work (not issue-scoped):**
```
squad/add-spec-kit-v0.8.10      (verb + tool name + tool version)
squad/update-bicep-linter-2.0   (tool upgrade)
```

**Why:** Tool/infra branches live longer and are version-tracked for repeatability. Issue branches are ephemeral and tie to a tracking number.

## Staging Best Practices

### ⚠️ Never use bulk adds
- ❌ `git add .`
- ❌ `git add -A`
- ❌ `git add <directory-glob>`

### ✅ Always stage explicitly
```powershell
# Enumerate all files by path
git add -- 'path/to/file1.md'
git add -- 'path/to/file2.json'
git add -- '.github/workflows/ci.yml'

# For directories: list first, then add each file
git glob **.py  # or `git status --short` to enumerate
git add -- 'module/file1.py'
git add -- 'module/file2.py'
```

**Why:** Squad members work in parallel with **separate ownership lanes** (e.g., Scribe owns `.squad/decisions/inbox/*`). Explicit staging prevents accidental inclusion of cross-agent changes.

## Commit Message Format

Use `git commit -F <tempfile>` on Windows (avoids quoting hell):

```powershell
$msg = @"
<Title line — 50 chars max>

<Body — motivation, scope, affected areas>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
"@
$tempFile = [System.IO.Path]::GetTempFileName()
$msg | Out-File -FilePath $tempFile -Encoding UTF8
git commit -F $tempFile
Remove-Item $tempFile -Force
```

**Include Co-authored-by trailer** for all squad commits (CI/CD requirement).

## Example: Multi-Directory Commit with Intentional Exclusions

**Scenario:** Bundling tool scaffolding + populated artifacts + cross-agent history, but **NOT** inbox files (Scribe's lane).

```powershell
# Stage deliverables (40 files across 4 dirs)
9..$..github/agents/speckit.*.agent.md
git add -- '.github/agents/speckit.analyze.agent.md'
# ... (9 files total)

git add -- '.github/prompts/speckit.analyze.prompt.md'
# ... (9 more)

git add -- '.specify/init-options.json'
# ... (17 .specify files)

git add -- '.squad/skills/spec-kit-authoring/SKILL.md'

# Stage history updates (3 files)
git add -- '.squad/agents/okoye/history.md'
git add -- '.squad/agents/stark/history.md'

# DO NOT stage inbox (intentional)
# git add -- '.squad/decisions/inbox/*'   ← Never

# Verify
git status --short   # Should show only intended files
git diff --cached --stat | tail -1  # Count files

# Commit
git commit -m "Add GitHub Spec Kit v0.8.10..."
```

**Result:** Clean separation of concerns. Scribe can later curate inbox files into decisions.md without rebase friction.

## Verification Checklist

After committing:

```powershell
# New commit exists
git log --oneline -1

# Correct file count
git diff --stat HEAD~1 | tail -1

# Status is clean (no uncommitted changes)
git status --short

# Intentional exclusions still present (untracked)
git status --short | Select-String "inbox"   # Should be empty
```

## When to Defer Push

Push is deferred when:
- Remote is unresolvable (`git remote -v` shows no valid origin).
- SSH key auth fails.
- Repo not yet provisioned on GitHub.
- Parallel branch uses same remote (both branches ready to push; blocked as a group).

**Action:** Document in decision inbox. Wait for T'Challa or infrastructure team to restore remote, then push all local branches together.

## Org Import Pattern: PAT + SSO + HTTPS Remote

**Scenario:** Release branches queued locally; remote origin cannot be reached due to auth/SSH issues.

**Pattern (verified 2026-05-15, D-012 resolved):**

1. **Authenticate with PAT** (in-memory, never to disk):
   ```powershell
   $env:GH_TOKEN = 'ghp_<token>'
   gh auth status               # Verify active account + token scopes
   ```

2. **Smoke test org reachability:**
   ```powershell
   gh api orgs/<ORG-NAME> --jq '.login'  # Must return org login, not 404
   ```
   If 404 appears: **Stop.** PAT lacks SSO authorization (user must click "Authorize" button in GitHub SSO prompt) OR account is not an org member.

3. **Flip remote to HTTPS:**
   ```powershell
   git remote set-url origin https://github.com/<ORG>/<REPO>.git
   gh auth setup-git           # Establish credential helper (no SSH key management)
   git remote -v              # Verify
   ```

4. **Verify repo exists and is accessible:**
   ```powershell
   gh repo view <ORG>/<REPO> --json name,visibility
   # If 404: repo not yet created. Use `gh repo create ...` before pushing.
   ```

5. **Push all branches and create PRs:**
   ```powershell
   git push -u origin <branch-1>
   git push -u origin <branch-2>
   gh pr create --title "..." --base main --head <branch-1> --body-file body.txt
   gh pr create --title "..." --base main --head <branch-2> --body-file body.txt
   ```

**Key insights:**
- **SSO authorization is separate from token scopes.** Even with correct scopes (`admin:org`, `repo`, `workflow`), org API calls return 404 until user clicks "Authorize."
- **HTTPS + credential helper** is more reliable than SSH key config in Windows CI/CD environments.
- **Dual-branch push + parallel PR creation** is supported; no merge dependency required.

**Confidence:** Medium — tested once at org scale (2026-05-15). Pattern should generalize to any org with SSO enabled.

## See Also

- `.squad/decisions/inbox/okoye-org-import-success.md` — Resolution summary for D-012.
- `.squad/team.md` — Squad routing and ownership lanes.
