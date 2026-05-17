/**
 * VoiceMicButton — toggle button for starting/stopping voice conversation.
 */

import React from 'react';
import { MicrophoneIcon, ArrowPathIcon } from '@heroicons/react/24/solid';
import { VoiceUIState } from '../types/voice';

interface VoiceMicButtonProps {
  voiceState: VoiceUIState;
  onToggle: () => void;
  disabled?: boolean;
}

const stateStyles: Record<VoiceUIState, string> = {
  [VoiceUIState.Idle]: 'text-gray-400 hover:text-gray-600 hover:bg-gray-100',
  [VoiceUIState.Connecting]: 'text-yellow-500 animate-pulse',
  [VoiceUIState.Listening]: 'text-green-500 bg-green-50',
  [VoiceUIState.Processing]: 'text-blue-500',
  [VoiceUIState.Speaking]: 'text-green-600 bg-green-50',
  [VoiceUIState.Error]: 'text-red-500 hover:text-red-600 hover:bg-red-50',
};

const stateLabels: Record<VoiceUIState, string> = {
  [VoiceUIState.Idle]: 'Start voice conversation',
  [VoiceUIState.Connecting]: 'Connecting to voice…',
  [VoiceUIState.Listening]: 'End voice conversation',
  [VoiceUIState.Processing]: 'Processing your request…',
  [VoiceUIState.Speaking]: 'Agent is speaking…',
  [VoiceUIState.Error]: 'Voice error — click to retry',
};

export const VoiceMicButton: React.FC<VoiceMicButtonProps> = ({
  voiceState,
  onToggle,
  disabled = false,
}) => {
  const isActive =
    voiceState !== VoiceUIState.Idle && voiceState !== VoiceUIState.Error;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      onToggle();
    }
    if (e.key === 'Escape' && isActive) {
      e.preventDefault();
      onToggle();
    }
  };

  return (
    <button
      type="button"
      onClick={onToggle}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label={stateLabels[voiceState]}
      aria-pressed={isActive}
      className={`
        p-2 rounded-full transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        disabled:opacity-50 disabled:cursor-not-allowed
        ${stateStyles[voiceState]}
      `}
    >
      {voiceState === VoiceUIState.Processing ? (
        <ArrowPathIcon className="w-6 h-6 animate-spin" />
      ) : (
        <MicrophoneIcon className="w-6 h-6" />
      )}
    </button>
  );
};
