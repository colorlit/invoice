import pyaudio
import wave
import os


def playing(file_name):
    chunk = 1024

    root_dir = os.getcwd()
    input_dir = root_dir + r'\data\inputs'
    usr_input_dir = root_dir + r'\data\usr_inputs'
    output_dir = root_dir + r'\data\outputs'

    wf = wave.open(file_name, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    )

    data = wf.readframes(chunk)
    while data != b'':
        stream.write(data)
        data = wf.readframes(chunk)

    wf.close()
    stream.close()
    p.terminate()
