import pyautogui as pa
import time
import os
from datetime import date

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPhotoZ(AutoGUIBase):

    def __init__(self, data_dir="C:/Turbo-SM/SMDATA/John/",
                 pre_file="tsm50ms.pre",
                 use_today=True):
        self.photoZ_icon = "images/photoZ_icon.png"
        self.photoZ_small_icon = "images/photoZ_small_icon.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_preference_menu = "images/photoZ_preference.png"
        self.photoZ_load_preference = "images/photoZ_load_preference.png"
        self.photoZ_array = "images/photoZ_array.png"
        self.photoZ_cancel = "images/photoZ_cancel.png"
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
        self.photoZ_binning = "images/photoZ_binning.png"
        self.photoZ_background_SNR = "images/photoZ_background_SNR.png"
        self.photoZ_background_MaxAmp = "images/photoZ_background_MaxAmp.png"
        self.photoZ_background_menu = "images/photoZ_background_menu.png"
        self.photoZ_value_SNR = "images/photoZ_value_SNR.png"
        self.photoZ_value = "images/photoZ_value.png"
        self.photoZ_open = "images/photoZ_open.png"
        self.photoZ_record_no = "images/photoZ_record_no"
        self.photoZ_load_roi = "images/photoZ_load_roi.png"
        self.photoZ_roi_tab = "images/photoZ_roi_tab.png"
        self.photoZ_save_load_tab = "images/photoZ_save_load.png"
        self.photoZ_traces = "images/photoZ_traces.png"
        self.photoZ_rli_div = "images/photoZ_rli_div.png"
        self.photoZ_measure_window_start = "images/photoZ_measure_window_start.png"
        self.photoZ_measure_window_width = "images/photoZ_measure_window_width.png"
        self.photoZ_value_latency = "images/photoZ_value_latency.png"
        self.photoZ_value_maxamp = "images/photoZ_value_maxamp.png"
        self.photoZ_value_peaktime = "images/photoZ_value_peaktime.png"
        self.photoZ_save_values = "images/photoZ_save_values.png"

        if not data_dir.endswith("/"):
            data_dir = data_dir + "/"

        self.pre_file = pre_file
        self.data_dir = data_dir
        self.use_today = use_today

    def select_PhotoZ(self):
        success = False
        while not success:
            self.click_image(self.photoZ_icon)
            if len([l for l in self.get_image_locations(self.photoZ_small_icon)]) > 2:
                return  # already selected
            success = self.click_nth_image(self.photoZ_small_icon, 1)

    def set_measure_window(self, start, width):
        self.click_image(self.photoZ_dsp)
        self.click_image(self.photoZ_main)

        # change the measure window start
        self.click_next_to(self.photoZ_measure_window_start, 50)
        pa.hotkey('ctrl', 'a')
        time.sleep(1)
        pa.press(['backspace'])
        time.sleep(1)
        self.type_string(str(start))
        time.sleep(1)
        pa.press(['enter'])
        time.sleep(4)

        # change the measure window width
        self.click_next_to(self.photoZ_measure_window_width, 50)
        pa.hotkey('ctrl', 'a')
        time.sleep(1)
        pa.press(['backspace'])
        time.sleep(1)
        self.type_string(str(width))
        time.sleep(1)
        pa.press(['enter'])
        time.sleep(4)

    def open_preference(self, pre_file=None):
        self.click_image(self.photoZ_preference_menu)
        self.click_image(self.photoZ_load_preference)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(1)
        pa.press(['backspace'])
        time.sleep(1)
        pre_file_dir = os.getcwd().replace("\\", "/") + "/PhotoZ_pre/"
        if pre_file is None:
            self.type_string(pre_file_dir + self.pre_file)
        else:
            self.type_string(pre_file_dir + pre_file)
        time.sleep(2)
        pa.press(['enter'])
        time.sleep(2)
        pa.press(['enter'])

    def open_zda_file(self, file_full_path):
        if not file_full_path.endswith(".zda"):
            return
        self.select_PhotoZ()
        self.click_image(self.photoZ_file)
        self.move_cursor_off()
        self.click_image(self.photoZ_open)
        pa.hotkey('ctrl', 'a')
        pa.press(['backspace'])
        self.type_string(file_full_path)
        time.sleep(1)
        pa.press(['enter'])
        time.sleep(2)
        self.click_image(self.photoZ_cancel, retry_attempts=2)  # in case file not selectable

    def create_select_folder(self):
        self.click_image(self.photoZ_file)
        self.click_image(self.photoZ_create_folder)
        time.sleep(2)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(2)
        pa.press(['backspace'])
        dst_dir = self.data_dir
        if self.use_today:
            today = date.today().strftime("%m-%d-%y")
            dst_dir += "/" + today
        self.type_string(dst_dir)  # to-do: this dir might not exist yet
        time.sleep(2)
        pa.press(['enter'])
        time.sleep(1)
        self.click_image(self.photoZ_cancel, retry_attempts=2)  # in case folder already exists

    def turn_on_inversing(self):
        self.click_image(self.photoZ_dsp)
        self.click_image(self.photoZ_main)
        self.click_image(self.photoZ_inverse)

    def turn_on_rli_div(self, select_tab=True):
        if select_tab:
            self.click_image(self.photoZ_dsp)
            self.click_image(self.photoZ_main)
        self.click_image(self.photoZ_rli_div)

    def turn_on_filters(self):
        self.click_image(self.photoZ_filter)
        self.click_image(self.photoZ_filter_type)
        self.click_image(self.photoZ_binomial8)
        self.click_image(self.photoZ_s_filter_slider)

        self.click_image(self.photoZ_t_filter)
        time.sleep(2)
        self.click_image(self.photoZ_s_filter)

    def turn_off_binning(self):
        self.click_image(self.photoZ_array)
        self.click_image(self.photoZ_binning)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(1)
        pa.press(['backspace', '1', 'enter'])

    def select_roi_tab(self):
        self.click_image(self.photoZ_roi_tab, retry_attempts=2)

    def select_save_load_tab(self):
        self.click_image(self.photoZ_save_load_tab, retry_attempts=2)

    def save_current_traces(self, dst_file):
        self.click_image(self.photoZ_traces)
        time.sleep(1)
        self.type_string(dst_file)
        time.sleep(1)
        self.click_image("images/save_ok.png")

    def save_trace_values(self, dst_file):
        self.click_image(self.photoZ_save_load_tab)
        self.click_image(self.photoZ_save_values)
        time.sleep(1)
        self.type_string(dst_file)
        time.sleep(1)
        self.click_image("images/save_ok.png")

    def open_roi_file(self, file):
        self.click_image(self.photoZ_load_roi)
        self.type_string(file)
        time.sleep(2)
        pa.press(['enter'])
        time.sleep(1)

    def select_SNR_displays(self):
        self.select_SNR_array()
        self.select_SNR_trace_value()

    def select_SNR_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.click_image(self.photoZ_value_SNR)

    def select_latency_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.click_image(self.photoZ_value_latency)

    def select_maxamp_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.click_image(self.photoZ_value_maxamp)

    def select_peaktime_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.click_image(self.photoZ_value_peaktime)

    def select_MaxAmp_array(self):
        self.click_image(self.photoZ_array)
        self.click_photoZ_background_menu()
        self.click_image(self.photoZ_background_MaxAmp)

    def select_SNR_array(self):
        self.click_image(self.photoZ_array)
        self.click_photoZ_background_menu()
        self.click_image(self.photoZ_background_SNR)

    def click_photoZ_background_menu(self):
        """ Open array background drop-down regardless of
            current selection """
        self.click_next_to(self.photoZ_background_menu, 120)
        self.move_cursor_off()

    def prepare_photoZ(self):
        self.select_PhotoZ()
        self.create_select_folder()
        self.open_preference()
        self.turn_on_inversing()
        self.turn_on_rli_div(select_tab=False)
        self.turn_on_filters()
        self.turn_off_binning()
        self.select_SNR_displays()

    def select_record_no_field(self):
        """ Currently not used """
        self.move_cursor_off()
        self.click_next_to(self.photoZ_record_no, 120)



