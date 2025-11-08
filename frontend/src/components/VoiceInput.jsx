import React, { useState, useRef, useEffect } from 'react';
import { useAudio } from '../hooks';

export const VoiceInput = ({ onTranscribe, isLoading }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      // Attempt to unlock audio on this user gesture (Start Recording) so later playback is allowed on iOS
      try {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (AC) {
          const ctx = new AC();
          if (ctx.state === 'suspended') await ctx.resume();
          try {
            const buffer = ctx.createBuffer(1, 1, 22050);
            const src = ctx.createBufferSource();
            src.buffer = buffer;
            src.connect(ctx.destination);
            src.start(0);
          } catch (err) {
            console.debug('VoiceInput silent buffer failed', err);
          }
        } else {
          // Fallback: play a tiny silent audio blob
          try {
            const silent = new Uint8Array([82,73,70,70,36,0,0,0,87,65,86,69,102,109,116,32,16,0,0,0,1,0,1,0,68,172,0,0,136,88,1,0,2,0,16,0,100,97,116,97,0,0,0,0]);
            const blob = new Blob([silent], { type: 'audio/wav' });
            const url = URL.createObjectURL(blob);
            const a = new Audio(url);
            a.play().catch(() => {});
            setTimeout(() => URL.revokeObjectURL(url), 2000);
          } catch (err) {
            console.debug('VoiceInput silent fallback failed', err);
          }
        }
        window.__audio_unlocked = true;
      } catch (err) {
        console.debug('Audio unlock attempt failed in VoiceInput', err);
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        (async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });

          // Try to unlock audio again on this user gesture boundary (stop)
          try {
            const AC = window.AudioContext || window.webkitAudioContext;
            if (AC) {
              const ctx = new AC();
              if (ctx.state === 'suspended') await ctx.resume();
              try {
                // play a slightly longer silent buffer twice to increase chance of unlocking on iOS
                const buffer = ctx.createBuffer(1, 2205, 22050); // 0.1s
                const src = ctx.createBufferSource();
                src.buffer = buffer;
                src.connect(ctx.destination);
                src.start(0);
                // play a second time shortly after
                setTimeout(() => {
                  try {
                    const src2 = ctx.createBufferSource();
                    src2.buffer = buffer;
                    src2.connect(ctx.destination);
                    src2.start(0);
                  } catch (e) {
                    console.debug('second silent play failed', e);
                  }
                }, 60);
              } catch (err) {
                console.debug('VoiceInput stop silent buffer failed', err);
              }
            } else {
              try {
                // Fallback: play a slightly larger silent WAV blob twice
                const silent = new Uint8Array([82,73,70,70,100,0,0,0,87,65,86,69,102,109,116,32,16,0,0,0,1,0,1,0,68,172,0,0,136,88,1,0,2,0,16,0,100,97,116,97,0,0,0,0]);
                const blob = new Blob([silent], { type: 'audio/wav' });
                const url = URL.createObjectURL(blob);
                const a = new Audio(url);
                a.play().catch(() => {});
                setTimeout(() => {
                  const a2 = new Audio(url);
                  a2.play().catch(() => {});
                  setTimeout(() => URL.revokeObjectURL(url), 2000);
                }, 80);
              } catch (err) {
                console.debug('VoiceInput stop fallback failed', err);
              }
            }
            window.__audio_unlocked = true;
          } catch (err) {
            console.debug('Audio unlock attempt failed on stop', err);
          }

          // Small delay to ensure the resume/unlock takes effect before the app attempts playback
          await new Promise((resolve) => setTimeout(resolve, 220));

          onTranscribe(audioBlob);
        })();
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div className="voice-input">
      <button
        className={`record-button ${isRecording ? 'recording' : ''} ${isLoading ? 'disabled' : ''}`}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isLoading}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
    </div>
  );
};

export default VoiceInput;
