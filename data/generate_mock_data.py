"""MOCK DATA — NOT FROM MTA. For hackathon training only.

Generates synthetic train-control logs, runbooks, and incident seeds for the
MTA AI Hackathon accelerator. Deterministic via SEED.

Run:  python data/generate_mock_data.py
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 20260519
ROOT = Path(__file__).resolve().parent
LOGS_DIR = ROOT / "mock_logs"
RUNBOOKS_DIR = ROOT / "runbooks"

LINES = ["L1", "L2", "L3"]
STATIONS = [
    "Atlas", "Beacon", "Crescent", "Dune", "Eastgate", "Falcon",
    "Granite", "Harbor", "Iris", "Junction", "Keystone", "Lantern",
    "Meridian", "Northpoint", "Orchard", "Pioneer", "Quarry",
    "Rampart", "Summit", "Tideway",
]
SEVERITIES = ["INFO", "WARN", "ERROR", "CRITICAL"]
SEVERITY_WEIGHTS = [70, 20, 8, 2]

EVENT_TEMPLATES = [
    ("INFO",     "train.dwell",        "Train {train} dwelled {dwell}s at {station} ({line})."),
    ("INFO",     "train.departure",    "Train {train} departed {station} on {line} at speed {speed} km/h."),
    ("INFO",     "signal.green",       "Signal SG-{sig} at {station} cleared to GREEN for {line}."),
    ("WARN",     "doors.held",         "Doors held open on train {train} at {station} for {dwell}s (threshold 45s)."),
    ("WARN",     "comms.jitter",       "Comms jitter to wayside controller WC-{wc} on {line}: {ms}ms (>120ms)."),
    ("WARN",     "speed.restriction",  "Temporary speed restriction issued: {line} between {station} and {station2}, limit {speed} km/h."),
    ("ERROR",    "interlock.fault",    "Interlock fault at {station} on {line}: relay R-{relay} failed self-test."),
    ("ERROR",    "trackcircuit.shunt", "Track circuit TC-{tc} on {line} reporting persistent shunt near {station}."),
    ("ERROR",    "axle.counter",       "Axle counter AC-{ac} on {line} discrepancy at {station}: counted {count}, expected {expected}."),
    ("CRITICAL", "emergency.brake",    "Emergency brake applied on train {train} approaching {station} on {line}. Trigger: {trigger}."),
    ("CRITICAL", "loss.of.shunt",      "Loss of shunt detected on {line} at TC-{tc}; line forced to manual block working."),
    ("CRITICAL", "power.trip",         "Traction power trip on {line} sector {sector}; standby supply engaged."),
]

PATTERN_SIGNATURES = {
    "cascading_doors_then_dwell": [
        "doors.held",
        "train.dwell",
        "comms.jitter",
    ],
    "interlock_pre_emergency": [
        "interlock.fault",
        "speed.restriction",
        "emergency.brake",
    ],
    "shunt_then_power_trip": [
        "trackcircuit.shunt",
        "loss.of.shunt",
        "power.trip",
    ],
}

INCIDENT_SUMMARIES = [
    ("L1", "Cascading dwell on northbound peak: doors held at Beacon triggered a 14-train queue."),
    ("L2", "Interlock fault at Meridian preceded emergency brake on train 1042; relay R-117 replaced."),
    ("L3", "Loss of shunt on TC-228 forced manual block working for 47 minutes mid-day."),
    ("L1", "Comms jitter spike to WC-09 correlated with a string of door-held warnings between Atlas and Crescent."),
    ("L2", "Axle counter AC-44 discrepancy at Pioneer turned out to be a known sensor mis-calibration."),
    ("L3", "Traction power trip in sector 7-B; standby supply engaged within 8s, no service impact."),
    ("L1", "Speed restriction held for 3 hours between Granite and Harbor pending track-circuit investigation."),
    ("L2", "False-positive emergency brake event from train 2103 traced to a stuck onboard sensor."),
    ("L3", "Shunt-then-trip pattern recurred at TC-228 — flagged as candidate for predictive maintenance."),
    ("L1", "Door-held warnings clustered at Junction during a planned event; staffing adjustment recommended."),
    ("L2", "Interlock self-test failures during overnight maintenance window; cleared by manual reseat."),
    ("L3", "Wayside controller WC-22 firmware rollback after a comms jitter regression."),
    ("L1", "Investigation of repeated dwell at Iris northbound found a misaligned platform sensor."),
    ("L2", "Critical: emergency brake on train 1207 approaching Summit; cause confirmed wayside spurious signal."),
    ("L3", "Axle counter chain on northbound L3 re-baselined after 36 hours of intermittent discrepancies."),
    ("L1", "Comms jitter from WC-05 resolved by switching to the redundant fiber path."),
    ("L2", "Door held + dwell + jitter cluster at Beacon — see runbook 03 for the canonical pattern."),
    ("L3", "Power trip sector 7-B recurrence: candidate for the 'shunt-then-trip' signature in runbook 07."),
    ("L1", "Severity-warn flood at Pioneer turned out to be a logging-level regression on the controller."),
    ("L2", "Interlock-pre-emergency signature confirmed on overnight train 2099; no injuries; track held 22min."),
]


def weighted(items: list[str], weights: list[int], rng: random.Random) -> str:
    return rng.choices(items, weights=weights, k=1)[0]


def generate_logs(rng: random.Random, n: int = 5000) -> list[dict]:
    rows: list[dict] = []
    start = datetime(2026, 5, 18, 4, 0, 0, tzinfo=timezone.utc)
    for i in range(n):
        ts = start + timedelta(seconds=int(rng.expovariate(1 / 18)) * i % 86400 + i * 15)
        sev = weighted(SEVERITIES, SEVERITY_WEIGHTS, rng)
        candidates = [t for t in EVENT_TEMPLATES if t[0] == sev]
        sev_label, event_type, template = rng.choice(candidates)
        line = rng.choice(LINES)
        station = rng.choice(STATIONS)
        station2 = rng.choice([s for s in STATIONS if s != station])
        msg = template.format(
            train=rng.randint(1000, 2999),
            dwell=rng.choice([30, 45, 60, 90, 120, 180]),
            station=station,
            station2=station2,
            line=line,
            speed=rng.choice([15, 25, 40, 60, 80]),
            sig=rng.randint(1, 99),
            wc=f"{rng.randint(1, 30):02d}",
            ms=rng.randint(80, 260),
            relay=rng.randint(100, 199),
            tc=rng.randint(100, 299),
            ac=rng.randint(1, 80),
            count=rng.randint(1, 8),
            expected=rng.randint(1, 8),
            trigger=rng.choice([
                "wayside spurious signal",
                "onboard sensor fault",
                "low brake pressure",
                "operator pull",
            ]),
            sector=f"{rng.randint(1,9)}-{rng.choice('AB')}",
        )
        rows.append({
            "log_id": f"L-{i:06d}",
            "timestamp": ts.isoformat(),
            "line": line,
            "station": station,
            "severity": sev_label,
            "event_type": event_type,
            "message": msg,
            "operator_id": f"OP-{rng.randint(100, 999)}",
        })
    return rows


def generate_incidents(rng: random.Random) -> list[dict]:
    incidents: list[dict] = []
    base = datetime(2026, 5, 18, 6, 0, 0, tzinfo=timezone.utc)
    for i, (line, summary) in enumerate(INCIDENT_SUMMARIES):
        opened = base + timedelta(hours=i * 3 + rng.randint(0, 90) / 60)
        closed = opened + timedelta(minutes=rng.randint(15, 240))
        sig = rng.choice(list(PATTERN_SIGNATURES.keys()) + [None, None])
        incidents.append({
            "incidentId": f"INC-{i + 1001}",
            "line": line,
            "openedAt": opened.isoformat(),
            "closedAt": closed.isoformat(),
            "severity": rng.choice(["WARN", "ERROR", "CRITICAL"]),
            "summary": summary,
            "patternSignature": sig,
            "relatedRunbook": rng.choice([
                "RB-01-doors-held", "RB-03-comms-jitter",
                "RB-05-interlock-fault", "RB-07-shunt-then-trip",
                "RB-09-axle-counter",
            ]),
        })
    return incidents


# ---- Runbooks ----------------------------------------------------------------
RUNBOOKS: list[tuple[str, str, str]] = [
    ("RB-01-doors-held.md",
     "Doors Held Open — Triage Runbook",
     """When a train reports doors held open beyond the 45s threshold, the on-call controller should:

1. Confirm the dwell event in the live log feed (`event_type=doors.held`).
2. Check for adjacent `train.dwell` warnings on the same line within ±5 minutes — a cluster usually means crowding.
3. If `comms.jitter` warnings are also present from the same wayside controller, escalate to comms-on-call.
4. Issue a hold to following trains if the queue exceeds 3.
5. Open an incident with `patternSignature=cascading_doors_then_dwell` if all three event types are present in the window.
"""),
    ("RB-02-speed-restriction.md",
     "Temporary Speed Restriction — Application Runbook",
     """Speed restrictions are applied when track condition or signaling integrity is in question.

- A restriction is logged with `event_type=speed.restriction` and a bounded line segment.
- Restrictions auto-expire after 8 hours unless renewed.
- If a restriction is followed by `emergency.brake` events on the same segment, treat as a candidate for the interlock-pre-emergency signature (see RB-05).
- Document the cause and the inspection result in the incident notes.
"""),
    ("RB-03-comms-jitter.md",
     "Comms Jitter to Wayside Controllers — Runbook",
     """Jitter above 120ms to any wayside controller (WC-NN) is a precursor to door-hold and dwell anomalies.

Steps:
1. Identify the affected WC from `event_type=comms.jitter`.
2. Verify the fiber path; the redundant path is enabled by default.
3. If jitter persists after a path switch, roll the controller firmware to the previously known-good version.
4. Correlate against `doors.held` and `train.dwell` events on the line.
"""),
    ("RB-04-track-circuit-shunt.md",
     "Track Circuit Shunt — Investigation Runbook",
     """Persistent shunt indications on a track circuit (TC-NNN) can indicate contamination, broken bond, or wet leaves.

- Confirm with a manual test if maintenance is on site.
- If shunt persists, watch for `loss.of.shunt` — that elevates to manual block working.
- Combination of `trackcircuit.shunt` → `loss.of.shunt` → `power.trip` is the canonical shunt-then-trip signature; flag for predictive maintenance.
"""),
    ("RB-05-interlock-fault.md",
     "Interlock Fault — Runbook",
     """Interlock self-test failures show up as `event_type=interlock.fault`.

Sequence to watch for: `interlock.fault` → `speed.restriction` → `emergency.brake` within 30 minutes. That is the interlock-pre-emergency signature.

Replacement of relay R-NNN is the most common fix. Always re-run the self-test after reseat.
"""),
    ("RB-06-emergency-brake.md",
     "Emergency Brake — Post-Event Runbook",
     """When a train triggers `event_type=emergency.brake`:

1. Confirm the trigger field (`wayside spurious signal`, `onboard sensor fault`, `low brake pressure`, `operator pull`).
2. Inspect the train at the next safe stop.
3. If trigger = `wayside spurious signal`, file against the wayside team and check for adjacent interlock faults.
4. File an incident with the related runbook reference.
"""),
    ("RB-07-shunt-then-trip.md",
     "Shunt-then-Trip Signature — Predictive Maintenance",
     """The canonical sequence:

1. `trackcircuit.shunt` on TC-NNN.
2. `loss.of.shunt` on the same TC within 90 minutes.
3. `power.trip` in the surrounding sector within 4 hours.

When detected, recommend a daytime inspection of the bonding and any nearby junctions. This signature has historically correlated with bonding degradation rather than rolling-stock faults.
"""),
    ("RB-08-traction-power-trip.md",
     "Traction Power Trip — Runbook",
     """Power trips (`event_type=power.trip`) automatically engage standby supply within 8 seconds.

- Verify the standby engaged (look for the follow-up INFO event).
- If standby fails to engage, escalate immediately to control center.
- Repeated trips in the same sector across 48 hours are a known fingerprint of the shunt-then-trip signature.
"""),
    ("RB-09-axle-counter.md",
     "Axle Counter Discrepancy — Runbook",
     """Axle counters (AC-NN) report counted vs expected vehicle counts.

A single discrepancy is almost always sensor mis-calibration. A run of three or more on the same counter within an hour is a likely physical fault. Re-baseline only after on-site inspection.
"""),
    ("RB-10-controller-firmware.md",
     "Controller Firmware Rollback — Runbook",
     """When comms jitter, interlock faults, or axle-counter discrepancies cluster on the same controller after a firmware push:

1. Roll the controller back to the previous known-good version.
2. Watch for 90 minutes; the cluster should clear.
3. File the regression with the firmware team and link the affected logs.
"""),
]


def write_runbooks() -> None:
    RUNBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, title, body in RUNBOOKS:
        path = RUNBOOKS_DIR / filename
        content = (
            "<!-- MOCK DATA — NOT FROM MTA. For hackathon training only. -->\n"
            f"# {title}\n\n"
            f"_Runbook id: `{filename.removesuffix('.md')}` · Rail lines L1/L2/L3 only._\n\n"
            f"{body}\n"
        )
        path.write_text(content, encoding="utf-8", newline="\n")


def write_logs(rows: list[dict]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    header_csv = "# MOCK DATA — NOT FROM MTA. For hackathon training only.\n"
    csv_path = LOGS_DIR / "logs.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        f.write(header_csv)
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    jsonl_path = LOGS_DIR / "logs.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write('{"_comment": "MOCK DATA — NOT FROM MTA. For hackathon training only."}\n')
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def write_incidents(incidents: list[dict]) -> None:
    out = {
        "_comment": "MOCK DATA — NOT FROM MTA. For hackathon training only.",
        "incidents": incidents,
    }
    (ROOT / "seed_incidents.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8", newline="\n"
    )


def main() -> None:
    rng = random.Random(SEED)
    logs = generate_logs(rng)
    incidents = generate_incidents(rng)
    write_logs(logs)
    write_incidents(incidents)
    write_runbooks()
    print(f"Wrote {len(logs)} log rows, {len(incidents)} incidents, {len(RUNBOOKS)} runbooks.")


if __name__ == "__main__":
    main()
