<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Comms Jitter to Wayside Controllers — Runbook

_Runbook id: `RB-03-comms-jitter` · Rail lines L1/L2/L3 only._

Jitter above 120ms to any wayside controller (WC-NN) is a precursor to door-hold and dwell anomalies.

Steps:
1. Identify the affected WC from `event_type=comms.jitter`.
2. Verify the fiber path; the redundant path is enabled by default.
3. If jitter persists after a path switch, roll the controller firmware to the previously known-good version.
4. Correlate against `doors.held` and `train.dwell` events on the line.

