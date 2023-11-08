import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPulser(AutoGUIBase):

    def __init__(self, pulser_setting_index=0, should_create_settings=False):
        """ Pulser Setting index is the number of times to press down when selecting from Load Settings """
        self.pulser_setting_index = pulser_setting_index
        self.start_seq = "images/pulser_start_seq.png"
        self.file = "images/pulser_file.png"
        self.pulser_load_settings = "images/pulser_load_settings.png"
        self.pulser_save_settings = 'images/pulser_save_settings.png'
        self.pulser_delete_settings = "images/pulser_delete_settings.png"
        self.pulser_select = "images/pulser_select.png"
        self.pulser_down_arrow = "images/pulser_down_arrow.png"
        self.pulser_connect_port = "images/pulser_connect_port.png"
        self.pulser_usb_port = 'images/pulser_usb_port.png'
        self.pulser_operation_mode = 'images/pulser_operation_mode.png'
        self.pulser_op_mode_2 = 'images/pulser_op_mode_2.png'
        self.pulser_new_name = 'images/pulser_new_name.png'
        self.pulser_save = 'images/pulser_save.png'

        self.delay_settings = [0, 10, 20, 30, 40, 50, 100, 120, 140, 160]
        self.setting_index = {}
        self.should_create_settings = should_create_settings

    def prepare_pulser(self):
        """ Run this immediately after opening Pulser (does not select Pulser)"""
        self.open_port()
        if self.should_create_settings:
            self.create_settings(delete_old=True)
        self.load_settings()
        self.start_sequence()

    def open_port(self):
        self.click_image(self.pulser_connect_port)
        self.click_image(self.pulser_usb_port)
        pa.press(['enter'])

    def start_sequence(self):
        time.sleep(.5)
        pa.scroll(-200)  # scroll to expose Operation Mode
        time.sleep(.5)
        try:
            self.click_next_to(self.pulser_operation_mode, 100)
        except Exception as e:
            print(e)
            return
        self.click_image(self.pulser_op_mode_2)
        self.click_image(self.start_seq)

    def load_settings(self):
        self.click_image(self.file)
        self.click_image(self.pulser_load_settings)
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

    def create_settings(self, delete_old=True):
        if delete_old:
            self.click_image(self.file)
            self.click_image(self.pulser_delete_settings)
        for interval in self.delay_settings:
            self.create_delay_setting(interval)

    def create_delay_setting(self, interval):
        self.click_next_to(self.pulser_total_trains, 100)
        field_values = [1, 0, 0, interval, 1, 0]  # fields: total trains, TI, P1D, P1I, P2D, P2I
        for fv in field_values:
            pa.hotkey('ctrl', 'a')
            time.sleep(.1)
            pa.press(['backspace'])
            time.sleep(.1)
            self.type_string(str(fv))
        self.save_setting('delay_' + str(interval) + "ms")

    def save_setting(self, name):
        self.click_image(self.file)
        self.click_image(self.pulser_save_settings)
        self.click_next_to(self.pulser_new_name, 100)
        self.type_string(name)
        self.click_image(self.pulser_save)




