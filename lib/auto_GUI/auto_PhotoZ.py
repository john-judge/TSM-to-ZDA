import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPhotoZ(AutoGUIBase):

    def __init__(self, data_dir="C:/Turbo-SM/SMDATA/John/"):
        self.photoZ_icon = "images/photoZ_icon.png"
        self.photoZ_small_icon = "images/photoZ_small_icon.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_preference = "images/photoZ_preference.png"

        self.data_dir = data_dir

    def select_PhotoZ(self):
        self.click_image(self.photoZ_icon)
        self.click_image(self.photoZ_small_icon)

    def create_folder(self):
        self.click_image(self.photoZ_file)
        self.type_string(self.data_dir)

    def prepare_photoZ(self):
        self.select_PhotoZ()
        self.create_folder()
