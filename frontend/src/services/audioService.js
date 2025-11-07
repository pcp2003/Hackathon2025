export const audioService = {
  mediaRecorder: null,
  audioChunks: [],

  async startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      this.mediaRecorder.start();
      return { status: 'recording' };
    } catch (error) {
      throw new Error('Failed to start recording: ' + error.message);
    }
  },

  stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No recording in progress'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        this.audioChunks = [];
        
        // Stop all tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  },

  playAudio(audioBlob) {
    const url = URL.createObjectURL(audioBlob);
    const audio = new Audio(url);
    audio.play();
    return audio;
  },
};

export default audioService;
