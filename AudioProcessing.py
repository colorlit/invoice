import librosa
import librosa.display
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import wave
import soundfile as sf
import pyrubberband as pyrb

# 1. pyaudio
CHUNK = 1024
FORMAT = pyaudio.paInt24
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("RECORD START")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("RECORD END")

stream.stop_stream()
stream.close()
p.terminate()

# SAVE to wav
WAVE_OUTPUT_FILENAME = "output.wav"
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# 2. librosa
LENGTH = 512
wavfilename = "output.wav"
# wavobj, sr = librosa.load(wavfilename)

# 3. Librosa / Rubberband Pitch_shift (upward)
y_ax, sr = librosa.load(wavfilename)
y_pyrb_ps = pyrb.pitch_shift(y_ax, sr=sr, n_steps=10)

# 4. Librosa output thru SF
sf.write('output2.wav', y_pyrb_ps, sr, subtype='PCM_24')