import pyaudio
import wave
import os

class MicInputManager:
    def __init__(self, rate=16000, chunk=1024, channels=1, seconds=5):
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self.seconds = seconds
        self.p = pyaudio.PyAudio()

    def record_audio(self):
        print("Recording...")
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=self.channels,
                             rate=self.rate,
                             input=True,
                             frames_per_buffer=self.chunk)

        frames = []
        for _ in range(0, int(self.rate / self.chunk * self.seconds)):
            data = stream.read(self.chunk)
            frames.append(data)

        print("Recording finished.")
        stream.stop_stream()
        stream.close()

        return frames

    def save_audio(self, frames, filename="temp_input.wav"):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        return filename

    def get_input(self):
        frames = self.record_audio()
        filename = self.save_audio(frames)
        return filename

    def __del__(self):
        self.p.terminate()