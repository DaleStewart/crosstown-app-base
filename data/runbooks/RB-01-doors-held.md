<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Doors Held Open — Triage Runbook

_Runbook id: `RB-01-doors-held` · Rail lines L1/L2/L3 only._

When a train reports doors held open beyond the 45s threshold, the on-call controller should:

1. Confirm the dwell event in the live log feed (`event_type=doors.held`).
2. Check for adjacent `train.dwell` warnings on the same line within ±5 minutes — a cluster usually means crowding.
3. If `comms.jitter` warnings are also present from the same wayside controller, escalate to comms-on-call.
4. Issue a hold to following trains if the queue exceeds 3.
5. Open an incident with `patternSignature=cascading_doors_then_dwell` if all three event types are present in the window.

