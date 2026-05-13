<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Controller Firmware Rollback — Runbook

_Runbook id: `RB-10-controller-firmware` · Rail lines L1/L2/L3 only._

When comms jitter, interlock faults, or axle-counter discrepancies cluster on the same controller after a firmware push:

1. Roll the controller back to the previous known-good version.
2. Watch for 90 minutes; the cluster should clear.
3. File the regression with the firmware team and link the affected logs.

