import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImageAnalyzer from '../components/ImageAnalyzer';
import * as api from '../services/api';

// Mock the API
vi.mock('../services/api', () => ({
  analyzeImage: vi.fn(),
}));

// Mock the useAudio hook
vi.mock('../hooks/useAudio', () => ({
  useAudio: () => ({
    playAudio: vi.fn().mockResolvedValue(null),
  }),
}));

// Mock navigator.mediaDevices
const mockGetUserMedia = vi.fn();
const mockStop = vi.fn();
const mockAddTrack = vi.fn();

beforeEach(() => {
  global.navigator.mediaDevices = {
    getUserMedia: mockGetUserMedia,
  };

  mockGetUserMedia.mockResolvedValue({
    getTracks: () => [{ stop: mockStop }],
  });

  HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
    drawImage: vi.fn(),
  }));

  HTMLCanvasElement.prototype.toBlob = vi.fn((callback) => {
    const blob = new Blob(['test'], { type: 'image/jpeg' });
    callback(blob);
  });

  // Mock HTMLVideoElement properties
  Object.defineProperty(HTMLMediaElement.prototype, 'videoWidth', {
    configurable: true,
    get: () => 1280,
  });

  Object.defineProperty(HTMLMediaElement.prototype, 'videoHeight', {
    configurable: true,
    get: () => 720,
  });

  HTMLMediaElement.prototype.play = vi.fn(() => Promise.resolve());
});

afterEach(() => {
  vi.clearAllMocks();
});

describe('ImageAnalyzer Component', () => {
  it('should render the analyze image section', () => {
    render(<ImageAnalyzer />);
    expect(screen.getByText('Analyze Surroundings')).toBeInTheDocument();
  });

  it('should show "Open Camera" button initially', () => {
    render(<ImageAnalyzer />);
    expect(screen.getByRole('button', { name: /open camera/i })).toBeInTheDocument();
  });

  it('should show "Upload Image" button initially', () => {
    render(<ImageAnalyzer />);
    const uploadLabel = screen.getByText('📁 Upload Image');
    expect(uploadLabel).toBeInTheDocument();
  });

  it('should open camera when clicking "Open Camera" button', async () => {
    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        video: { facingMode: 'environment' },
      });
    });
  });

  it('should show camera controls after opening camera', async () => {
    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });
  });

  it('should handle camera permission denied', async () => {
    const permissionError = new Error('Camera permission denied');
    permissionError.name = 'NotAllowedError';
    mockGetUserMedia.mockRejectedValueOnce(permissionError);

    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText(/camera permission denied/i)).toBeInTheDocument();
    });
  });

  it('should close camera when clicking cancel', async () => {
    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture/i })).toBeInTheDocument();
    });

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await userEvent.click(cancelButton);

    await waitFor(() => {
      expect(mockStop).toHaveBeenCalled();
    });
  });

  it('should call analyzeImage when capturing a photo', async () => {
    api.analyzeImage.mockResolvedValueOnce({
      description: 'A busy street intersection',
      danger_detected: false,
    });

    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture/i })).toBeInTheDocument();
    });

    const captureButton = screen.getByRole('button', { name: /capture/i });
    await userEvent.click(captureButton);

    await waitFor(() => {
      expect(api.analyzeImage).toHaveBeenCalled();
    });
  });

  it('should display analysis result', async () => {
    const mockResult = {
      description: 'A busy street with traffic lights',
      danger_detected: false,
    };

    api.analyzeImage.mockResolvedValueOnce(mockResult);

    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture/i })).toBeInTheDocument();
    });

    const captureButton = screen.getByRole('button', { name: /capture/i });
    await userEvent.click(captureButton);

    await waitFor(() => {
      expect(screen.getByText(mockResult.description)).toBeInTheDocument();
    });
  });

  it('should show danger alert when danger is detected', async () => {
    const mockResult = {
      description: 'A construction area with machinery',
      danger_detected: true,
      danger_type: 'construction_hazard',
    };

    api.analyzeImage.mockResolvedValueOnce(mockResult);

    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture/i })).toBeInTheDocument();
    });

    const captureButton = screen.getByRole('button', { name: /capture/i });
    await userEvent.click(captureButton);

    await waitFor(() => {
      expect(screen.getByText(/potential danger detected/i)).toBeInTheDocument();
      expect(screen.getByText(/construction_hazard/i)).toBeInTheDocument();
    });
  });

  it('should handle file upload', async () => {
    const mockFile = new File(['test'], 'photo.jpg', { type: 'image/jpeg' });
    const mockResult = {
      description: 'Uploaded image analysis',
      danger_detected: false,
    };

    api.analyzeImage.mockResolvedValueOnce(mockResult);

    render(<ImageAnalyzer />);
    const fileInput = screen.getByDisplayValue('');
    
    await userEvent.upload(fileInput, mockFile);

    await waitFor(() => {
      expect(api.analyzeImage).toHaveBeenCalled();
    });
  });

  it('should display error message on API failure', async () => {
    api.analyzeImage.mockRejectedValueOnce({
      response: {
        data: { detail: 'Image analysis failed' },
      },
    });

    render(<ImageAnalyzer />);
    const openButton = screen.getByRole('button', { name: /open camera/i });

    await userEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /capture/i })).toBeInTheDocument();
    });

    const captureButton = screen.getByRole('button', { name: /capture/i });
    await userEvent.click(captureButton);

    await waitFor(() => {
      expect(screen.getByText(/analysis error/i)).toBeInTheDocument();
    });
  });
});
