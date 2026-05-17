#!/usr/bin/env bash
# scripts/smoke-test.sh — Crosstown Transit AI deploy smoke test (FR-009)
#
# Usage:
#   bash scripts/smoke-test.sh <frontend-url> [--full]
#
# Exits non-zero on first failure with: FAIL at check N: <reason>
# On success prints: smoke OK in <Ns> (4 checks)   or   (5 checks) for --full
#
# Reference: specs/002-tuesday-demo/plan.md §2.1 and spec.md FR-009.
# Phase-0 audit corrections applied (override plan where it disagrees):
#   - Health endpoint is /health (not /healthz) on orchestrator + log_analyst + service_advisor
#   - Frontend env var is FRONTEND_URL (not SERVICE_FRONTEND_URI)
#   - service_advisor port is 8002
#
# All data is synthetic; rail lines L1/L2/L3 are fictional.

set -euo pipefail

# ---------- args ----------
if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/smoke-test.sh <frontend-url> [--full]" >&2
  exit 2
fi

FRONTEND_URL="${1%/}"   # strip trailing slash
FULL=0
if [[ $# -ge 2 && "$2" == "--full" ]]; then
  FULL=1
fi

ORCHESTRATOR_URL="${ORCHESTRATOR_URL:-}"
ORCHESTRATOR_URL="${ORCHESTRATOR_URL%/}"

# ---------- jq vs grep fallback ----------
JSON_PATH="grep"
if command -v jq >/dev/null 2>&1; then
  JSON_PATH="jq"
fi
echo "# smoke-test: JSON parser = ${JSON_PATH}"

START_TS=$(date +%s)

fail() {
  # fail <check-number> <reason>
  echo "FAIL at check $1: $2" >&2
  exit 1
}

# get_field <json-string> <field>   (top-level scalar, jq if available)
get_field() {
  local body="$1" field="$2"
  if [[ "$JSON_PATH" == "jq" ]]; then
    printf '%s' "$body" | jq -r --arg f "$field" '.[$f] // empty' 2>/dev/null || true
  else
    # crude grep fallback: "field":"value" or "field":value (string only)
    printf '%s' "$body" \
      | grep -oE "\"$field\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
      | head -n1 \
      | sed -E "s/^\"$field\"[[:space:]]*:[[:space:]]*\"([^\"]*)\"$/\1/"
  fi
}

# has_nonempty_array <json-string> <field>
has_nonempty_array() {
  local body="$1" field="$2"
  if [[ "$JSON_PATH" == "jq" ]]; then
    local n
    n=$(printf '%s' "$body" | jq -r --arg f "$field" '(.[$f] // []) | length' 2>/dev/null || echo 0)
    [[ "${n:-0}" =~ ^[0-9]+$ && "$n" -gt 0 ]]
  else
    # grep fallback: look for "field": [ { ... } ] with at least one char inside
    printf '%s' "$body" | grep -oE "\"$field\"[[:space:]]*:[[:space:]]*\[[^]]*[^][:space:]][^]]*\]" >/dev/null
  fi
}

# has_key <json-string> <field>
has_key() {
  local body="$1" field="$2"
  if [[ "$JSON_PATH" == "jq" ]]; then
    printf '%s' "$body" | jq -e --arg f "$field" 'has($f)' >/dev/null 2>&1
  else
    printf '%s' "$body" | grep -qE "\"$field\"[[:space:]]*:"
  fi
}

# http_get_with_status <url>  -> sets HTTP_BODY, HTTP_CODE
http_get_with_status() {
  local url="$1" tmp
  tmp=$(mktemp -t smoke-XXXXXX 2>/dev/null || mktemp)
  set +e
  HTTP_CODE=$(curl --silent --show-error --max-time 10 \
                   --output "$tmp" --write-out '%{http_code}' "$url" 2>/dev/null)
  local rc=$?
  set -e
  if [[ $rc -ne 0 || -z "$HTTP_CODE" ]]; then
    HTTP_CODE="000"
  fi
  HTTP_BODY=$(cat "$tmp")
  rm -f "$tmp"
}

# http_post_json <url> <json-body>
http_post_json() {
  local url="$1" payload="$2" tmp
  tmp=$(mktemp -t smoke-XXXXXX 2>/dev/null || mktemp)
  set +e
  HTTP_CODE=$(curl --silent --show-error --max-time 10 \
                   -H 'Content-Type: application/json' \
                   -d "$payload" \
                   --output "$tmp" --write-out '%{http_code}' "$url" 2>/dev/null)
  local rc=$?
  set -e
  if [[ $rc -ne 0 || -z "$HTTP_CODE" ]]; then
    HTTP_CODE="000"
  fi
  HTTP_BODY=$(cat "$tmp")
  rm -f "$tmp"
}

# ---------- Check 1: frontend root ----------
echo "# check 1: GET ${FRONTEND_URL}/ — expect 200 + Crosstown marker (not Hello World)"
http_get_with_status "${FRONTEND_URL}/"
if [[ "$HTTP_CODE" != "200" ]]; then
  fail 1 "GET / returned HTTP ${HTTP_CODE}"
fi
# Hard-fail on the ACA quickstart placeholder image first (per task spec).
if printf '%s' "$HTTP_BODY" | grep -qi 'Your container app is running'; then
  fail 1 "Hello World quickstart placeholder detected"
fi
# Accept either the app marker ("Crosstown") or the SPA root div as proof of the real bundle.
if ! printf '%s' "$HTTP_BODY" | grep -qiE 'Crosstown|<div[^>]+id="root"'; then
  fail 1 "body missing 'Crosstown' / app marker — got $(printf '%s' "$HTTP_BODY" | head -c 80 | tr -d '\n')"
fi
echo "  check 1 PASS"

# ---------- Check 2: frontend /api/health (nginx -> orchestrator /health) ----------
# Retries for up to SMOKE_RETRY_SECONDS (default 90) to tolerate ACA revision-flip lag.
echo "# check 2: GET ${FRONTEND_URL}/api/health — expect 200 JSON {status, service:orchestrator}"
_c2_budget="${SMOKE_RETRY_SECONDS:-90}"
_c2_deadline=$(( $(date +%s) + _c2_budget ))
_c2_sleep=5
_c2_attempt=0
_c2_max=$(( _c2_budget / 15 + 3 ))
status_v=""
service_v=""
while true; do
  _c2_attempt=$(( _c2_attempt + 1 ))
  http_get_with_status "${FRONTEND_URL}/api/health"
  if [[ "$HTTP_CODE" != "200" ]]; then
    fail 2 "GET /api/health returned HTTP ${HTTP_CODE} (nginx rewrite likely broken)"
  fi
  status_v=$(get_field "$HTTP_BODY" "status")
  service_v=$(get_field "$HTTP_BODY" "service")
  if [[ "$status_v" == "ok" || "$status_v" == "degraded" ]] && [[ "$service_v" == "orchestrator" ]]; then
    break
  fi
  if [[ $(date +%s) -ge $_c2_deadline ]]; then
    if [[ "$status_v" != "ok" && "$status_v" != "degraded" ]]; then
      fail 2 "status='${status_v}', expected 'ok' or 'degraded'"
    fi
    fail 2 "service='${service_v}', expected 'orchestrator' (nginx rewrite hit wrong upstream)"
  fi
  echo "# retrying check 2 (revision flip): attempt $(( _c2_attempt + 1 ))/${_c2_max}..."
  sleep "$_c2_sleep"
  _c2_sleep=$(( _c2_sleep * 2 < 15 ? _c2_sleep * 2 : 15 ))
done
echo "  check 2 PASS (status=${status_v})"

# ---------- Check 3: direct orchestrator /health (optional) ----------
if [[ -n "$ORCHESTRATOR_URL" ]]; then
  echo "# check 3: GET ${ORCHESTRATOR_URL}/health — expect 200"
  http_get_with_status "${ORCHESTRATOR_URL}/health"
  if [[ "$HTTP_CODE" != "200" ]]; then
    fail 3 "GET ${ORCHESTRATOR_URL}/health returned HTTP ${HTTP_CODE}"
  fi
  echo "  check 3 PASS"
else
  echo "  check 3 SKIP — ORCHESTRATOR_URL not set (warning, not failure)"
fi

# ---------- Check 4: POST /api/turn ----------
# Retries for up to SMOKE_RETRY_SECONDS (default 90) — first /api/turn after cold start is
# LLM-bound (~14s observed). Uses --max-time 30 so curl doesn't time out before the response.
echo "# check 4: POST ${FRONTEND_URL}/api/turn — expect 200 + non-empty text"
_c4_budget="${SMOKE_RETRY_SECONDS:-90}"
_c4_deadline=$(( $(date +%s) + _c4_budget ))
_c4_sleep=5
_c4_attempt=0
_c4_max=$(( _c4_budget / 15 + 3 ))
text_v=""
while true; do
  _c4_attempt=$(( _c4_attempt + 1 ))
  _c4_tmp=$(mktemp -t smoke-XXXXXX 2>/dev/null || mktemp)
  set +e
  HTTP_CODE=$(curl --silent --show-error --max-time 30 \
                   -H 'Content-Type: application/json' \
                   -d '{"text":"status of L1?"}' \
                   --output "$_c4_tmp" --write-out '%{http_code}' \
                   "${FRONTEND_URL}/api/turn" 2>/dev/null)
  _c4_rc=$?
  set -e
  if [[ $_c4_rc -ne 0 || -z "$HTTP_CODE" ]]; then HTTP_CODE="000"; fi
  HTTP_BODY=$(cat "$_c4_tmp"); rm -f "$_c4_tmp"
  if [[ "$HTTP_CODE" == "200" ]]; then
    text_v=$(get_field "$HTTP_BODY" "text")
    if [[ -n "$text_v" ]]; then break; fi
  fi
  if [[ $(date +%s) -ge $_c4_deadline ]]; then
    if [[ "$HTTP_CODE" != "200" ]]; then
      fail 4 "POST /api/turn returned HTTP ${HTTP_CODE}"
    fi
    fail 4 "'text' field missing or empty in /api/turn response"
  fi
  echo "# retrying check 4 (cold start): attempt $(( _c4_attempt + 1 ))/${_c4_max}..."
  sleep "$_c4_sleep"
  _c4_sleep=$(( _c4_sleep * 2 < 15 ? _c4_sleep * 2 : 15 ))
done
echo "  check 4 PASS (text length=${#text_v})"

# ---------- Check 5 (--full): six rehearsed demo prompts must each return citations[] ----------
if [[ "$FULL" -eq 1 ]]; then
  echo "# check 5 (--full): 6 rehearsed demo prompts must each return non-empty citations[]"

  # Demo prompts from specs/002-tuesday-demo/spec.md User Story 2.
  # Prompts 1-3 hit log-analyst tools; prompts 4-6 hit service-advisor tools.
  PROMPTS=(
    "Show me the most recent door-fault logs from station Atlantic"
    "Look at log L-001234 — is it part of a known pattern?"
    "Summarize incident INC-1001"
    "Is the L1 line running right now?"
    "S-Penn to S-East with the L1 disruption"
    "Are there shuttle buses for L1?"
  )

  idx=0
  for p in "${PROMPTS[@]}"; do
    idx=$((idx + 1))
    # JSON-escape: backslashes then double-quotes.
    esc=${p//\\/\\\\}
    esc=${esc//\"/\\\"}
    payload="{\"text\":\"${esc}\"}"
    echo "  prompt ${idx}/6: ${p}"
    http_post_json "${FRONTEND_URL}/api/turn" "$payload"
    if [[ "$HTTP_CODE" != "200" ]]; then
      fail 5 "prompt ${idx} returned HTTP ${HTTP_CODE}"
    fi
    if ! has_key "$HTTP_BODY" "citations"; then
      fail 5 "prompt ${idx} response missing 'citations' key"
    fi
    if ! has_nonempty_array "$HTTP_BODY" "citations"; then
      fail 5 "prompt ${idx} returned empty citations[] (uncited turn)"
    fi
  done
  echo "  check 5 PASS"
fi

# ---------- summary ----------
END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))
N=4
[[ "$FULL" -eq 1 ]] && N=5
echo "smoke OK in ${ELAPSED}s (${N} checks)"
