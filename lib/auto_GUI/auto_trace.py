import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase
from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ


class AutoTrace(AutoGUIBase):
    """ Loads ROIs into PhotoZ and automatically exports each ROI's full trace """

    def __init__(self, datadir='.', processing_sleep_time=2, file_prefix=""):
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        if not datadir.endswith("/"):
            datadir += "/"
        self.data_dir = datadir
        self.file_list = []
        self.processing_sleep_time = processing_sleep_time
        self.file_prefix = file_prefix
        self.aPhz = AutoPhotoZ(data_dir=self.data_dir)
        self.file_count = 0
        self.populate_file_list()

    def get_file_count(self):
        return self.file_count

    def populate_file_list(self):
        self.file_list = []
        for f in os.listdir(self.data_dir):
            if f.endswith('.dat') and 'ROI' in f:
                self.file_list.append(f)

    def export_trace_files(self):
        """ Load file into a prepared PhotoZ """
        self.aPhz.select_PhotoZ()
        if len(self.file_list) < 0:
            self.populate_file_list()
        for file in self.file_list:
            print(file)
            src_file = self.data_dir + file
            dst_file = self.data_dir + "traces_" + file

            self.aPhz.select_roi_tab()
            self.aPhz.open_roi_file(src_file)

            # save the traces as tsv
            self.aPhz.select_save_load_tab()
            self.aPhz.save_current_traces(dst_file)
            print('\tWrote file:', dst_file)
            self.file_count += 1
        print(self.file_count, "traces exported.")


