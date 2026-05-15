# Skill: Spec Kit Authoring (MTA AI Hackathon)

## What this skill does

Authors Spec Kit v0.8.10 artifacts (constitution, spec, plan, tasks) for the MTA AI Hackathon accelerator repo. Translates existing repo contracts into the `.specify/` + `specs/` layout.

## When to use

- Ratifying or amending the project constitution
- Writing a new feature spec + plan + tasks for a change to the accelerator
- Reviewing whether a proposed change violates constitution principles

## Key patterns

### Constitution authoring
1. Read `README.md`, `docs/architecture.md`, `docs/voice.md`, `docs/evals.md`, `.github/copilot-instructions.md`, and `.squad/decisions.md` to extract principles.
2. Each principle needs: Roman numeral name, one-line ethos, rationale paragraph, enforcing file list.
3. Mark genuinely non-negotiable principles — at minimum, the citation contract and mock-data rule.
4. Quality Gates section maps to the four CI gates with thresholds from `docs/architecture.md`.
5. Development Workflow section mirrors `.github/copilot-instructions.md` build/test/lint commands.
6. Template: `.specify/templates/constitution-template.md`. Output: `.specify/memory/constitution.md`.

### Spec authoring
1. `create-new-feature.ps1 -DryRun -ShortName <slug> -Number <N> "<description>"` to preview naming. **Do not run without `-DryRun` if you don't want a new git branch** — the script creates a branch by default.
2. Create `specs/NNN-slug/` by hand if branch creation is unwanted.
3. Template: `.specify/templates/spec-template.md`. Write WHAT changed and WHY, not HOW.
4. User stories should be independently testable. Non-goals are as important as goals.

### Plan authoring
1. Template: `.specify/templates/plan-template.md`.
2. Include: files changed, files NOT changed (and why), naming decisions, verification gates, rollback.
3. Constitution Check table: verify each principle is unviolated.

### Tasks authoring
1. Template: `.specify/templates/tasks-template.md`.
2. Tasks grouped by phase (infra → app → docs → verification).
3. Each task: ID, slug, file(s) touched, dependencies, status.
4. Mid-flight discoveries (scope additions) should be noted inline.

## Pitfalls discovered

- `create-new-feature.ps1` creates a git branch unless `-DryRun` is passed. If you need to stay on `main`, create the `specs/NNN-slug/` folder by hand.
- The `.github/prompts/speckit.*.prompt.md` files are minimal agent frontmatter stubs — the real workflow logic is in the templates under `.specify/templates/`.
- The constitution template uses `<!-- Example: ... -->` HTML comments for guidance — strip them all in the final output.
- Keep principles to 5–7 max. The template implies five but allows more. Prioritize defensibility over coverage.
