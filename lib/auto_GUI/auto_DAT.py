import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase
from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ


class AutoDAT(AutoGUIBase):
    """ Automatically save background image data for many ZDA files """

    def __init__(self, datadir='.', processing_sleep_time=2, file_prefix=""):
        super().__init__()
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        if not datadir.endswith("/"):
            datadir += "/"
        self.data_dir = datadir
        self.record_tree = {}
        self.processing_sleep_time = processing_sleep_time
        self.file_prefix = file_prefix
        self.aPhz = AutoPhotoZ(data_dir=self.data_dir)
        self.file_count = 0

        self.pulse2_pre_files = {
            0: None,
            20: 'tsm50ms_pulse20ms.pre',
            50: 'tsm50ms_pulse50ms.pre',
            100: 'tsm50ms_pulse100ms.pre'
        }

    def get_file_count(self):
        return self.file_count

    def get_target_dir(self):
        dir = self.data_dir
        if not dir.endswith("/"):
            dir += "/"
        # dir + "dat_output/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def return_to_lowest_recording(self):
        """ Select the lowest slice/loc/rec of the current directory """
        slic, loc, rec = self.get_initial_keys()
        filename = self.data_dir + self.create_zda_filename(slic, loc, rec)

        self.aPhz.open_zda_file(filename)

    def save_snr_background_data(self, disable_alert=False):
        if not disable_alert:
            pa.alert("This will export SNR Background Maps. "
                     "To interrupt, move cursor to any corner of the screen.")
        try:
            self.get_zda_file_list()
            if len(self.record_tree.keys()) < 1:
                return
            self.aPhz.select_PhotoZ()
            self.return_to_lowest_recording()
            self.save_all_background_data(load_file_list=False)
        except Exception as e:
            print(e)

    def save_snr_background_data_at_times(self, pulse2_times, allowed_times):
        """ Assumes PhotoZ is already selected and user has already been
                informed / given instructions """
        try:
            if self.file_count < 1:
                self.get_zda_file_list()
            if len(self.record_tree.keys()) < 1:
                return
            self.return_to_lowest_recording()
            self.save_background_data_with_pre_choice(pulse2_times, allowed_times)
        except Exception as e:
            print(e)

    def save_background_data_with_pre_choice(self, pulse2_times, allowed_times):
        i_file = 0
        slice, loc, rec = self.get_initial_keys()
        button_to_increment = -1
        current_pre = 0
        do_not_save_flag = False
        while button_to_increment is not None:
            next_pre = pulse2_times[i_file]
            if current_pre != next_pre and next_pre in allowed_times:
                pre_filename = self.pulse2_pre_files[next_pre]
                if pre_filename is not None and len(pre_filename) > 4:
                    self.aPhz.open_preference(pre_file=self.pulse2_pre_files[next_pre])
                    current_pre = next_pre
                else:
                    do_not_save_flag = True
            if not do_not_save_flag:
                print("saving Slice", slice, "Location", loc, "Record", rec, "at pulse stim time", current_pre, "ms")
                self.save_background(slice, loc, rec)
                do_not_save_flag = False
            else:
                time.sleep(self.processing_sleep_time)

            slice, loc, rec, button_to_increment = self.iterate_tree(slice, loc, rec)
            i_file += 1
            while not self.click_file_button(level_index=button_to_increment):
                time.sleep(self.processing_sleep_time)

    def save_3_kinds_all_background_data(self):
        pa.alert("This will export all Background Maps. "
                 "To interrupt, move cursor to any corner of the screen.")
        try:
            self.get_zda_file_list()
            if len(self.record_tree.keys()) < 1:
                return
            self.set_up_SNR()
            self.change_file_prefix("SNR")
            self.save_all_background_data(load_file_list=False)
            self.set_up_prestim_SNR()
            self.change_file_prefix("nostimSNR")
            self.save_all_background_data(load_file_list=False)
            self.set_up_MaxAmp()
            self.change_file_prefix("Amp")
            self.save_all_background_data(load_file_list=False)
        except Exception as e:
            print(e)

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

    def go_to_next_file(self, slice, loc, rec):
        """ Go to next file. Return False if no next file. """
        slice, loc, rec, button_to_increment = self.iterate_tree(slice, loc, rec)
        while not self.click_file_button(level_index=button_to_increment):
            time.sleep(self.processing_sleep_time)
        return slice, loc, rec, (button_to_increment is not None)

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

    def click_background_save_buttons(self):
        """ Save the current SNR background (return file name: ...dir/Data.dat)"""
        retries = 10
        success = False
        while not success and retries > 0:
            self.click_image("images/save_background.png", retry_attempts=1)
            time.sleep(1)
            success = self.click_image("images/save_ok.png", retry_attempts=1)
            time.sleep(1)
            retries -= 1
        if success:
            return self.data_dir + "/Data.dat"
        return None

    def save_background(self, slice, loc, rec, overwrite_existing=False):

        # Rename the file
        target_file = self.data_dir + "/Data.dat"  # default PhotoZ filename

        dst_filename = self.pad_zeros(slice) + "_" + self.pad_zeros(loc) + "_" + self.pad_zeros(rec) + ".dat"
        dst_filename_path = self.get_target_dir() + self.file_prefix + dst_filename

        if not overwrite_existing and os.path.exists(dst_filename_path):
            return dst_filename_path
        self.click_background_save_buttons()

        try:
            os.rename(target_file, dst_filename_path)
        except Exception as e:
            print("could not save", dst_filename)
            print(e)
        time.sleep(1)
        return dst_filename_path

    def get_zda_file_list(self):
        files = os.listdir(self.data_dir)
        print("AutoDAT", self.data_dir, files)
        self.file_count = 0
        for f in files:
            if f.endswith(".zda"):
                slice, loc, rec = self.parse_zda_filename(f)
                if slice not in self.record_tree:
                    self.record_tree[slice] = {}
                if loc not in self.record_tree[slice]:
                    self.record_tree[slice][loc] = []
                self.record_tree[slice][loc].append(rec)
                self.file_count += 1

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

    def jump_to_record(self, rec_no):
        """ Currently not used """
        self.aPhz.select_record_no_field()
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(1)
        pa.press(['backspace'])
        time.sleep(1)
        pa.press([c for c in str(rec_no)])
        pa.press(['enter'])
        time.sleep(self.processing_sleep_time)

    def increment_trial(self):
        self.click_file_button(3)

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

    def change_file_prefix(self, new_prefix):
        self.file_prefix = new_prefix

