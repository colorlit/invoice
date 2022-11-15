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
        # PyAudio Initialization
        self.pa_format = pyaudio.paFloat32
        self.pa_channels = 1
        self.pa_rate = 44100
        self.pa_chunk = 1024 * 2
        self.p = None
        self.pa_stream = None
        #self.pa_length = 512
        self.pa_num_samples = 0

        # Librosa Initialization
        self.lr_length = 512
        self.lr_array = None
        self.lr_chunk = 1024 * 2
        self.lr_sr = None # note to set 44100 if not initialized by load

        # Filesystem Initialization
        self.files_list = []
        self.root_dir = os.getcwd()
        self.input_dir = self.root_dir + r'\data\ffmpeg\outputs'

    def pa_stream_open(self):
        # Intergration WIP
        self.p = pyaudio.PyAudio()
        self.pa_stream = self.p.open(format=self.pa_format,
                                     channels=self.pa_channels,
                                     rate=self.pa_rate,
                                     input=True,
                                     output=False,
                                     stream_callback=self.callback,
                                     frames_per_buffer=self.pa_chunk)

    def import_file(self):
        self.files_list = os.listdir(self.input_dir)
        for path in os.listdir(self.input_dir):
            if os.path.isfile(os.path.join(self.input_dir, path)):
                self.files_list.append(path)
        #print(self.files_list)
        print("{0} of files added.".format(len(self.files_list)))

    def lr_load(self):
        # Test driver
        file_name = self.input_dir + r'\\' + self.files_list[0]
        self.lr_array, self.lr_sr = librosa.load(file_name)

    def testd_centroid(self):
        cent_obj = librosa.feature.spectral_centroid(y=self.lr_array, sr=self.lr_sr, n_fft=self.lr_chunk,
                                                     hop_length=self.lr_length)[0]
        print(cent_obj.shape)
        cent_frames = range(len(cent_obj))
        cent_t = librosa.frames_to_time(cent_frames, hop_length=self.lr_length)
        print(len(cent_t))

        plt.figure(figsize=(25,10))
        plt.plot(cent_t, cent_obj, color='r')
        plt.show()
        plt.savefig('testd_centroid.jpg')

    def start(self):
        pass

    def stop(self):
        print("Process Halted.")

    def callback(self, in_data, frame_count, time_info, flag):
        # WIP
        self.lr_array = np.frombuffer(in_data, dtype=np.float32)

    def mainloop(self):
        pass

audio = AudioSampler()
audio.import_file()
audio.lr_load()
audio.testd_centroid()
audio.stop()