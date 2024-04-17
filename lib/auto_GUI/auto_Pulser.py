import pyautogui as pa
import time
import os
import pandas as pd

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPulser(AutoGUIBase):

    def __init__(self):
        """ Pulser Setting index is the number of times to press down when selecting from Load Settings """
        image_dir = 'images/pulser/'
        self.pulser_start_seq = image_dir + "pulser_start_seq.png"
        self.pulser_stop = image_dir + "pulser_stop.png"
        self.pulser_file = image_dir + "pulser_file.png"
        self.pulser_load_settings = image_dir + "pulser_load_settings.png"
        self.pulser_save_settings = image_dir + "pulser_save_settings.png"
        self.pulser_delete_settings = image_dir + "pulser_delete_settings.png"
        self.pulser_select = image_dir + "pulser_select.png"
        self.pulser_select_config = image_dir + "pulser_select_config.png"
        self.pulser_connect_port = image_dir + "pulser_connect_port.png"
        self.pulser_usb_port = image_dir + 'pulser_usb_port.png'
        self.pulser_operation_mode = image_dir + 'pulser_operation_mode.png'
        self.pulser_op_mode_2 = image_dir + 'pulser_op_mode_2.png'
        self.pulser_new_name = image_dir + 'pulser_new_name.png'
        self.pulser_save = image_dir + 'pulser_save.png'
        self.pulser_total_trains = image_dir + "pulser_total_trains.png"
        self.pulser_fingerprint = image_dir + "pulser_fingerprint.png"

        self.settings_file = 'pulser_settings.csv'
        self.pulser_setting_map = self.load_pulser_settings_file()

    def load_pulser_settings_file(self):
        try:
            df = pd.read_csv(self.settings_file)
            return pd.DataFrame(df)
        except FileNotFoundError:
            return pd.DataFrame(columns=['Names', 'Setting Index'])

    def update_setting_map(self, name):
        i_pulser = len(self.pulser_setting_map['Names'])
        self.pulser_setting_map = self.pulser_setting_map.append({'Names': name, 'Setting Index': i_pulser},
                                       ignore_index=True)
        self.pulser_setting_map.to_csv(self.settings_file, index=False)

    def does_setting_exist(self, name):
        return self.get_pulser_setting(name) is not None

    def get_pulser_setting(self, setting_name):
        df = self.pulser_setting_map
        df = df.loc[df['Names'] == setting_name, 'Setting Index']
        if len(df) < 1:
            return None
        if len(df) > 1:
            return df.iloc[0].item()
        return df.item()

    def prepare_pulser(self):
        """ Run this immediately after opening Pulser (does not select Pulser)"""
        self.open_port()
        setting_ind = self.get_pulser_setting('single_pulse')
        self.load_settings(setting_ind, restart=False)
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
        self.click_image(self.pulser_start_seq)

    def restart_sequence(self):
        self.click_image(self.pulser_stop)
        time.sleep(0.5)
        self.click_image(self.pulser_start_seq)

    def load_settings(self, pulser_setting_index, restart=False):
        print(pulser_setting_index, "\n", self.pulser_setting_map)
        """ pulser_setting_index is how many times to hit down arrow key in drop-down menu """
        self.click_image(self.pulser_file)
        self.click_image(self.pulser_load_settings)
        self.click_next_to(self.pulser_select_config, 150)
        time.sleep(0.5)
        for _ in range(pulser_setting_index):
            pa.press('down')
        pa.press('enter')
        self.click_image(self.pulser_select)
        if restart:
            self.restart_sequence()

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
            self.load_settings(0)

    def delete_settings(self):
        self.click_image(self.pulser_file)
        self.click_image(self.pulser_delete_settings)
        print("delete settings not implemented fully")

    def highlight_pulser_window(self):
        """ selects the pulser browser window as focus. Asks for user help if unable. """
        locations = self.get_image_locations(self.pulser_fingerprint)
        locations = [loc for loc in locations]
        while len(locations) < 1:
            pa.alert("Pulser window not in view. Please bring it into view before continuing.")
            locations = self.get_image_locations(self.pulser_fingerprint)
            locations = [loc for loc in locations]
        loc = locations[0]
        x, y = pa.center(loc)
        pa.click(x, y)
        return

    def set_double_pulse(self, ipi, alignment, T_end, should_create_settings=False):
        self.highlight_pulser_window()
        pulser_setting_index = self.get_pulser_setting(self.make_ipi_setting_name(ipi, alignment, T_end))
        if pulser_setting_index is None and not should_create_settings:
            pa.alert("Pulser setting for " + str(ipi) + " ms does not exist. Creating.")
        if pulser_setting_index is None or should_create_settings:
            setting_name = self.create_delay_setting(ipi, alignment, T_end)
            pulser_setting_index = self.get_pulser_setting(setting_name)
        self.load_settings(pulser_setting_index, restart=True)

    @staticmethod
    def make_ipi_setting_name(ipi, alignment, T_end):
        return 'paired' + str(ipi) + "ms_" + alignment + "Aligned_End" + str(T_end) + "pt"

    def calculate_onset_delay(self, interval, alignment, T_end):
        """ Based on the alignment (Left, Right, Center) and end of recording (T_end) calculate the onset delay """
        if alignment == 'Left':
            return 0
        if alignment == 'Right':
            return T_end - interval
        if alignment == 'Center':
            return (T_end - interval) / 2

    def create_delay_setting(self, interval, alignment, T_end):
        self.click_next_to(self.pulser_total_trains, 100)
        onset_delay = self.calculate_onset_delay(interval, alignment, T_end)
        field_values = [1, onset_delay, 1, interval, 1, 0]  # fields: total trains, TI, P1D, P1I, P2D, P2I
        for fv in field_values:
            pa.hotkey('ctrl', 'a')
            time.sleep(.1)
            pa.press(['backspace'])
            time.sleep(.1)
            self.type_string(str(fv))
            pa.press(['tab'])
        setting_name = self.make_ipi_setting_name(interval)
        self.save_setting(setting_name)
        self.update_setting_map(setting_name)
        return setting_name

    def save_setting(self, name):
        self.click_image(self.pulser_file)
        self.click_image(self.pulser_save_settings)
        self.click_next_to(self.pulser_new_name, 100)
        self.type_string(name)
        self.click_image(self.pulser_save)
