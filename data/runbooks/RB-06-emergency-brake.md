<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Emergency Brake — Post-Event Runbook

_Runbook id: `RB-06-emergency-brake` · Rail lines L1/L2/L3 only._

When a train triggers `event_type=emergency.brake`:

1. Confirm the trigger field (`wayside spurious signal`, `onboard sensor fault`, `low brake pressure`, `operator pull`).
2. Inspect the train at the next safe stop.
3. If trigger = `wayside spurious signal`, file against the wayside team and check for adjacent interlock faults.
4. File an incident with the related runbook reference.

