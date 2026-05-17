<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Full-Line Shutdown — Rider Contingency Playbook

_Runbook id: `RB-11-line-shutdown-contingency` · Rail lines L1/L2/L3 only._

When an entire line is suspended for a multi-hour or multi-day disruption, the rider-facing copilot must:

1. State only what is in the active `DSR-*` disruption record. Do not invent a resume time. If `estimated_resume` is `"unknown"`, say "no resume time has been published yet."
2. Cite the `disruption_id` for every status claim and the parent runbook for guidance.
3. Surface the available bridging plan from `RB-12-shuttle-bus-bridging` when the rider's origin or destination is in `affected_stations`.
4. Offer work-from-home / alternate-mode guidance from `RB-13-wfh-and-alternate-modes` when the rider is uncertain about commuting.
5. Refuse to comment on the cause of the disruption, employees, union positions, or fare disputes. Only repeat fare facts that appear verbatim in `advisories`.
6. If asked about other lines, confirm they are operating normally only if no `DSR-*` record references them.
