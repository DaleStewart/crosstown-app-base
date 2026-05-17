/**
 * VoiceTranscript — renders voice conversation transcript entries.
 */

import React from 'react';
import { MicrophoneIcon, SpeakerWaveIcon } from '@heroicons/react/24/solid';
import type { VoiceMessage } from '../types/voice';

interface VoiceTranscriptProps {
  messages: VoiceMessage[];
}

export const VoiceTranscript: React.FC<VoiceTranscriptProps> = ({ messages }) => {
  if (messages.length === 0) return null;

  return (
    <div className="space-y-2 py-2" role="log" aria-label="Voice transcript">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`
              max-w-[80%] rounded-lg px-3 py-2 text-sm
              ${msg.role === 'user'
                ? 'bg-blue-100 text-blue-900'
                : 'bg-gray-100 text-gray-900'
              }
            `}
          >
            <div className="flex items-center gap-1 mb-1">
              {msg.role === 'user' ? (
                <MicrophoneIcon className="w-3 h-3 opacity-60" />
              ) : (
                <SpeakerWaveIcon className="w-3 h-3 opacity-60" />
              )}
              <span className="text-xs opacity-60">
                {msg.role === 'user' ? 'You (voice)' : 'Agent'}
              </span>
            </div>
            <p>{msg.content}</p>
            <time className="text-xs opacity-40 mt-1 block">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </time>
          </div>
        </div>
      ))}
    </div>
  );
};
