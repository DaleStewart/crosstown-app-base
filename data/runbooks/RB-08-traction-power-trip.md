<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Traction Power Trip — Runbook

_Runbook id: `RB-08-traction-power-trip` · Rail lines L1/L2/L3 only._

Power trips (`event_type=power.trip`) automatically engage standby supply within 8 seconds.

- Verify the standby engaged (look for the follow-up INFO event).
- If standby fails to engage, escalate immediately to control center.
- Repeated trips in the same sector across 48 hours are a known fingerprint of the shunt-then-trip signature.

