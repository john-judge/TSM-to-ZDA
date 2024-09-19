import pyautogui as pa
import time
import threading
import os
from datetime import date

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoTSM(AutoGUIBase):

    def __init__(self, use_today=True, data_dir="C:/Turbo-SM/SMDATA/John/"):
        super().__init__()

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
        self.num_recording_points_field = 'images/tsm_num_recording_points_field.png'
        self.shutter_wait = 'images/tsm_shutter_wait.png'

        self.is_recording = False
        self.data_dir = data_dir
        self.use_today = use_today

    def select_TSM(self):
        self.click_image(self.tsm_icon)

    def select_camera_settings(self, delay=100, shutter_wait=100):
        # open Camera settings
        self.click_image(self.settings_button)
        # choose program (2000 Hz, 512x60)
        self.click_image(self.cam_setting)
        # select stim delay box
        self.click_image(self.stim_delay_button)
        # delete and change to 50ms
        time.sleep(1)
        pa.press(['backspace'])
        self.type_string(str(delay))

        # set shutter wait
        time.sleep(1)
        self.click_next_to(self.shutter_wait, 140)
        time.sleep(1)
        self.key_delete_all()
        self.type_string(str(shutter_wait))
        time.sleep(1)
        # done
        self.click_image(self.small_ok_button)

    def set_num_recording_points(self, num_pts):
        # open Camera settings
        self.click_image(self.settings_button)
        # select num recording points
        time.sleep(1)
        self.click_num_recording_points_field()
        # delete and change to NUM_PTS
        time.sleep(1)
        pa.press(['backspace', 'backspace', 'backspace', 'backspace'])
        self.type_string(str(num_pts))
        # done
        self.click_image(self.small_ok_button)

    def click_num_recording_points_field(self):
        c = pa.locateOnScreen(self.num_recording_points_field,
                              confidence=0.8)
        x, y = pa.center(c)
        pa.click(x+120, y)
        self.move_cursor_off()

    def open_tsm_folder(self):
        success = False
        i = 0
        while not success and i < 10:
            self.click_image(self.browse_button, sleep=0.5)
            success = self.click_image(self.folder_SMDATA, sleep=0.5)
        self.click_image(self.folder_John, sleep=0.5, clicks=2)

    def create_tsm_folder(self, super_dir):
        dir = super_dir
        if self.use_today:
            today = date.today().strftime("%m-%d-%y")
            dir += today
        self.os_make_new_folder(dir)

    def prepare_TSM(self, num_points=200, num_extra_points=200, stim_delay=100):
        """
        num_extra_points: additional points to gather after requested
        Run after TSM is launched to put TSM in correct setting """
        self.select_TSM()
        self.click_image(self.ok_button)  # has 10 retry attempts
        self.click_until_gone(self.ok_button)  # clear all OK buttons, with 2 retries each hit
        time.sleep(3)
        self.select_camera_settings(delay=stim_delay)
        time.sleep(3)
        self.set_num_recording_points(num_points + num_extra_points)
        time.sleep(3)
        self.create_tsm_folder(self.data_dir)
        self.open_tsm_folder()
        if self.use_today:
            self.make_new_folder_today()  # If need to change this, simplify to simply title entire dir+file
        self.click_image(self.folder_open)

    def generate_stim_file(self, steady_state_freq, stim_delay, file_path):
        """ Generate a stim file for TSM """
        file_lines = [
            "5.0 - stim width (ms)",
            "",
            str(round(1000 / steady_state_freq, 1)) + " - stim interval (ms)",
            "",
            str(round(stim_delay, 1)) + " - stim delay (s) - the 1st stim",
        ]
        with open(file_path, 'w') as f:
            f.write("\n".join(file_lines))

    def run_recording_schedule(self,
                               stop_event,
                               trials_per_recording=5,
                               trial_interval=15,
                               number_of_recordings=1,
                               recording_interval=30,
                               init_delay=0,
                               select_tsm=True,
                               fan=None,
                               progress=None):
        if select_tsm:
            self.select_TSM()
        self.is_recording = True

        # ensure fan is off
        if fan is not None:
            fan_on = fan.is_fan_on()
            fan.manual_off()
            if fan_on and init_delay == 0:
                time.sleep(5)  # time for fan to stop spinning

        if init_delay > 0:
            print("Sleep for", init_delay, " minutes before recording.")
            for min in range(init_delay):
                progress.increment_progress_value(60)
                time.sleep(60)
                if stop_event.is_set():
                    return
            print("Delay done. Starting recording...")
        for i in range(number_of_recordings):
            # new dark frame each recording
            if trials_per_recording > 0:
                self.click_image(self.dark_frame_button)
                self.click_image(self.ok_button)
                time.sleep(3)
            for j in range(trials_per_recording):
                if stop_event.is_set():
                    return
                pa.moveTo(50, 50)
                self.click_image(self.record_button)
                if fan is not None:
                    fan.manual_on()
                    time.sleep(trial_interval / 2)
                    progress.increment_progress_value(trial_interval / 2)
                    fan.manual_off()
                time.sleep(trial_interval / 2)
                progress.increment_progress_value(trial_interval / 2)
            if i < number_of_recordings - 1:
                if fan is not None:
                    fan.manual_on()
                    time.sleep(recording_interval / 2)
                    progress.increment_progress_value(recording_interval / 2)
                    fan.manual_off()
                time.sleep(recording_interval / 2)
                progress.increment_progress_value(recording_interval / 2)
        self.is_recording = False

        # finally, turn on fan for extended cooling period
        if fan is not None:
            fan.manual_on()
