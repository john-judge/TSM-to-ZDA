import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoTSM(AutoGUIBase):

    def __init__(self):

        self.browse_button = 'images/tsm_browse.png'
        self.cam_setting = 'images/tsm_cam_setting.png'
        self.ok_button = 'images/tsm_ok.png'
        self.small_ok_button = 'images/tsm_small_ok.png'
        self.record_button = 'images/tsm_record.png'
        self.settings_button = 'images/tsm_settings.png'
        self.stim_delay_button = 'images/tsm_stim_delay.png'
        self.dark_frame_button = 'images/tsm_dark_frame.png'
        self.folder_SMDATA = 'images/folder_SMDATA.png'
        self.folder_John = 'images/folder_John.png'
        self.folder_open = 'images/folder_open.png'
        self.tsm_icon = 'images/tsm_icon.png'

        self.is_recording = False

    def select_TSM(self):
        self.click_image(self.tsm_icon)

    def select_camera_settings(self):
        # open Camera settings
        self.click_image(self.settings_button)
        # choose program (2000 Hz, 512x60)
        self.click_image(self.cam_setting)
        # select stim delay box
        self.click_image(self.stim_delay_button)
        # delete and change to 50ms
        time.sleep(1)
        pa.press(['backspace', '5', '0'])
        # done
        self.click_image(self.small_ok_button)

    def open_tsm_folder(self):
        success = False
        i = 0
        while not success and i < 10:
            self.click_image(self.browse_button, sleep=0.5)
            success = self.click_image(self.folder_SMDATA, sleep=0.5)
        self.click_image(self.folder_John, sleep=0.5, clicks=2)

    def prepare_TSM(self):
        """ Run after TSM is launched to put TSM in correct setting """
        self.select_TSM()
        self.click_image(self.ok_button)  # has 10 retry attempts
        self.click_until_gone(self.ok_button)  # clear all OK buttons, with 2 retries each hit
        time.sleep(3)
        self.select_camera_settings()
        time.sleep(3)
        self.open_tsm_folder()
        self.make_new_folder()  # If need to change this, simplify to simply title entire dir+file
        self.click_image(self.folder_open)

    def run_recording_schedule(self,
                               trials_per_recording=5,
                               trial_interval=15,
                               number_of_recordings=1,
                               recording_interval=30):

        self.is_recording = True
        for i in range(number_of_recordings):
            # new dark frame each recording
            self.click_image(self.dark_frame_button)
            self.click_image(self.ok_button)
            time.sleep(3)
            for j in range(trials_per_recording):
                self.click_image(self.record_button)
                time.sleep(trial_interval)
            if i < number_of_recordings - 1:
                time.sleep(recording_interval)
        self.is_recording = False
