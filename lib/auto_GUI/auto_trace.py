import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase
from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ
from lib.auto_GUI.auto_DAT import AutoDAT


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

    def get_file_count(self):
        return self.file_count

    def populate_file_list(self, keyword=None):
        self.file_list = []
        for f in os.listdir(self.data_dir):
            if f.endswith('.dat') and 'ROI' in f and (keyword is None or keyword in f):
                self.file_list.append(f)

    def export_trace_files(self):
        """ Load file into a prepared PhotoZ """
        ad = AutoDAT(datadir=self.data_dir)
        ad.get_zda_file_list()
        slice, loc, rec = ad.get_initial_keys()
        ad.return_to_lowest_recording()

        self.aPhz.select_PhotoZ()
        if len(self.file_list) < 1:
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

            # Go to next file
            slice, loc, rec, done = ad.go_to_next_file(slice, loc, rec)
            if not done:
                print("This should be the last file: Slice",
                      slice, "\t Loc", loc, "\t Rec", rec)
                break
            else:
                print("Selected: Slice", slice, "\t Loc", loc, "\t Rec", rec)

            print('\tWrote file:', dst_file)
            self.file_count += 1
        print(self.file_count, "traces exported.")

    def export_persistent_trace_files(self):
        """ Load file into a prepared PhotoZ """
        ad = AutoDAT(datadir=self.data_dir)
        ad.get_zda_file_list()
        slice, loc, rec = ad.get_initial_keys()
        ad.return_to_lowest_recording()
        continuing = True

        self.aPhz.select_PhotoZ()
        if len(self.file_list) < 1:
            self.populate_file_list(keyword='persistent')
            print(self.file_list)

        persistent_dict = {}

        for file in self.file_list:
            if 'traces' not in file:
                print(file)

                slic_loc_id = file.split('tent')[1]
                slic_loc_id = slic_loc_id[:-4]
                persist_slic, persist_loc = [int(x) for x in slic_loc_id.split("-")]
                print(persist_slic, persist_loc)

                if persist_slic not in persistent_dict:
                    persistent_dict[persist_slic] = {}
                if persist_loc not in persistent_dict[persist_slic]:
                    persistent_dict[persist_slic][persist_loc] = {}
                persistent_dict[persist_slic][persist_loc]['src'] = self.data_dir + file
                dst = self.data_dir + "traces_" + file
                persistent_dict[persist_slic][persist_loc]['dst'] = dst[:-4]

        persist_slic = 1
        persist_loc = 1
        while persist_slic not in persistent_dict:
            persist_slic += 1
        self.aPhz.select_roi_tab()
        try:
            self.aPhz.open_roi_file(persistent_dict[persist_slic][persist_loc]['src'])
        except Exception as e:
            pass

        while continuing:

            if persist_slic == slice and persist_loc == loc:

                # save the traces as tsv
                self.aPhz.select_save_load_tab()
                self.aPhz.save_current_traces(persistent_dict[persist_slic][persist_loc]['dst'] + "-" + str(rec) + '.dat')

                # Go to next file
                slice, loc, rec, continuing = ad.go_to_next_file(slice, loc, rec)
                print("\tSelected recording: Slice", slice, "\t Loc", loc, "\t Rec", rec)
                if not continuing:
                    break

            if persist_slic < slice or persist_loc < loc:
                # time to open the next persist slice/loc.
                persist_slic = slice
                persist_loc = loc
                while persist_slic not in persistent_dict:
                    persist_loc = 1
                    persist_slic += 1
                self.aPhz.select_roi_tab()
                self.aPhz.open_roi_file(persistent_dict[persist_slic][persist_loc]['src'])
                print("Selected persistent file: Slice", persist_slic, "\t Loc", persist_loc)

            if persist_slic > slice or persist_loc > loc:
                # need to fast forward PhotoZ to match this persistent file.
                while persist_slic > slice or persist_loc > loc:
                    slice, loc, rec, continuing = ad.go_to_next_file(slice, loc, rec)
                    if not continuing:
                        break
                    self.aPhz.move_cursor_off()
                    print("\tSelected recording: Slice", slice, "\t Loc", loc, "\t Rec", rec)
                    time.sleep(3)

            print('\tWrote file:', persistent_dict[persist_slic][persist_loc]['dst'] + "-" + str(rec) + '.dat')
            print("Not Done:", continuing)
            self.file_count += 1
        print(self.file_count, "traces exported.")