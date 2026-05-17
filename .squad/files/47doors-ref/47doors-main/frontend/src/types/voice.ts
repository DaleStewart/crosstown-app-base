/**
 * Voice interaction types for 47 Doors.
 * Mirrors backend voice_schemas.py / voice_enums.py.
 */

// =============================================================================
// Enums
// =============================================================================

/** UI state machine for voice interaction. */
export enum VoiceUIState {
  Idle       = "idle",
  Connecting = "connecting",
  Listening  = "listening",
  Processing = "processing",
  Speaking   = "speaking",
  Error      = "error",
}

// =============================================================================
// UI Types
// =============================================================================

/** A single voice transcript entry. */
export interface VoiceMessage {
  /** UUID for this transcript entry. */
  id: string;
  /** PII-filtered transcribed text. */
  content: string;
  /** Speaker role. */
  role: "user" | "assistant";
  /** When this turn was spoken. */
  timestamp: Date;
}

// =============================================================================
// Configuration Types
// =============================================================================

/** Configuration for the voice client. */
export interface VoiceConfig {
  /** URL for POST /api/realtime/session. */
  sessionEndpoint: string;
  /** URL for the WS tool-relay endpoint. */
  wsEndpoint: string;
  /** Azure voice name (default: "alloy"). */
  voice: string;
  /** Voice Activity Detection silence threshold in ms (default: 500). */
  vadThreshold: number;
}

// =============================================================================
// API Types
// =============================================================================

/** Response from POST /api/realtime/session. */
export interface RealtimeSessionResponse {
  /** Session identifier. */
  sessionId: string;
  /** Short-lived ephemeral credential (≤60s TTL). */
  token: string;
  /** Token expiry timestamp. */
  expiresAt: string;
  /** Azure OpenAI Realtime API WebRTC endpoint URL. */
  endpoint: string;
  /** Model deployment name. */
  deployment: string;
}

/** Health check response from GET /api/realtime/health. */
export interface VoiceHealthResponse {
  /** Whether the realtime API is available. */
  realtimeAvailable: boolean;
  /** Whether mock mode is active. */
  mockMode: boolean;
  /** Whether voice feature is enabled. */
  voiceEnabled: boolean;
}
