<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Shunt-then-Trip Signature — Predictive Maintenance

_Runbook id: `RB-07-shunt-then-trip` · Rail lines L1/L2/L3 only._

The canonical sequence:

1. `trackcircuit.shunt` on TC-NNN.
2. `loss.of.shunt` on the same TC within 90 minutes.
3. `power.trip` in the surrounding sector within 4 hours.

When detected, recommend a daytime inspection of the bonding and any nearby junctions. This signature has historically correlated with bonding degradation rather than rolling-stock faults.

