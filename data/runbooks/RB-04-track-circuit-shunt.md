<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Track Circuit Shunt — Investigation Runbook

_Runbook id: `RB-04-track-circuit-shunt` · Rail lines L1/L2/L3 only._

Persistent shunt indications on a track circuit (TC-NNN) can indicate contamination, broken bond, or wet leaves.

- Confirm with a manual test if maintenance is on site.
- If shunt persists, watch for `loss.of.shunt` — that elevates to manual block working.
- Combination of `trackcircuit.shunt` → `loss.of.shunt` → `power.trip` is the canonical shunt-then-trip signature; flag for predictive maintenance.

