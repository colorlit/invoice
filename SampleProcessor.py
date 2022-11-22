import librosa
import librosa.display
import numpy as np
import soundfile as sf
import pyrubberband as pyrb
import os


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
        cent_eval = np.average(librosa.feature.spectral_centroid(y=y_eval_ps, sr=sr))
        print('{0} step | is_zero_crossing:{1}, steps_inc:{2}, cur_steps:{3}, cent_target:{4}, cent_eval:{5}'.format(step, is_zero_crossed, steps_inc, cur_steps, sa_avg_cent, cent_eval))

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

        print('[SRC|n_steps:{0}|cent_avg:{1}][EVA|n_steps:{2}|cent_avg:{3}]'.format('unknown', sa_avg_cent, cur_steps,
                                                                                    cent_eval))

    return cur_steps


def audio_process():
    # file management
    files_list = []
    file_name = []
    usr_files_list = []
    usr_file_name = []
    root_dir = os.getcwd()
    input_dir = root_dir + r'\data\inputs'
    usr_input_dir = root_dir + r'\data\usr_inputs'
    output_dir = root_dir + r'\data\outputs'

    # import sample files | call file_name[index]
    for path in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, path)):
            files_list.append(path)

    for filename in files_list:
        # Extension check
        if os.path.splitext(os.path.join(input_dir, filename))[-1] == '.wav':
            file_name.append(os.path.join(input_dir, filename))

    # import user input files | call usr_file_name[index]
    for path in os.listdir(usr_input_dir):
        if os.path.isfile(os.path.join(usr_input_dir, path)):
            usr_files_list.append(path)

    for filename in usr_files_list:
        # Extension check
        if os.path.splitext(os.path.join(usr_input_dir, filename))[-1] == '.wav':
            usr_file_name.append(os.path.join(usr_input_dir, filename))

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


#audio_process()