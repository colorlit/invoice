import librosa
import librosa.display
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import wave
import soundfile as sf
import pyrubberband as pyrb
import time
from pathlib import Path
import threading
import os

class AudioSampler(object):
    def __init__(self):
        #PyAudio Initialization
        self.pa_format = pyaudio.paFloat32
        self.pa_channels = 1
        self.pa_rate = 44100
        self.pa_chunk = 1024 * 2
        self.p = None
        self.stream = None
        self.pa_length = 512
        self.pa_num_samples = 0

        #Filesystem Initialization
        self.files = []
        self.root_dir = os.getcwd()
        self.input_dir = self.root_dir + r'\data\ffmpeg\outputs'

    def import_file(self):
        self.files = os.listdir(self.input_dir)
        #print(self.files)
        print("{0} of files added.".format(len(self.files)))

    def start(self):
        pass

    def stop(self):
        print("Process Halted.")

    def mainloop(self):
        pass

audio = AudioSampler()
#audio.start()  # open the stream
#audio.mainloop()  # main operations with librosa
audio.import_file()
audio.stop()