-- Extension 09 — Postgres Target
-- Fixture schema for the incidents table.
-- This file is used BOTH by the real Postgres migration AND by the SQLite in-memory
-- fixture in the test suite. Keep it compatible with both dialects (no Postgres-only types).

CREATE TABLE IF NOT EXISTS incidents (
    id          INTEGER PRIMARY KEY,
    line        TEXT    NOT NULL CHECK (line IN ('L1', 'L2', 'L3')),
    system      TEXT    NOT NULL,
    description TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'open',
    created_at  TEXT    NOT NULL  -- ISO 8601 string; avoids TIMESTAMPTZ dialect difference
);

-- Seed data — fictional incidents only
INSERT INTO incidents (id, line, system, description, status, created_at) VALUES
    (1, 'L1', 'signal',  'Signal fault at sector 4 — intermittent red-light failure',       'open',     '2025-11-01T03:12:00Z'),
    (2, 'L2', 'SCADA',   'SCADA bridge-7 timeout — no heartbeat for 90 s',                  'resolved', '2025-11-01T03:45:00Z'),
    (3, 'L3', 'power',   'Power fluctuation sector 2 — voltage drop to 580 V (nominal 630)','open',     '2025-11-02T14:05:00Z');
