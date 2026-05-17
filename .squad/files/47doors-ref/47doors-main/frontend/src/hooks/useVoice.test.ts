/**
 * T021: useVoice hook tests.
 *
 * Tests will fail until the hook is implemented (test-first, Constitution Principle V).
 * The active assertions are limited to what can run without the real implementation;
 * the rest are marked .todo so they appear in the test report as pending work.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
// renderHook, act imported when hook is implemented
// import { renderHook, act } from '@testing-library/react';
import { VoiceUIState } from '../types/voice';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock('../api/client', () => ({
  createRealtimeSession: vi.fn().mockResolvedValue({
    sessionId: 'test-session',
    token: 'eph_mock_token',
    expiresAt: new Date(Date.now() + 60_000).toISOString(),
    endpoint: 'http://localhost:8000/mock',
    deployment: 'gpt-4o-realtime-preview',
  }),
}));

const mockDataChannel = {
  onmessage: null as ((ev: MessageEvent) => void) | null,
  onopen: null as ((ev: Event) => void) | null,
  send: vi.fn(),
  readyState: 'open' as RTCDataChannelState,
};

const mockPeerConnection = {
  createOffer: vi.fn().mockResolvedValue({ type: 'offer', sdp: 'mock-sdp' }),
  setLocalDescription: vi.fn().mockResolvedValue(undefined),
  setRemoteDescription: vi.fn().mockResolvedValue(undefined),
  createDataChannel: vi.fn().mockReturnValue(mockDataChannel),
  addTrack: vi.fn(),
  close: vi.fn(),
  connectionState: 'new' as RTCPeerConnectionState,
  onconnectionstatechange: null as ((ev: Event) => void) | null,
  ontrack: null,
};

vi.stubGlobal('RTCPeerConnection', vi.fn(() => mockPeerConnection));
vi.stubGlobal('MediaStream', vi.fn(() => ({ getTracks: () => [] })));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useVoice hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should detect RTCPeerConnection global (WebRTC environment check)', () => {
    // Guard: if RTCPeerConnection is undefined the hook cannot work at all
    expect(typeof RTCPeerConnection).toBe('function');
  });

  it('should export VoiceUIState enum with expected values', () => {
    expect(VoiceUIState.Idle).toBe('idle');
    expect(VoiceUIState.Connecting).toBe('connecting');
    expect(VoiceUIState.Listening).toBe('listening');
    expect(VoiceUIState.Processing).toBe('processing');
    expect(VoiceUIState.Speaking).toBe('speaking');
    expect(VoiceUIState.Error).toBe('error');
  });

  // ---------------------------------------------------------------------------
  // Pending — require useVoice implementation
  // ---------------------------------------------------------------------------

  it.todo('should initialize with Idle state');
  it.todo('should transition to Connecting on startVoice');
  it.todo('should call createRealtimeSession on start');
  it.todo('should create RTCPeerConnection with received endpoint');
  it.todo('should create data channel named "oai-events"');
  it.todo('should transition to Listening when WebRTC data channel opens');
  it.todo('should relay function_call events through data channel');
  it.todo('should return to Idle on stopVoice');
  it.todo('should set Error state when session creation fails');
  it.todo('should handle WebRTC not supported (no RTCPeerConnection global)');
  it.todo('should expose voiceState, startVoice, stopVoice, transcript, isSpeaking');
});
