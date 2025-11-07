import React, { useState, useRef, useEffect } from 'react';
import { useAudio } from '../hooks';

export const VoiceInput = ({ onTranscribe, isLoading }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        onTranscribe(audioBlob);
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
        {isRecording ? '🔴 Stop Recording' : '🎤 Start Recording'}
      </button>
    </div>
  );
};

export default VoiceInput;
