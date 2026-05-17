/**
 * Types for the live demo transcript stream (SSE).
 */

export interface TranscriptEventBase {
  call_id: string;
  timestamp: string;
}

export interface CallStartedEvent extends TranscriptEventBase {
  type: 'call_started';
  phone_number: string;
}

export interface UserSpeechEvent extends TranscriptEventBase {
  type: 'user_speech';
  text: string;
}

export interface AgentSpeechEvent extends TranscriptEventBase {
  type: 'agent_speech';
  text: string;
}

export interface ToolCallEvent extends TranscriptEventBase {
  type: 'tool_call';
  tool: string;
  summary: string;
}

export interface CallEndedEvent extends TranscriptEventBase {
  type: 'call_ended';
  duration_seconds: number;
}

export type TranscriptEvent =
  | CallStartedEvent
  | UserSpeechEvent
  | AgentSpeechEvent
  | ToolCallEvent
  | CallEndedEvent;

export type CallStatus = 'idle' | 'active' | 'ended';

export interface CallState {
  status: CallStatus;
  callId: string | null;
  durationSeconds: number | null;
  events: TranscriptEvent[];
}
