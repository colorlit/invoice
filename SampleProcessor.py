import librosa
import librosa.display
import numpy as np
import soundfile as sf
import pyrubberband as pyrb
import os
import time
import matplotlib.pyplot as plt

import AudioPlayer


def phase_finder(y, sr, sa_avg_cent):
    # evaluate diffs between the sample and user input
    # Calculate n_steps
    y_orig_ts = pyrb.time_stretch(y, sr=sr, rate=1)
    y_orig_ps = pyrb.pitch_shift(y_orig_ts, sr=sr, n_steps=0)
    y_eval_ts = pyrb.time_stretch(y, sr=sr, rate=1)
    y_eval_ps = pyrb.pitch_shift(y_eval_ts, sr=sr, n_steps=0)
    steps_inc = 3.0
    cur_steps = 0.0
    is_asc_mode = False
    is_desc_mode = False
    is_zero_crossed = False

    cent_eval = np.average(librosa.feature.spectral_centroid(y=y_eval_ps, sr=sr))
    if sa_avg_cent > cent_eval:
        is_asc_mode = True
    elif sa_avg_cent < cent_eval:
        is_desc_mode = True

    # change the iter count to higher value if the program cannot follow
    for step in range(15):
        # we need a neater evaluation value than this
        #cent_eval = np.average(librosa.feature.spectral_centroid(y=y_eval_ps, sr=sr))
        cent_array = librosa.feature.spectral_centroid(y=y_eval_ps, sr=sr)
        cent_median = np.median(cent_array)
        cent_array = cent_array - (cent_median/3)
        cent_bias = cent_array[cent_array >= 0]
        cent_bias = cent_bias + (cent_median/3)
        cent_eval = np.average(cent_bias)
        print('| {0} STEP | INCREMENT LVL:{1}, CURRENT TONE:{2} | TARGET CENT:{3}, CURRENT CENT:{4} |'.format(step, steps_inc, cur_steps, sa_avg_cent, cent_eval))

        if is_asc_mode is True:
            if sa_avg_cent > cent_eval:
                cur_steps += steps_inc
                y_eval_ps = pyrb.pitch_shift(y_orig_ps, sr=sr, n_steps=cur_steps)
            elif sa_avg_cent < cent_eval:
                is_zero_crossed = True

        elif is_desc_mode is True:
            if sa_avg_cent < cent_eval:
                cur_steps -= steps_inc
                y_eval_ps = pyrb.pitch_shift(y_orig_ps, sr=sr, n_steps=cur_steps)
            elif sa_avg_cent > cent_eval:
                is_zero_crossed = True

        if is_zero_crossed is True:
            is_zero_crossed = False
            y_eval_ps = pyrb.pitch_shift(y_orig_ps, sr=sr, n_steps=cur_steps)

            if is_asc_mode is True:
                cur_steps -= steps_inc
            else:
                cur_steps += steps_inc

            if steps_inc > 1.0:
                steps_inc -= 1
            elif steps_inc > 0.0:
                steps_inc /= 2

        #print('[SRC|cent_avg:{0}][EVA|n_steps:{1}|cent_avg:{2}]'.format(sa_avg_cent, cur_steps, cent_eval))

    return cur_steps


def audio_process(track_id):
    # file management
    files_list = []
    file_name = []
    usr_files_list = []
    usr_file_name = []
    root_dir = os.getcwd()
    input_dir = root_dir + r'\data\inputs'
    usr_input_dir = root_dir + r'\data\usr_inputs'
    output_dir = root_dir + r'\data\outputs'

    is_batch_mode = False

    if track_id == -72:
        is_batch_mode = True

    # import sample files | call file_name[index]
    for path in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, path)):
            files_list.append(path)

    for filename in files_list:
        # Extension check
        if os.path.splitext(os.path.join(input_dir, filename))[-1] == '.wav':
            file_name.append(os.path.join(input_dir, filename))

    if is_batch_mode is False:
        file_name_store = file_name[track_id]
        del file_name
        file_name = []
        file_name.append(file_name_store)

    # import user input files | call usr_file_name[index]
    for path in os.listdir(usr_input_dir):
        if os.path.isfile(os.path.join(usr_input_dir, path)):
            usr_files_list.append(path)

    for filename in usr_files_list:
        # Extension check
        if os.path.splitext(os.path.join(usr_input_dir, filename))[-1] == '.wav':
            usr_file_name.append(os.path.join(usr_input_dir, filename))

    if is_batch_mode is False:
        usr_file_name_store = usr_file_name[track_id]
        del usr_file_name
        usr_file_name = []
        usr_file_name.append(usr_file_name_store)

    # sample preprocessing
    sa_avg_cent = None
    sa_avg_cent_list = []
    for sa_capture_counts in range(len(file_name)):
        y_sa, sa_sr = librosa.load(file_name[sa_capture_counts])
        y_sa_ts = pyrb.time_stretch(y_sa, sr=sa_sr, rate=1)
        y_sa_ps = pyrb.pitch_shift(y_sa_ts, sr=sa_sr, n_steps=0)
        sa_avg_cent = np.average(librosa.feature.spectral_centroid(y=y_sa_ps, sr=sa_sr))
        sa_avg_cent_list.append(sa_avg_cent)

    sa_avg_cent = np.average(sa_avg_cent_list)
    print('{0} files has loaded and sampled with centroid {1} as target'.format(len(file_name),sa_avg_cent))

    # user sample handling
    ps_steps_list = []
    for usr_capture_counts in range(len(usr_file_name)):
        y_usr, sr_usr = librosa.load(usr_file_name[usr_capture_counts])
        ps_step = phase_finder(y_usr, sr_usr, sa_avg_cent)
        ps_steps_list.append(ps_step)

    ps_step = np.average(ps_steps_list)

    # audio processing
    for file_idx in range(len(usr_file_name)):
        y_ap, sr_ap = librosa.load(usr_file_name[file_idx])
        y_proc_ts = pyrb.time_stretch(y_ap, sr=sr_ap, rate=1)
        y_proc = pyrb.pitch_shift(y_proc_ts, sr=sr_ap, n_steps=ps_step)
        output_file = os.path.basename(usr_file_name[file_idx])
        sf.write(os.path.join(output_dir, output_file), y_proc, sr_ap, subtype='PCM_24')

    if is_batch_mode is False:
        # address processing delay...
        # but it seems that the main thread does not meet any of conflict due to its blocking exec.
        time.sleep(0.7)
        playback_path = os.path.join(output_dir, output_file)
        AudioPlayer.playing(playback_path)


# driver for testing purpose
def audio_process_alt(track_id):
    # file management
    files_list = []
    file_name = []
    usr_files_list = []
    usr_file_name = []
    root_dir = os.getcwd()
    input_dir = root_dir + r'\data\inputs'
    usr_input_dir = root_dir + r'\data\usr_inputs'
    output_dir = root_dir + r'\data\outputs'
    image_dir = root_dir + r'\data\images'

    is_batch_mode = False

    if track_id == -72:
        is_batch_mode = True

    # import sample files | call file_name[index]
    for path in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, path)):
            files_list.append(path)

    for filename in files_list:
        # Extension check
        if os.path.splitext(os.path.join(input_dir, filename))[-1] == '.wav':
            file_name.append(os.path.join(input_dir, filename))

    if is_batch_mode is False:
        file_name_store = file_name[track_id]
        del file_name
        file_name = []
        file_name.append(file_name_store)

    # import user input files | call usr_file_name[index]
    for path in os.listdir(usr_input_dir):
        if os.path.isfile(os.path.join(usr_input_dir, path)):
            usr_files_list.append(path)

    for filename in usr_files_list:
        # Extension check
        if os.path.splitext(os.path.join(usr_input_dir, filename))[-1] == '.wav':
            usr_file_name.append(os.path.join(usr_input_dir, filename))

    if is_batch_mode is False:
        usr_file_name_store = usr_file_name[track_id]
        del usr_file_name
        usr_file_name = []
        usr_file_name.append(usr_file_name_store)

    # sample preprocessing
    sa_avg_cent = None
    sa_avg_cent_list = []
    for sa_capture_counts in range(len(file_name)):
        y_sa, sa_sr = librosa.load(file_name[sa_capture_counts])
        y_sa_ts = pyrb.time_stretch(y_sa, sr=sa_sr, rate=1)
        y_sa_ps = pyrb.pitch_shift(y_sa_ts, sr=sa_sr, n_steps=0)
        # new implementation for evaluation
        #sa_avg_cent = np.average(librosa.feature.spectral_centroid(y=y_sa_ps, sr=sa_sr))
        cent_array = librosa.feature.spectral_centroid(y=y_sa_ps, sr=sa_sr)
        cent_median = np.median(cent_array)
        cent_array = cent_array - (cent_median/3)
        cent_bias = cent_array[cent_array >= 0]
        cent_bias = cent_bias + (cent_median/3)
        sa_avg_cent = np.average(cent_bias)
        # end of new thing
        sa_avg_cent_list.append(sa_avg_cent)
        s = librosa.feature.melspectrogram(y=y_sa, sr=sa_sr, n_mels=128, fmax=8192)
        s_db = librosa.power_to_db(s, ref=np.max)
        fig, ax = plt.subplots()
        img = librosa.display.specshow(s_db, x_axis='time', y_axis='mel',
                                       sr=sa_sr, fmax=8192, ax=ax)
        fig.savefig(os.path.join(image_dir, 'input' + str(sa_capture_counts) + '.png'))

    sa_avg_cent = np.average(sa_avg_cent_list)
    print('{0} files has loaded and sampled with centroid {1} as target'.format(len(file_name),sa_avg_cent))

    # user sample handling
    ps_steps_list = []
    for usr_capture_counts in range(len(usr_file_name)):
        y_usr, sr_usr = librosa.load(usr_file_name[usr_capture_counts])
        s = librosa.feature.melspectrogram(y=y_usr, sr=sr_usr, n_mels=128, fmax=8192)
        s_db = librosa.power_to_db(s, ref=np.max)
        fig, ax = plt.subplots()
        img = librosa.display.specshow(s_db, x_axis='time', y_axis='mel',
                                       sr=sr_usr, fmax=8192, ax=ax)
        fig.savefig(os.path.join(image_dir, 'uinput' + str(usr_capture_counts) + '.png'))
        ps_step = phase_finder(y_usr, sr_usr, sa_avg_cent)
        ps_steps_list.append(ps_step)

    ps_step = np.average(ps_steps_list)

    # audio processing
    for file_idx in range(len(usr_file_name)):
        y_ap, sr_ap = librosa.load(usr_file_name[file_idx])
        y_proc_ts = pyrb.time_stretch(y_ap, sr=sr_ap, rate=1)
        y_proc = pyrb.pitch_shift(y_proc_ts, sr=sr_ap, n_steps=ps_step)
        output_file = os.path.basename(usr_file_name[file_idx])
        sf.write(os.path.join(output_dir, output_file), y_proc, sr_ap, subtype='PCM_24')
        s = librosa.feature.melspectrogram(y=y_proc, sr=sr_ap, n_mels=128, fmax=8192)
        s_db = librosa.power_to_db(s, ref=np.max)
        fig, ax = plt.subplots()
        img = librosa.display.specshow(s_db, x_axis='time', y_axis='mel',
                                       sr=sr_ap, fmax=8192, ax=ax)
        fig.savefig(os.path.join(image_dir, 'output' + str(file_idx) + '.png'))

    if is_batch_mode is False:
        # address processing delay...
        # but it seems that the main thread does not meet any of conflict due to its blocking exec.
        time.sleep(0.7)
        playback_path = os.path.join(output_dir, output_file)
        AudioPlayer.playing(playback_path)
