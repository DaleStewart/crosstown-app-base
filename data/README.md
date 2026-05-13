# MOCK DATA — NOT FROM MTA. For hackathon training only.

This folder contains **synthetic** train-control telemetry and runbooks generated for the
NYCMTA AI Hackathon accelerator. Nothing here references real MTA systems, employees,
schedules, or telemetry.

- Rail lines are fictional: **L1, L2, L3**.
- Stations are fictional placeholder names (Atlas, Beacon, Crescent, …).
- Operator IDs are random tokens with the prefix `OP-`.
- Timestamps are seeded (`SEED=20260519`) so every regeneration is identical.

## Layout
```
data/
├── mock_logs/
│   ├── logs.csv        # ~5,000 train-control log rows
│   └── logs.jsonl      # same rows, JSON Lines (indexed into Azure AI Search)
├── runbooks/           # 10 markdown runbooks (indexed into Azure AI Search)
├── seed_incidents.json # ~20 incident docs (loaded into Cosmos `incidents`)
└── generate_mock_data.py
```

## Regenerate
```bash
python data/generate_mock_data.py
```
Deterministic output — re-running yields byte-identical files.
