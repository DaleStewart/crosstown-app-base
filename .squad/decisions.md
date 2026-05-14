# Squad Decisions

## Active Decisions

### D-001 · Cast the Avengers · Lead: T'Challa
**Date:** 2026-05-12
**Author:** Squad (operator request)
**Status:** Adopted

The squad is cast from the **Marvel Cinematic Universe** as the **Avengers**, with **T'Challa (Black Panther)** as the Lead. T'Challa's role aligns with the `ralph` slot's persistent-memory mandate: institutional recall + tie-breaking authority.

**Hires today:**
- `ralph` → **T'Challa** (Lead, Black Panther)
- `scribe` → **Shuri** (Knowledge archivist + R&D)

**Bench (hire as needed):** Tony Stark, Natasha Romanoff, Bruce Banner, Sam Wilson, Peter Parker, Okoye, Wanda Maximoff, Stephen Strange. See `.squad/casting/registry.json` for intended roles.

**Rationale:** T'Challa-as-Lead gives us a calm, strategy-first persona that complements the hackathon's "opt-in scaffolding" framing. The MCU was already on the allowlist (capacity 25) and pairs naturally with the team's existing two-slot baseline.

**Reversal procedure:** Re-cast by overwriting `.squad/casting/registry.json` and appending a new entry to `.squad/casting/history.json`. Update `.squad/team.md` and the affected `agents/*/charter.md`.

### D-002 · Judging app layout — `apps/judging/` as a sibling workload
**Date:** 2026-05-13
**Author:** Stark (Architect)
**Status:** Adopted

Everything for the judging app lives under **`apps/judging/`** as a self-contained workload:
- `apps/judging/shared/criteria.js` (dual-export: CJS + window global)
- `apps/judging/staticwebapp.config.json` (SWA AAD + route rules)
- `apps/judging/api/` (SWA managed Functions: teams-list, teams-create, myscores, score-submit, leaderboard, lock, export)
- `apps/judging/infra/main.bicep` (Cosmos serverless + SWA Standard)

Root `azure.yaml`, root `infra/`, and sibling `apps/*` remain untouched.

**Rationale:** Isolation of deploy lifecycle, single source of truth for criteria, SWA managed Functions reduces infra surface, partition key `/track` on Cosmos ensures predictable RU.

**Follow-ups (Okoye):** Decide azd integration vs. standalone GH Actions workflow. Replace `{{TODO_TENANT_GUID}}`. Document admin-role grant path.

### D-003 · Frontend design tokens for the judging app (v3 — MTA brand)
**Date:** 2026-05-13
**Author:** Parker (Frontend)
**Status:** Adopted

Reference scorecards used Barlow as a stand-in. Sean confirmed the real MTA brand is **Helvetica** + the **NYCT route palette**. All tokens repointed to MTA specs at `apps/judging/src/styles.css`:
- Color: MTA Blue `#0039A6`, MTA Red `#EE352E`, MTA Green `#00933C`, MTA Orange `#FF6319`, MTA Yellow `#FCCC0A`
- Typography: Helvetica Neue (no web fonts), 400 body / 500 labels / 700 display, uppercase tracking `-0.02em` to `-0.04em`
- Shape: `--radius: 2px` (buttons), `--radius-lg: 0` (cards), circular bullets/pills
- Tier ladder: Exceptional (green, ≥90), Strong (navy, ≥70), Developing (orange, ≥50), Needs work (red, <50)
- Components: `.bullet` (route-bullet primitive), `.hack-roundel`, `.signage`, `.tier-block`, `.tier-cell`, etc.
- Iconography: Tabler icons (mono), used sparingly; numbered bullets replace criterion icons
- Dark mode: bg `#0A0A0A`, surface `#181818`, navy `#4D7EE8`

**Rationale:** Maintains MTA visual identity, sharp-cornered panels, brand-layer compliance. Trademark: hackathon `AI` route bullet (not MTA "M" logo).

### D-004 · Separate `azure.yaml` inside `apps/judging/` (do not modify root)
**Date:** 2026-05-13
**Author:** Okoye (Operations)
**Status:** Adopted

Ship a **self-contained `azd` project at `apps/judging/azure.yaml`** with its own `infra/` folder. Users run `cd apps/judging && azd up` to deploy. Root `azure.yaml` is untouched.

**Rationale:** Isolation of blast radius, different lifecycles (event-scoped vs. long-running platform), different service topology (single staticwebapp vs. multi-containerapp), team parallelism, azd nesting is native.

**Trade-offs:** Users must `cd apps/judging` before azd commands (documented). SWA Functions auto-discovery documented as fallback using `swa deploy --api-location ./api`.

## Governance

- All meaningful changes require team consensus.
- Document architectural decisions here.
- Keep history focused on work, decisions focused on direction.
- Casting changes require a T'Challa sign-off entry.

