<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->
# Shuttle Bus Bridging — Rider Guidance

_Runbook id: `RB-12-shuttle-bus-bridging` · Rail lines L1/L2/L3 only._

When a `DSR-*` record names a shuttle plan, the rider-facing copilot should:

1. Identify the affected segment between the listed `affected_stations`.
2. Quote the headway (e.g., "every 20 minutes") and travel-time band from the `advisories` field — do not invent values.
3. Always pair the shuttle plan with the surface alternative on a connecting line when one exists in `route_graph.json` (cross-honor pickup at S-Jamaica is the standard L1↔L2/L3 bridge for fictional `DSR-2026-001`).
4. If the rider's station is not in `affected_stations`, tell them the shuttle does not stop there and offer the nearest covered station instead.
5. Cite both the disruption record and this runbook.
