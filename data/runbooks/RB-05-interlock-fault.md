<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Interlock Fault — Runbook

_Runbook id: `RB-05-interlock-fault` · Rail lines L1/L2/L3 only._

Interlock self-test failures show up as `event_type=interlock.fault`.

Sequence to watch for: `interlock.fault` → `speed.restriction` → `emergency.brake` within 30 minutes. That is the interlock-pre-emergency signature.

Replacement of relay R-NNN is the most common fix. Always re-run the self-test after reseat.

