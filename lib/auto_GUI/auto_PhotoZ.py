import pyautogui as pa
import time
import os
from datetime import date

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPhotoZ(AutoGUIBase):

    def __init__(self, data_dir="C:/Turbo-SM/SMDATA/John/"):
        self.photoZ_icon = "images/photoZ_icon.png"
        self.photoZ_small_icon = "images/photoZ_small_icon.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_create_folder = "images/photoZ_create_folder.png"

        self.data_dir = data_dir

    def select_PhotoZ(self):
        success = False
        while not success:
            self.click_image(self.photoZ_icon)
            if len([l for l in self.get_image_locations(self.photoZ_small_icon)]) > 2:
                return  # already selected
            success = self.click_nth_image(self.photoZ_small_icon, 1)

    def create_folder(self):
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

    def prepare_photoZ(self):
        self.select_PhotoZ()
        self.create_folder()
