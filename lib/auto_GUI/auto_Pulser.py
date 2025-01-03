import pyautogui as pa
import time
import os
import pandas as pd

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPulser(AutoGUIBase):

    def __init__(self):
        """ Pulser Setting index is the number of times to press down when selecting from Load Settings """
        super().__init__()
        self.confidence = 0.8
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
        """ return the index of the setting """
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
        """ pulser_setting_index is how many times to hit down arrow key in drop-down menu """
        self.click_image(self.pulser_file)
        time.sleep(0.5)
        self.click_image(self.pulser_load_settings)
        time.sleep(0.5)
        #self.click_next_to(self.pulser_select_config, 450)
        #time.sleep(0.5)
        for _ in range(pulser_setting_index):
            pa.press('down')
            time.sleep(.1)
        #pa.press('enter')
        time.sleep(0.5)
        self.click_image(self.pulser_select)
        if restart:
            self.restart_sequence()

    def set_up_tbs(self, is_connected):
        if not is_connected:
            pa.alert("Since Pulser is not connected to this machine,"
                     " please select the TBS settings for Pulser GUI"
                     " manually, then continue.")
            return
        self.highlight_pulser_window()
        setting_idx = self.get_pulser_setting('tbs')
        if setting_idx is None:
            print("Pulser setting for TBS does not exist. Creating.")
            setting = self.create_tbs_setting()
            setting_idx = self.get_pulser_setting(setting)
        self.load_settings(setting_idx, restart=True)

    def clean_up_tbs(self, is_connected):
        if not is_connected:
            pa.alert("Since Pulser is not connected to this machine,"
                     " please select the TBS settings for Pulser GUI"
                     " manually, then continue.")
        else:
            self.highlight_pulser_window()
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
            print("Pulser setting for " + str(ipi) + " ms does not exist. Creating.")
        if pulser_setting_index is None or should_create_settings:
            setting_name = self.create_delay_setting(ipi, alignment, T_end)
            pulser_setting_index = self.get_pulser_setting(setting_name)
        self.load_settings(pulser_setting_index, restart=True)

    def set_single_pulse_control(self, ipi, alignment, T_end, should_create_settings=False):
        """ Set up recording for a PPR control recording (single pulse at time of first pulse) """
        self.highlight_pulser_window()
        pulser_setting_index = self.get_pulser_setting(self.make_ipi_setting_name_control(ipi, alignment, T_end))
        if pulser_setting_index is None and not should_create_settings:
            print("Pulser PPR control setting for " + str(ipi) + " ms does not exist. Creating.")
        if pulser_setting_index is None or should_create_settings:
            setting_name = self.create_delay_setting(ipi, alignment, T_end, control=True)
            pulser_setting_index = self.get_pulser_setting(setting_name)
        self.load_settings(pulser_setting_index, restart=True)

    @staticmethod
    def make_ipi_setting_name_control(ipi, alignment, T_end):
        return 'PPR_control' + str(ipi) + "ms_" + alignment + "Aligned_End" + str(T_end) + "pt"
    
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

    def create_tbs_setting(self):
        """ Create a new Pulser setting for a tbs recording """
        self.click_next_to(self.pulser_total_trains, 100)
        field_values = [3, 0, 5, 5, 5, 5]  # 3 trains of 2 pulses = 6 pulses @ 100 Hz
        for i in range(len(field_values)):
            fv = field_values[i]
            pa.hotkey('ctrl', 'a')
            time.sleep(.1)
            pa.press(['backspace'])
            time.sleep(.1)
            self.type_string(str(fv))
            if i < len(field_values) - 1:
                pa.press(['tab'])
            time.sleep(.1)
        time.sleep(3)
        setting_name = 'tbs'
        self.save_setting(setting_name)
        self.update_setting_map(setting_name)
        return setting_name

    def create_delay_setting(self, interval, alignment, T_end, control=False):
        """ Create a new Pulser setting for a paired pulse recording """
        self.click_next_to(self.pulser_total_trains, 100)
        onset_delay = self.calculate_onset_delay(interval, alignment, T_end)
        field_values = [1, onset_delay, 1, interval, 1, 0]  # fields: total trains, TI, P1D, P1I, P2D, P2I
        if control:  # then erase second pulse
            field_values = [1, onset_delay, 1, 0, 0]  # one fewer, last field gets greyed out
        for i in range(len(field_values)):
            fv = field_values[i]
            pa.hotkey('ctrl', 'a')
            time.sleep(.1)
            pa.press(['backspace'])
            time.sleep(.1)
            self.type_string(str(fv))
            if i < len(field_values) - 1:
                pa.press(['tab'])
            time.sleep(.1)
        time.sleep(3)
        setting_name = self.make_ipi_setting_name(interval, alignment, T_end)
        if control:
            setting_name = self.make_ipi_setting_name_control(interval, alignment, T_end)
        self.save_setting(setting_name)
        self.update_setting_map(setting_name)
        return setting_name

    def save_setting(self, name):
        self.click_image(self.pulser_file)
        time.sleep(0.5)
        self.click_image(self.pulser_save_settings)
        time.sleep(0.5)
        self.click_next_to(self.pulser_new_name, 100)
        self.type_string(name)
        self.click_image(self.pulser_save)
