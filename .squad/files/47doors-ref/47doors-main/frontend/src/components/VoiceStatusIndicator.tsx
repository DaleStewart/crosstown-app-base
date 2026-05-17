/**
 * VoiceStatusIndicator — shows current voice session state to the user.
 */

import React from 'react';
import { VoiceUIState } from '../types/voice';

interface VoiceStatusIndicatorProps {
  voiceState: VoiceUIState;
}

const stateConfig: Record<
  VoiceUIState,
  { label: string; color: string; pulse: boolean } | null
> = {
  [VoiceUIState.Idle]: null,
  [VoiceUIState.Connecting]: {
    label: 'Connecting…',
    color: 'bg-yellow-100 text-yellow-800',
    pulse: true,
  },
  [VoiceUIState.Listening]: {
    label: 'Listening — speak now',
    color: 'bg-green-100 text-green-800',
    pulse: true,
  },
  [VoiceUIState.Processing]: {
    label: 'Processing your request…',
    color: 'bg-blue-100 text-blue-800',
    pulse: false,
  },
  [VoiceUIState.Speaking]: {
    label: 'Agent is responding…',
    color: 'bg-green-100 text-green-700',
    pulse: true,
  },
  [VoiceUIState.Error]: {
    label: 'Voice unavailable',
    color: 'bg-red-100 text-red-800',
    pulse: false,
  },
};

export const VoiceStatusIndicator: React.FC<VoiceStatusIndicatorProps> = ({
  voiceState,
}) => {
  const config = stateConfig[voiceState];
  if (!config) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium
        ${config.color}
        ${config.pulse ? 'animate-pulse' : ''}
      `}
    >
      <span
        className={`w-2 h-2 rounded-full bg-current ${config.pulse ? 'animate-ping' : ''}`}
      />
      {config.label}
    </div>
  );
};
