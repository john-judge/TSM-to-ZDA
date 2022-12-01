import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPulser(AutoGUIBase):

    def __init__(self, pulser_setting_index=0):
        """ Pulser Setting index is the number of times to press down when selecting from Load Settings """
        self.pulser_setting_index = pulser_setting_index
        self.start_seq = "images/pulser_start_seq.png"
        self.file = "images/pulser_file.png"
        self.load_settings_button = "images/pulser_load_settings.png"
        self.pulser_select = "images/pulser_select.png"
        self.pulser_down_arrow = "images/pulser_down_arrow.png"
        self.pulser_connect_port = "images/pulser_connect_port.png"


    def prepare_pulser(self):
        """ Run this immediately after opening Pulser (does not select Pulser)"""
        self.open_port()
        self.load_settings()
        self.start_sequence()

    def open_port(self):
        self.click_image(self.pulser_connect_port)
        pa.press(['tab', 'down', 'down', 'enter'])

    def start_sequence(self):
        self.click_image(self.start_seq)

    def load_settings(self):

        self.click_image(self.file)
        self.click_image(self.load_settings_button)
        self.click_image(self.pulser_down_arrow)
        for _ in range(self.pulser_setting_index):
            pa.press('down')
        pa.press('enter')
        self.click_image(self.pulser_select)

    def set_up_tbs(self, is_connected):
        if not is_connected:
            pa.alert("Since Pulser is not connected to this machine,"
                     " please select the TBS settings for Pulser GUI"
                     " manually, then continue.")
        else:
            print("Pulser auto-TBS setting not implemented")

    def clean_up_tbs(self, is_connected):
        if not is_connected:
            pa.alert("Since Pulser is not connected to this machine,"
                     " please select the TBS settings for Pulser GUI"
                     " manually, then continue.")
        else:
            self.load_settings()


