<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Temporary Speed Restriction — Application Runbook

_Runbook id: `RB-02-speed-restriction` · Rail lines L1/L2/L3 only._

Speed restrictions are applied when track condition or signaling integrity is in question.

- A restriction is logged with `event_type=speed.restriction` and a bounded line segment.
- Restrictions auto-expire after 8 hours unless renewed.
- If a restriction is followed by `emergency.brake` events on the same segment, treat as a candidate for the interlock-pre-emergency signature (see RB-05).
- Document the cause and the inspection result in the incident notes.

