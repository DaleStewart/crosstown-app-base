<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Work-From-Home and Alternate Modes — Rider Guidance

_Runbook id: `RB-13-wfh-and-alternate-modes` · Rail lines L1/L2/L3 only._

During an active line-level disruption (`DSR-*` with `status=active`), riders may ask whether to come in, work from home, or use another mode. The copilot should:

1. Offer work-from-home as the default suggestion when the rider's role allows it. Do not assume the rider's role — ask, or qualify the answer ("if your role supports remote work …").
2. Mention surface alternatives only if a route exists in `route_graph.json` for their origin/destination pair.
3. Never quote a specific fare amount, refund policy, or reimbursement amount — only reference the `advisories` field of the active disruption verbatim.
4. Never recommend a private taxi-share, app-based rideshare, or specific bus operator by name. Use generic phrasing ("a connecting line on L2 or L3").
5. Cite the disruption record and this runbook in every reply.
