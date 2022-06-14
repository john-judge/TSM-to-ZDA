import pyautogui as pa
import time
import os
from datetime import date

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPhotoZ(AutoGUIBase):

    def __init__(self, data_dir="C:/Turbo-SM/SMDATA/John/",
                 pre_file="tsm50ms.pre"):
        self.photoZ_icon = "images/photoZ_icon.png"
        self.photoZ_small_icon = "images/photoZ_small_icon.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_preference_menu = "images/photoZ_preference.png"
        self.photoZ_load_preference = "images/photoZ_load_preference.png"
        self.photoZ_array = "images/photoZ_array.png"
        self.photoZ_dsp = "images/photoZ_dsp.png"
        self.photoZ_main = "images/photoZ_main.png"
        self.photoZ_filter = "images/photoZ_filter.png"
        self.photoZ_binomial8 = "images/photoZ_binomial8.png"
        self.photoZ_filter_type = "images/photoZ_filter_type.png"
        self.photoZ_inverse = "images/photoZ_inverse.png"
        self.photoZ_s_filter = "images/photoZ_s_filter.png"
        self.photoZ_t_filter = "images/photoZ_t_filter.png"
        self.photoZ_s_filter_slider = "images/photoZ_s_filter_slider.png"
        self.photoZ_create_folder = "images/photoZ_create_folder.png"

        self.pre_file = data_dir + pre_file
        self.data_dir = data_dir

    def select_PhotoZ(self):
        success = False
        while not success:
            self.click_image(self.photoZ_icon)
            if len([l for l in self.get_image_locations(self.photoZ_small_icon)]) > 2:
                return  # already selected
            success = self.click_nth_image(self.photoZ_small_icon, 1)

    def open_preference(self):
        self.click_image(self.photoZ_preference_menu)
        self.click_image(self.photoZ_load_preference)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(2)
        pa.press(['backspace'])
        self.type_string(self.pre_file)
        time.sleep(2)
        pa.press(['enter'])

    def create_select_folder(self):
        self.click_image(self.photoZ_file)
        self.click_image(self.photoZ_create_folder)
        time.sleep(2)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(2)
        pa.press(['backspace'])
        today = date.today().strftime("%m-%d-%y")
        self.type_string(self.data_dir + "/" + today)
        time.sleep(2)
        pa.press(['enter'])

    def turn_on_inversing(self):
        self.click_image(self.photoZ_dsp)
        self.click_image(self.photoZ_main)
        self.click_image(self.photoZ_inverse)

    def turn_on_filters(self):
        self.click_image(self.photoZ_filter)
        self.click_image(self.photoZ_filter_type)
        self.click_image(self.photoZ_binomial8)
        self.click_image(self.photoZ_s_filter_slider)

        self.click_image(self.photoZ_t_filter)
        time.sleep(2)
        self.click_image(self.photoZ_s_filter)

    def prepare_photoZ(self):
        self.select_PhotoZ()
        self.create_select_folder()
        self.open_preference()
        self.turn_on_inversing()
        self.turn_on_filters()

        # select array tab
        self.click_image(self.photoZ_array)

