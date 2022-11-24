import pyaudio
import wave
import os
import time

is_active = 1


def recording():
    global is_active
    is_active = 1
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    root_dir = os.getcwd()
    input_dir = root_dir + r'\data\inputs'
    usr_input_dir = root_dir + r'\data\usr_inputs'
    output_dir = root_dir + r'\data\outputs'

    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []

    while is_active == 1:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    cur_time = 'usr_rec_' + time.strftime('%y%m%d-%H%M%S', time.localtime(time.time()))

    file_name = os.path.join(usr_input_dir, cur_time + ".wav")

    wf = wave.open(file_name, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
