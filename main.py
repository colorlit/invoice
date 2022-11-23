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
        self.push_btn_record.clicked.connect(lambda: self.btn_record())
        self.push_btn_select.clicked.connect(lambda: self.btn_select())
        self.push_btn_process.clicked.connect(lambda: self.btn_process())
        self.push_btn_convert.clicked.connect(lambda: self.btn_convert())
        self.push_btn_init.clicked.connect(lambda: self.btn_init())
        self.push_btn_help.clicked.connect(lambda: self.btn_help())
        # does anybody knows why these guys need lambda? plz elaborate

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

    def btn_record(self):
        sub_thread = threading.Thread(target=AudioRecorder.recording)
        sub_thread.start()
        print('main thread')
        #AudioRecorder.recording()

    def btn_select(self):
        print('SELECTING')

    def btn_convert(self):
        ffmpeg_conv.format_convert()

    def btn_process(self):
        SampleProcessor.audio_process()

    def btn_init(self):
        print('INIT')
        audio_rec_toggle()
        #MicStream.is_active = False

    def btn_help(self):
        print('HELP')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    myWindow.show_plt()
    app.exec_()
