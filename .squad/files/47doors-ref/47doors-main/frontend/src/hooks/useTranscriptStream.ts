/**
 * Hook for connecting to the live phone transcript SSE stream.
 * Auto-reconnects via EventSource. Accumulates events per call.
 */

import { useEffect, useRef, useCallback, useReducer } from 'react';
import type { TranscriptEvent, CallState } from '../types/demo';

type Action =
  | { type: 'EVENT'; event: TranscriptEvent }
  | { type: 'RESET' }
  | { type: 'CONNECTION_ERROR' };

const initialState: CallState = {
  status: 'idle',
  callId: null,
  durationSeconds: null,
  events: [],
};

function reducer(state: CallState, action: Action): CallState {
  switch (action.type) {
    case 'EVENT': {
      const evt = action.event;
      if (evt.type === 'call_started') {
        return {
          status: 'active',
          callId: evt.call_id,
          durationSeconds: null,
          events: [evt],
        };
      }
      if (evt.type === 'call_ended') {
        return {
          ...state,
          status: 'ended',
          durationSeconds: evt.duration_seconds,
          events: [...state.events, evt],
        };
      }
      return {
        ...state,
        events: [...state.events, evt],
      };
    }
    case 'RESET':
      return initialState;
    case 'CONNECTION_ERROR':
      return state; // EventSource auto-reconnects; keep state
    default:
      return state;
  }
}

const SSE_URL = '/api/phone/transcripts/stream';

export function useTranscriptStream() {
  const [callState, dispatch] = useReducer(reducer, initialState);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource(SSE_URL);
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as TranscriptEvent;
        dispatch({ type: 'EVENT', event: data });
      } catch {
        // ignore malformed events
      }
    };

    es.onerror = () => {
      dispatch({ type: 'CONNECTION_ERROR' });
      // EventSource auto-reconnects
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  return { callState, reset };
}
