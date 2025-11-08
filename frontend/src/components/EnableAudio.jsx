import React, { useState } from 'react';

const EnableAudio = () => {
  const [unlocked, setUnlocked] = useState(false);
  const [busy, setBusy] = useState(false);

  const unlock = async () => {
    if (unlocked || busy) return;
    setBusy(true);
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) {
        const ctx = new AC();
        if (ctx.state === 'suspended') {
          await ctx.resume();
        }

        // Play a tiny silent buffer to ensure output is unlocked
        try {
          const buffer = ctx.createBuffer(1, 1, 22050);
          const src = ctx.createBufferSource();
          src.buffer = buffer;
          src.connect(ctx.destination);
          src.start(0);
        } catch (err) {
          // ignore
          console.debug('silent-buffer failed', err);
        }
      } else {
        // Fallback: create an <audio> and attempt to play a short silent blob
        try {
          const silent = new Uint8Array([82,73,70,70,36,0,0,0,87,65,86,69,102,109,116,32,16,0,0,0,1,0,1,0,68,172,0,0,136,88,1,0,2,0,16,0,100,97,116,97,0,0,0,0]);
          const blob = new Blob([silent], { type: 'audio/wav' });
          const url = URL.createObjectURL(blob);
          const a = new Audio(url);
          a.play().catch(() => {});
          setTimeout(() => URL.revokeObjectURL(url), 2000);
        } catch (err) {
          // ignore
        }
      }

      // Mark unlocked for UI
      setUnlocked(true);
      window.__audio_unlocked = true;
      console.log('Audio unlocked');
    } catch (err) {
      console.warn('Failed to unlock audio:', err);
    } finally {
      setBusy(false);
    }
  };

  if (unlocked) return null;

  return (
    <button
      onClick={unlock}
      disabled={busy}
      style={{
        marginLeft: 12,
        padding: '6px 10px',
        borderRadius: 6,
        border: '1px solid #ccc',
        background: '#fff',
        cursor: 'pointer',
      }}
      aria-pressed={unlocked}
    >
      {busy ? 'Enabling audio…' : 'Enable sound'}
    </button>
  );
};

export default EnableAudio;
