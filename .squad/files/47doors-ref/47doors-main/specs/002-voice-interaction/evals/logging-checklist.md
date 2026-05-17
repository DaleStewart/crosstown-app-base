# 🔍 Voice Interaction Logging Checklist

**Feature:** 002-voice-interaction  
**Last Updated:** 2026-03-13

---

## Required Audit Fields per Voice Session

Every voice interaction must produce an audit log entry containing all of the following fields:

- [ ] `session_id` — UUID matching both text and voice sessions
- [ ] `input_modality` — `"voice"` for voice interactions
- [ ] `tool_name` — name of pipeline tool invoked (e.g., `analyze_and_route_query`)
- [ ] `pii_detected` — boolean flag (`true` if PII was found and filtered, `false` otherwise)
- [ ] `timestamp` — ISO 8601 UTC (e.g., `2026-03-13T14:00:00Z`)
- [ ] `user_id_hash` — SHA-256 hashed user identifier (never the raw user ID)

---

## Verification Steps

1. Start a voice session in mock mode (`MOCK_MODE=true`)
2. Execute a tool call — say: *"I forgot my password"*
3. Check backend logs (stdout or log file) for the audit entry
4. Verify all 6 fields above are present in the log output

---

## Automated Verification

Run the PII filter test suite to confirm filtering logic is correct:

```bash
cd backend && python -m pytest tests/test_voice/test_pii_filter.py -v
```

**Expected:** All 5 PII filter tests pass

---

## What Must NOT Appear in Logs

- ❌ Raw audio data or audio file paths
- ❌ Unfiltered PII (SSN, email, phone number, credit card number)
- ❌ Azure OpenAI API keys or ephemeral session tokens
- ❌ WebRTC SDP offers/answers (contain ICE candidates with IP addresses)
