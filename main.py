import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
import librosa
import librosa.display
import numpy as np
import os
import threading

import AudioRecorder
import SampleProcessor
import ffmpeg_conv

form_class = uic.loadUiType("./invoice.ui")[0]


def audio_rec_toggle():
    AudioRecorder.is_active = 0


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('INVOICE')
        self.fig_tgt = plt.Figure()
        self.canvas_tgt = FigureCanvas(self.fig_tgt)
        self.layout_target_voice.addWidget(self.canvas_tgt)
        self.fig_usr = plt.Figure()
        self.canvas_usr = FigureCanvas(self.fig_usr)
        self.layout_user_voice.addWidget(self.canvas_usr)
        self.y_tgt = None
        self.y_usr = None
        self.sr_tgt = None
        self.sr_usr = None
        self.plot_tgt = None
        self.plot_usr = None
        self.track_id = None
        self.is_tgt_sel = None
        self.is_usr_sel = None

        # file management
        self.files_list = []
        self.file_name = []
        self.usr_files_list = []
        self.usr_file_name = []
        self.root_dir = os.getcwd()
        self.input_dir = self.root_dir + r'\data\inputs'
        self.usr_input_dir = self.root_dir + r'\data\usr_inputs'
        self.output_dir = self.root_dir + r'\data\outputs'

        # button click event handlers
        # sidebar ui
        self.push_btn_convert.clicked.connect(lambda: self.btn_convert())
        self.push_btn_process.clicked.connect(lambda: self.btn_process())
        self.push_btn_batch.clicked.connect(lambda: self.btn_batch())
        self.push_btn_load.clicked.connect(lambda: self.btn_load())
        self.push_btn_record.clicked.connect(lambda: self.btn_record())
        self.push_btn_stop.clicked.connect(lambda: self.btn_stop())
        # playback ui
        self.push_btn_tgt_play.clicked.connect(lambda: self.btn_tgt_play())
        self.push_btn_usr_play.clicked.connect(lambda: self.btn_usr_play())
        # track controls
        self.push_btn_tgt_sel.clicked.connect(lambda: self.btn_tgt_sel())
        self.push_btn_usr_sel.clicked.connect(lambda: self.btn_usr_sel())
        self.line_edit_id_sel.returnPressed.connect(lambda: self.ln_edit_id_sel())
        # got understood why these lines need lambda, no needs of () closing in the call of event func

    def open_files(self):
        # import sample files | call file_name[index]
        for path in os.listdir(self.input_dir):
            if os.path.isfile(os.path.join(self.input_dir, path)):
                self.files_list.append(path)

        for filename in self.files_list:
            # Extension check
            if os.path.splitext(os.path.join(self.input_dir, filename))[-1] == '.wav':
                self.file_name.append(os.path.join(self.input_dir, filename))

        # import user input files | call usr_file_name[index]
        for path in os.listdir(self.usr_input_dir):
            if os.path.isfile(os.path.join(self.usr_input_dir, path)):
                self.usr_files_list.append(path)

        for filename in self.usr_files_list:
            # Extension check
            if os.path.splitext(os.path.join(self.usr_input_dir, filename))[-1] == '.wav':
                self.usr_file_name.append(os.path.join(self.usr_input_dir, filename))

    def show_plt(self):
        self.open_files()
        self.y_tgt, self.sr_tgt = librosa.load(self.file_name[0])
        self.y_usr, self.sr_usr = librosa.load(self.usr_file_name[0])

        plt.axis('off')

        self.plot_tgt = self.fig_tgt.add_subplot()
        self.plot_tgt.plot()
        #self.plot_tgt.get_legend().remove()
        librosa.display.waveshow(self.y_tgt, sr=self.sr_tgt, ax=self.plot_tgt)
        self.canvas_tgt.draw()

        self.plot_usr = self.fig_usr.add_subplot()
        self.plot_usr.plot()
        #self.plot_usr.get_legend().remove()
        librosa.display.waveshow(self.y_usr, sr=self.sr_usr, ax=self.plot_usr)
        self.canvas_usr.draw()

    # sidebar ui
    def btn_record(self):
        sub_thread = threading.Thread(target=AudioRecorder.recording)
        sub_thread.start()
        #AudioRecorder.recording()

    def btn_stop(self):
        audio_rec_toggle()

    def btn_load(self):
        print('LOAD FILES')

    def btn_convert(self):
        ffmpeg_conv.format_convert()

    def btn_process(self):
        SampleProcessor.audio_process()

    def btn_batch(self):
        print('BATCH PROCESS')

    # playback ui
    def btn_tgt_play(self):
        pass

    def btn_usr_play(self):
        pass

    # track control ui
    def btn_tgt_sel(self):
        self.is_tgt_sel = True
        self.is_usr_sel = False

    def btn_usr_sel(self):
        self.is_usr_sel = True
        self.is_tgt_sel = False

    def ln_edit_id_sel(self):
        # how to 'put' text
        # self.<objname>.setText('string')
        # how to 'read' text
        # return = self.<objname>.text()
        self.track_id = self.line_edit_id_sel.text()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    myWindow.show_plt()
    app.exec_()
