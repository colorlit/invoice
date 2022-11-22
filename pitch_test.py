import librosa
import librosa.display
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import wave
import soundfile as sf
import pyrubberband as pyrb
import os
import scipy


files_list = []
root_dir = os.getcwd()
input_dir = root_dir + r'\SAMPLES\inputs'
output_dir = root_dir + r'\SAMPLES\outputs'

files_list = os.listdir(input_dir)
for path in os.listdir(input_dir):
    if os.path.isfile(os.path.join(input_dir, path)):
        files_list.append(path)

file_name = input_dir + r'\\' + files_list[0]

# Preprocessing
y_ax, sr = librosa.load(file_name)
y_pyrb_ts = pyrb.time_stretch(y_ax, sr=sr, rate=1)
y_pyrb_ps = pyrb.pitch_shift(y_pyrb_ts, sr=sr, n_steps=0)

src_avg_orig = np.average(y_ax)
src_avg = np.average(y_pyrb_ps)

src_cent_orig = librosa.feature.spectral_contrast(y=y_ax, sr=sr)
src_cent = librosa.feature.spectral_centroid(y=y_pyrb_ps, sr=sr)

src_cent_avg_orig = np.average(src_cent_orig)
src_cent_avg = np.average(src_cent)

#np.savetxt('output_cent_src.txt', src_cent)
#np.savetxt('output_cent_res.txt', res_cent)

#print('{0} is source avg and {1} is results avg'.format(src_avg_orig, src_avg))
#print('{0} is source centroid avg and {1} is result centroid avg'.format(src_cent_avg_orig, src_cent_avg))

# find n_steps required
#for num_trials in range(5):

# Pitch shift

sample_n_steps = 6.5

y_sample_ts = pyrb.time_stretch(y_ax, sr=sr, rate=1)
y_sample_ps = pyrb.pitch_shift(y_pyrb_ts, sr=sr, n_steps=sample_n_steps)
cent_target = np.average(librosa.feature.spectral_centroid(y=y_sample_ps, sr=sr))


# Calculate n_steps
y_eval_ts = pyrb.time_stretch(y_ax, sr=sr, rate=1)
y_eval_ps = pyrb.pitch_shift(y_pyrb_ts, sr=sr, n_steps=0)
steps_inc = 3.0
cur_steps = 0.0
is_asc_mode = False
is_desc_mode = False
is_zero_crossed = False

cent_eval = np.average(librosa.feature.spectral_centroid(y=y_eval_ps, sr=sr))
if cent_target > cent_eval:
    is_asc_mode = True
elif cent_target < cent_eval:
    is_desc_mode = True

for step in range(13):
    cent_eval = np.average(librosa.feature.spectral_centroid(y=y_eval_ps, sr=sr))
    print('{0} step | is_zero_crossing:{1}, steps_inc:{2}, cur_steps:{3}, cent_target:{4}, cent_eval:{5}'.format(step, is_zero_crossed, steps_inc, cur_steps, cent_target, cent_eval))

    if is_asc_mode is True:
        if cent_target > cent_eval:
            cur_steps += steps_inc
            y_eval_ps = pyrb.pitch_shift(y_pyrb_ts, sr=sr, n_steps=cur_steps)
        elif cent_target < cent_eval:
            is_zero_crossed = True

    elif is_desc_mode is True:
        if cent_target < cent_eval:
            cur_steps -= steps_inc
            y_eval_ps = pyrb.pitch_shift(y_pyrb_ts, sr=sr, n_steps=cur_steps)
        elif cent_target > cent_eval:
            is_zero_crossed = True

    if is_zero_crossed is True:
        is_zero_crossed = False
        y_eval_ps = pyrb.pitch_shift(y_pyrb_ts, sr=sr, n_steps=cur_steps)
        
        if is_asc_mode is True:
            cur_steps -= steps_inc
        else:
            cur_steps += steps_inc

        if steps_inc > 1.0:
            steps_inc -= 1
        elif steps_inc > 0.0:
            steps_inc /= 2


print('[SRC|n_steps:{0}|cent_avg:{1}][EVA|n_steps:{2}|cent_avg:{3}]'.format(sample_n_steps, cent_target, cur_steps, cent_eval))

# 4. Librosa output thru SF
#sf.write("Testd2.wav", y_pyrb_ps, sr, subtype='PCM_24')