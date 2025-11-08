import React, { useState, useRef } from 'react';
import { analyzeImage } from '../services/api';
import { useAudio } from '../hooks/useAudio';
import { API_CONFIG } from '../utils/constants';

export const ImageAnalyzer = () => {
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [cameraPermission, setCameraPermission] = useState(null);
  const [videoReady, setVideoReady] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const { playAudio } = useAudio();

  const openCamera = async () => {
    try {
      setError(null);
      setVideoReady(false);
      setIsCameraOpen(true); // Set this FIRST before getting the stream
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      streamRef.current = stream;
      
      // Small delay to ensure video element is mounted
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            console.log('Video loaded:', {
              videoWidth: videoRef.current.videoWidth,
              videoHeight: videoRef.current.videoHeight
            });
            setVideoReady(true);
          };
        }
      }, 100);
      
      setCameraPermission('granted');
    } catch (err) {
      setIsCameraOpen(false);
      const errorMessage = err.name === 'NotAllowedError' 
        ? 'Camera permission denied. Please allow camera access in your settings.'
        : 'Unable to access camera. Please check your device settings.';
      
      setError(errorMessage);
      setCameraPermission('denied');
      console.error('Camera error:', err);
    }
  };

  const closeCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsCameraOpen(false);
    setError(null);
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    try {
      const context = canvasRef.current.getContext('2d');
      const video = videoRef.current;

      // Try to get dimensions, but don't block if they're not available yet
      let width = video.videoWidth || 640;
      let height = video.videoHeight || 480;

      // Set canvas dimensions
      canvasRef.current.width = width;
      canvasRef.current.height = height;

      // Draw video frame to canvas
      context.drawImage(video, 0, 0, width, height);

      // Convert canvas to blob
      canvasRef.current.toBlob(async (blob) => {
        if (!blob) {
          setError('Failed to capture image');
          return;
        }

        // Close camera after capture
        closeCamera();

        // Send to backend
        await sendImageToBackend(blob);
      }, 'image/jpeg', 0.8);
    } catch (err) {
      setError('Error capturing image: ' + err.message);
      console.error('Capture error:', err);
    }
  };

  const sendImageToBackend = async (imageBlob) => {
    try {
      setIsAnalyzing(true);
      setError(null);

      const formData = new FormData();
      formData.append('image', imageBlob, 'photo.jpg');

      const result = await analyzeImage(formData);

      setAnalysisResult(result);

      // Convert description to speech using TTS endpoint
      if (result.description) {
        try {
          const ttsFormData = new FormData();
          ttsFormData.append('text', result.description);

          const response = await fetch(`${API_CONFIG.BASE_URL}/api/speak`, {
            method: 'POST',
            body: ttsFormData,
            headers: {
              'Accept': '*/*',
            },
            credentials: 'include',
            mode: 'cors',
          });

          if (response.ok) {
            const ttsResult = await response.json();
            if (ttsResult.audio) {
              // Build full audio URL
              const audioUrl = `${API_CONFIG.BASE_URL}${ttsResult.audio}`;
              await playAudio(audioUrl);
            }
          }
        } catch (ttsErr) {
          console.error('TTS error:', ttsErr);
          // Fallback: still show the description even if audio fails
        }
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to analyze image';
      setError('Analysis error: ' + errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsAnalyzing(true);
      setError(null);
      closeCamera();

      const formData = new FormData();
      formData.append('image', file);

      const result = await analyzeImage(formData);
      setAnalysisResult(result);

      // Convert description to speech using TTS endpoint
      if (result.description) {
        try {
          const ttsFormData = new FormData();
          ttsFormData.append('text', result.description);

          const response = await fetch(`${API_CONFIG.BASE_URL}/api/speak`, {
            method: 'POST',
            body: ttsFormData,
            headers: {
              'Accept': '*/*',
            },
            credentials: 'include',
            mode: 'cors',
          });

          if (response.ok) {
            const ttsResult = await response.json();
            if (ttsResult.audio) {
              // Build full audio URL
              const audioUrl = `${API_CONFIG.BASE_URL}${ttsResult.audio}`;
              await playAudio(audioUrl);
            }
          }
        } catch (ttsErr) {
          console.error('TTS error:', ttsErr);
          // Fallback: still show the description even if audio fails
        }
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to analyze image';
      setError('Analysis error: ' + errorMessage);
      console.error('File upload error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="image-analyzer">
      <div className="analyzer-section">
        <h4>Analyze Surroundings</h4>
        
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {/* Video element - ALWAYS rendered to keep ref stable */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="camera-feed"
          style={{
            display: isCameraOpen ? 'block' : 'none',
            width: '100%',
            height: 'auto',
            backgroundColor: '#000'
          }}
        />

        <canvas
          ref={canvasRef}
          style={{ display: 'none' }}
        />

        {isCameraOpen ? (
          <div className="camera-controls">
            <button
              onClick={capturePhoto}
              className="btn btn-primary"
              disabled={isAnalyzing || !videoReady}
              title={!videoReady ? 'Camera loading...' : 'Take photo'}
            >
              📷 Capture
            </button>
            <button
              onClick={closeCamera}
              className="btn btn-secondary"
              disabled={isAnalyzing}
            >
              ✕ Cancel
            </button>
          </div>
        ) : (
          <div className="analyzer-controls">
            <button
              onClick={openCamera}
              className="btn btn-primary"
              disabled={isAnalyzing}
            >
              📷 Open Camera
            </button>
            
            <label className="btn btn-secondary file-upload">
              📁 Upload Image
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                disabled={isAnalyzing}
              />
            </label>
          </div>
        )}

        {/* Analysis result */}
        {analysisResult && (
          <div className="analysis-result">
            <h5>Analysis</h5>
            <p className="description">
              {analysisResult.description}
            </p>
            {analysisResult.danger_detected && (
              <div className="alert alert-warning">
                ⚠️ Potential Danger Detected: {analysisResult.danger_type}
              </div>
            )}
          </div>
        )}

        {isAnalyzing && (
          <div className="loading-indicator">
            Analyzing image...
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageAnalyzer;
