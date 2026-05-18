# Audio regression diagnosis — 2026-05-18 ~11:15 ET

**Root cause: B.** Orchestrator relay committed a 0.00ms audio buffer to Foundry (`input_audio_buffer_commit_empty event_id=event_DgtyVSvJslOzlEzUhcsVp`); insufficient audio in the first buffer caused Whisper to hallucinate "Ozone on the surface" instead of "Brooklyn". Fix owner: **Stark** — add ≥100ms guard before calling `input_audio_buffer.commit`.
