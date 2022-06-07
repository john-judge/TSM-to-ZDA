import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoDAT(AutoGUIBase):
    """ Automatically save background image data for many ZDA files """

    def __init__(self, datadir='.', processing_sleep_time=2, file_prefix=""):
        self.data_dir = datadir
        self.record_tree = {}
        self.processing_sleep_time = processing_sleep_time
        self.file_prefix = file_prefix

    def save_all_background_data(self):
        pa.alert("This will export all Background Maps. Make sure the directory entered matches the one open in"
                 " PhotoZ. Open the lowest slice/loc/record in PhotoZ and ensure that the cyan 'Save Background"
                 " Date' button is visible on the screen. To interrupt, move cursor to any corner of the screen.")

        self.get_zda_file_list()

        slice, loc, rec = self.get_initial_keys()
        button_to_increment = -1
        while button_to_increment is not None:
            print("saving Slice", slice, "Location", loc, "Record", rec)
            self.save_background(slice, loc, rec)

            slice, loc, rec, button_to_increment = self.iterate_tree(slice, loc, rec)
            self.click_file_button(level_index=button_to_increment)

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
        if max(curr_loc_keys) > loc:
            record = min(self.record_tree[slice][loc+1])
            return slice, loc+1, record, 1  # increment at the location level

        # else we've hit the max loc
        curr_slice_keys = self.record_tree.keys()
        if max(curr_slice_keys) > slice:
            loc = min(self.record_tree[slice+1].keys())
            record = min(self.record_tree[slice+1][loc])
            return slice+1, loc, record, 0  # increment at the slice level

        return None, None, None, None

    def save_background(self, slice, loc, rec):
        self.click_image("images/save_background.png")
        time.sleep(1)
        self.click_image("images/save_ok.png")
        time.sleep(1)
        # Rename the file
        target_file = self.data_dir + "/Data.dat"  # default PhotoZ filename

        dst_filename = self.pad_zeros(slice) + "_" + self.pad_zeros(loc) + "_" + self.pad_zeros(rec) + ".dat"

        try:
            os.rename(target_file, self.data_dir + "/" + self.file_prefix + dst_filename)
        except Exception as e:
            print("could not save", dst_filename)
            print(e)
        time.sleep(1)

    def get_zda_file_list(self):
        files = os.listdir(self.data_dir)
        print(files)
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

    def click_file_button(self, level_index, increment=True):
        """ level_index: 0 - slice, 1 - location, 2 - record, 3 - trial """
        if level_index is None:
            return
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
        time.sleep(self.processing_sleep_time)

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
