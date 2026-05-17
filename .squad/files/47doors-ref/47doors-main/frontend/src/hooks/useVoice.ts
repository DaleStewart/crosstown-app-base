/**
 * useVoice — core hook for WebRTC-based voice interaction via Azure OpenAI Realtime API.
 */

import { useReducer, useCallback, useRef, useEffect } from 'react';
import { VoiceUIState, type VoiceMessage } from '../types/voice';
import { createRealtimeSession } from '../api/client';

interface VoiceState {
  voiceState: VoiceUIState;
  transcript: VoiceMessage[];
  error: string | null;
}

type VoiceAction =
  | { type: 'START_CONNECTING' }
  | { type: 'CONNECTED' }
  | { type: 'LISTENING' }
  | { type: 'PROCESSING' }
  | { type: 'SPEAKING' }
  | { type: 'STOP' }
  | { type: 'ERROR'; error: string }
  | { type: 'ADD_TRANSCRIPT'; message: VoiceMessage };

function voiceReducer(state: VoiceState, action: VoiceAction): VoiceState {
  switch (action.type) {
    case 'START_CONNECTING':
      return { ...state, voiceState: VoiceUIState.Connecting, error: null };
    case 'CONNECTED':
    case 'LISTENING':
      return { ...state, voiceState: VoiceUIState.Listening };
    case 'PROCESSING':
      return { ...state, voiceState: VoiceUIState.Processing };
    case 'SPEAKING':
      return { ...state, voiceState: VoiceUIState.Speaking };
    case 'STOP':
      return { ...state, voiceState: VoiceUIState.Idle, error: null };
    case 'ERROR':
      return { ...state, voiceState: VoiceUIState.Error, error: action.error };
    case 'ADD_TRANSCRIPT':
      return { ...state, transcript: [...state.transcript, action.message] };
    default:
      return state;
  }
}

interface UseVoiceOptions {
  sessionId?: string;
  voice?: string;
  onTranscript?: (message: VoiceMessage) => void;
}

export function useVoice(options: UseVoiceOptions = {}) {
  const [state, dispatch] = useReducer(voiceReducer, {
    voiceState: VoiceUIState.Idle,
    transcript: [],
    error: null,
  });

  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  // Stable ref for onTranscript callback to avoid stale closures
  const onTranscriptRef = useRef(options.onTranscript);
  useEffect(() => { onTranscriptRef.current = options.onTranscript; }, [options.onTranscript]);

  const isVoiceSupported =
    typeof window !== 'undefined' && typeof RTCPeerConnection !== 'undefined';

  const startVoice = useCallback(async () => {
    if (!isVoiceSupported) {
      dispatch({ type: 'ERROR', error: 'WebRTC is not supported in this browser' });
      return;
    }

    dispatch({ type: 'START_CONNECTING' });

    try {
      // 1. Get ephemeral token from backend
      const session = await createRealtimeSession({
        sessionId: options.sessionId,
        voice: options.voice ?? 'marin',
      });

      // 2. Create RTCPeerConnection
      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;

      // 3. Set up remote audio playback
      const audioEl = document.createElement('audio');
      audioEl.autoplay = true;
      audioElementRef.current = audioEl;

      pc.ontrack = (event) => {
        audioEl.srcObject = event.streams[0];
      };

      // 4. Add local mic audio
      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStream.getTracks().forEach((track) => pc.addTrack(track, micStream));

      // 5. Create data channel for Realtime API events
      const dc = pc.createDataChannel('oai-events');
      dataChannelRef.current = dc;

      dc.onopen = () => {
        // Send session.update with BOTH GA nested format AND preview flat format.
        // GA nested: audio.input.transcription, audio.output.voice
        // Preview flat: output_audio_transcription (needed since GA may not support audio.output.transcription)
        // The endpoint accepts what it supports and silently ignores the rest.
        dc.send(JSON.stringify({
          type: 'session.update',
          session: {
            output_audio_transcription: {
              model: 'whisper-1',
            },
            audio: {
              input: {
                transcription: {
                  model: 'whisper-1',
                },
              },
              output: {
                voice: options.voice ?? 'marin',
              },
            },
          },
        }));
        dispatch({ type: 'LISTENING' });
      };

      dc.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data as string);

          // Log all non-audio-delta events for debugging transcript issues
          if (data.type !== 'response.audio.delta') {
            console.log('[DC Event]', data.type);
          }

          if (
            data.type === 'response.output_audio_transcript.done' ||
            data.type === 'response.audio_transcript.done'
          ) {
            const message: VoiceMessage = {
              id: crypto.randomUUID(),
              content: data.transcript || '',
              role: 'assistant',
              timestamp: new Date(),
            };
            dispatch({ type: 'ADD_TRANSCRIPT', message });
            onTranscriptRef.current?.(message);
          } else if (data.type === 'conversation.item.input_audio_transcription.completed') {
            const message: VoiceMessage = {
              id: crypto.randomUUID(),
              content: data.transcript || '',
              role: 'user',
              timestamp: new Date(),
            };
            dispatch({ type: 'ADD_TRANSCRIPT', message });
            onTranscriptRef.current?.(message);
          } else if (data.type === 'response.output_item.done') {
            // Fallback: extract assistant transcript from completed output item
            // when response.audio_transcript.done is not sent
            const item = data.item;
            if (item?.type === 'message' && item?.role === 'assistant') {
              const audioPart = item.content?.find(
                (c: { type: string; transcript?: string }) => c.type === 'audio' && c.transcript
              );
              if (audioPart?.transcript) {
                const message: VoiceMessage = {
                  id: crypto.randomUUID(),
                  content: audioPart.transcript,
                  role: 'assistant',
                  timestamp: new Date(),
                };
                dispatch({ type: 'ADD_TRANSCRIPT', message });
                onTranscriptRef.current?.(message);
              }
            }
          } else if (data.type === 'response.function_call_arguments.done') {
            dispatch({ type: 'PROCESSING' });
          } else if (data.type === 'response.done') {
            dispatch({ type: 'LISTENING' });
          } else if (data.type === 'response.audio.delta') {
            dispatch({ type: 'SPEAKING' });
          }
        } catch (e) {
          console.error('Data channel message error:', e);
        }
      };

      // 6. Create and set local offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // 7. Exchange SDP with Azure OpenAI Realtime API via WebRTC
      const sdpResponse = await fetch(
        `${session.endpoint}/openai/v1/realtime/calls`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${session.token}`,
            'Content-Type': 'application/sdp',
          },
          body: offer.sdp,
        }
      );

      if (!sdpResponse.ok) {
        throw new Error(`WebRTC negotiation failed: ${sdpResponse.status}`);
      }

      const answerSdp = await sdpResponse.text();
      await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });

      // 8. Monitor connection state
      pc.onconnectionstatechange = () => {
        switch (pc.connectionState) {
          case 'connected':
            dispatch({ type: 'LISTENING' });
            break;
          case 'disconnected':
          case 'failed':
            dispatch({ type: 'ERROR', error: 'Connection lost' });
            break;
          case 'closed':
            dispatch({ type: 'STOP' });
            break;
        }
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start voice';
      dispatch({ type: 'ERROR', error: message });
      console.error('Voice start error:', error);
    }
  }, [isVoiceSupported, options.sessionId, options.voice]);

  const stopVoice = useCallback(() => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    if (dataChannelRef.current) {
      dataChannelRef.current.close();
      dataChannelRef.current = null;
    }
    if (audioElementRef.current) {
      audioElementRef.current.srcObject = null;
      audioElementRef.current = null;
    }
    dispatch({ type: 'STOP' });
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopVoice();
    };
  }, [stopVoice]);

  return {
    voiceState: state.voiceState,
    transcript: state.transcript,
    error: state.error,
    startVoice,
    stopVoice,
    isVoiceSupported,
  };
}
