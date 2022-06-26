import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase
from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ


class AutoDAT(AutoGUIBase):
    """ Automatically save background image data for many ZDA files """

    def __init__(self, datadir='.', processing_sleep_time=2, file_prefix=""):
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        if not datadir.endswith("/"):
            datadir += "/"
        self.data_dir = datadir
        self.record_tree = {}
        self.processing_sleep_time = processing_sleep_time
        self.file_prefix = file_prefix
        self.aPhz = AutoPhotoZ(data_dir=self.data_dir)

    def get_target_dir(self):
        dir = self.data_dir
        if not dir.endswith("/"):
            dir += "/"
        dir + "dat_output/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def return_to_lowest_recording(self):
        """ Select the lowest slice/loc/rec of the current directory """
        slic, loc, rec = self.get_initial_keys()
        filename = self.data_dir + self.create_zda_filename(slic, loc, rec)

        self.aPhz.open_zda_file(filename)

    def save_3_kinds_all_background_data(self):
        pa.alert("This will export all Background Maps. "
                 "To interrupt, move cursor to any corner of the screen.")

        self.get_zda_file_list()
        if len(self.record_tree.keys()) < 1:
            return
        self.set_up_SNR()
        self.save_all_background_data(load_file_list=False)
        self.set_up_prestim_SNR()
        self.save_all_background_data(load_file_list=False)
        self.set_up_MaxAmp()
        self.save_all_background_data(load_file_list=False)

    def set_up_SNR(self):
        self.aPhz.select_PhotoZ()
        self.return_to_lowest_recording()

    def set_up_prestim_SNR(self):
        self.return_to_lowest_recording()
        self.aPhz.open_preference(pre_file="tsm50ms_prestim.pre")
    
    def set_up_MaxAmp(self):
        self.aPhz.open_preference(pre_file="tsm50ms.pre")
        self.return_to_lowest_recording()
        self.aPhz.select_MaxAmp_array()

    def save_all_background_data(self, load_file_list=True):

        if load_file_list:
            self.get_zda_file_list()

        slice, loc, rec = self.get_initial_keys()
        button_to_increment = -1
        while button_to_increment is not None:
            print("saving Slice", slice, "Location", loc, "Record", rec)
            self.save_background(slice, loc, rec)

            slice, loc, rec, button_to_increment = self.iterate_tree(slice, loc, rec)

            while not self.click_file_button(level_index=button_to_increment):
                time.sleep(self.processing_sleep_time)

    def get_initial_keys(self):
        """ Assumes PhotoZ starts with the lowest number record open """
        curr_slice = min(self.record_tree.keys())
        curr_loc = min(self.record_tree[curr_slice].keys())
        curr_record = min(self.record_tree[curr_slice][curr_loc])
        return curr_slice, curr_loc, curr_record

    def iterate_tree(self, slice, loc, record):
        """ Return the next key set and the level to increment next,
                or None if iteration is done """
        curr_record_keys = self.record_tree[slice][loc]
        if max(curr_record_keys) > record:
            return slice, loc, record+1, 2  # increment at the record level

        # else we've hit the max record
        curr_loc_keys = self.record_tree[slice].keys()
        if max(curr_loc_keys) > loc and loc+1 in self.record_tree[slice]:  # skip to next slice if loc not consecutive
            record = min(self.record_tree[slice][loc+1])
            return slice, loc+1, record, 1  # increment at the location level

        # else we've hit the max loc
        curr_slice_keys = self.record_tree.keys()
        if max(curr_slice_keys) > slice and slice+1 in self.record_tree:  # end if slice not consecutive
            loc = min(self.record_tree[slice+1].keys())
            record = min(self.record_tree[slice+1][loc])
            return slice+1, loc, record, 0  # increment at the slice level

        return None, None, None, None

    def save_background(self, slice, loc, rec):

        retries = 10
        success = False
        while not success and retries > 0:
            self.click_image("images/save_background.png", retry_attempts=1)
            time.sleep(1)
            success = self.click_image("images/save_ok.png", retry_attempts=1)
            time.sleep(1)
            retries -= 1
        # Rename the file
        target_file = self.data_dir + "/Data.dat"  # default PhotoZ filename

        dst_filename = self.pad_zeros(slice) + "_" + self.pad_zeros(loc) + "_" + self.pad_zeros(rec) + ".dat"

        try:
            os.rename(target_file, self.get_target_dir() + self.file_prefix + dst_filename)
        except Exception as e:
            print("could not save", dst_filename)
            print(e)
        time.sleep(1)

    def get_zda_file_list(self):
        files = os.listdir(self.data_dir)
        print("AutoDAT", self.data_dir, files)
        for f in files:
            if f.endswith(".zda"):
                slice, loc, rec = self.parse_zda_filename(f)
                if slice not in self.record_tree:
                    self.record_tree[slice] = {}
                if loc not in self.record_tree[slice]:
                    self.record_tree[slice][loc] = []
                self.record_tree[slice][loc].append(rec)

    @staticmethod
    def parse_zda_filename(filename):
        x = filename[:-4].split("_")
        return [int(i) for i in x]

    @staticmethod
    def create_zda_filename(slic, loc, rec):
        f = ""
        for x in [slic, loc, rec]:
            x = str(x)
            if len(x) < 2:
                x = "0" + x
            f += x + "_"
        f = f[:-1] + ".zda"
        return f

    def click_file_button(self, level_index, increment=True):
        """ level_index: 0 - slice, 1 - location, 2 - record, 3 - trial """
        if level_index is None:
            return True
        locations = self.get_file_arrow_locations(right=increment)
        i = 0
        for loc in locations:
            if i == level_index:
                x, y = pa.center(loc)
                pa.click(x, y)
                break
            i += 1
        if i < level_index:
            print("increment button", level_index, "not found! Could not open correct file as a result.")
            return False
        time.sleep(self.processing_sleep_time)
        return True

    @staticmethod
    def get_file_arrow_locations(right=True):
        if right:
            return pa.locateAllOnScreen('images/right_file_arrow.png',
                                        confidence=0.9,
                                        grayscale=False)
        else:
            return pa.locateAllOnScreen('images/left_file_arrow.png',
                                        confidence=0.9,
                                        grayscale=False)
