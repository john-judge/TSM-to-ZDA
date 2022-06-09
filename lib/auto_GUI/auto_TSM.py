import pyautogui as pa
import time
import os

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoTSM(AutoGUIBase):

    def __init__(self):

        self.browse_button = 'images/tsm_browse.png'
        self.cam_setting = 'images/tsm_cam_setting.png'
        self.ok_button = 'images/tsm_ok.png'
        self.record_button = 'images/tsm_record.png'
        self.settings_button = 'images/tsm_settings.png'
        self.stim_delay_button = 'images/tsm_stim_delay.png'
        self.dark_frame_button = 'images/tsm_dark_frame.png'

        self.is_recording = False

    def prepare_TSM(self):
        """ Run after TSM is launched to put TSM in correct setting """

        self.click_image(self.ok_button)  # has 10 retry attempts
        self.click_until_gone(self.ok_button)  # clear all OK buttons, with 2 retries each hit

        # open Camera settings
        self.click_image(self.settings_button)
        # choose program (2000 Hz, 512x60)
        self.click_image(self.cam_setting)
        # select stim delay box
        self.click_image(self.stim_delay_button)
        # delete and change to 50ms
        pyautogui.press(['backspace', '5', '0'])
        # done
        self.click_image(self.ok_button)
        # open file browser for user
        self.click_image(self.browse_button)

    def run_recording_schedule(self,
                               trials_per_recording=5,
                               trial_interval=15,
                               number_of_recordings=1,
                               recording_interval=30):

        self.is_recording = True
        for i in range(number_of_recordings):
            # new dark frame each recording
            self.click_image(self.dark_frame_button)
            for j in range(trials_per_recording):
                self.click_image(self.record_button)
                time.sleep(trial_interval)
            if i < number_of_recordings - 1:
                time.sleep(recording_interval)
        self.is_recording = False
