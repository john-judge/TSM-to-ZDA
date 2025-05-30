import pyautogui as pa
import time
import os
from datetime import date

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoPhotoZ(AutoGUIBase):

    def __init__(self, data_dir="C:/Turbo-SM/SMDATA/John/",
                 pre_file="tsm50ms.pre",
                 use_today=True,
                 skip_select_photoZ=False,
                 **kwargs):
        super().__init__()

        self.photoZ_icon = "images/photoZ_icon.png"
        self.photoZ_small_icon = "images/photoZ_small_icon.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_file = "images/photoZ_file.png"
        self.photoZ_preference_menu = "images/photoZ_preference.png"
        self.photoZ_load_preference = "images/photoZ_load_preference.png"
        self.photoZ_array = "images/photoZ_array.png"
        self.photoZ_cancel = "images/photoZ_cancel.png"
        self.photoZ_dsp = "images/photoZ_dsp.png"
        self.photoZ_baseline = "images/photoZ_baseline.png"
        self.photoZ_baseline_correction_type = "images/photoZ_baseline_correction_type.png"
        self.photoZ_baseline_start_and_end = "images/photoZ_baseline_start_and_end.png"
        self.photoZ_baseline_polynomial = "images/photoZ_baseline_polynomial.png"
        self.photoZ_poly_skip_start = "images/photoZ_poly_skip_start.png"
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
        self.photoZ_value_half_rise_time = "images/photoZ_value_half_rise_time.png"
        self.photoZ_value_half_decay_time = "images/photoZ_value_half_decay_time.png"
        self.photoZ_value_half_width = "images/photoZ_value_half_width.png"
        self.photoZ_value_peaktime = "images/photoZ_value_peaktime.png"
        self.photoZ_value_sd = "images/photoZ_value_sd.png"
        self.photoZ_save_values = "images/photoZ_save_values.png"
        self.photoZ_save_as_jpeg = "images/photoZ_save_as_jpeg.png"
        self.photoZ_nor2arraymax = "images/photoZ_nor2arraymax.png"
        self.photoZ_color = "images/photoZ_color.png"
        self.photoZ_color_upper_bound = "images/photoZ_color_upper_bound.png"

        if not data_dir.endswith("/"):
            data_dir = data_dir + "/"

        self.skip_select_photoZ = True  # skip_select_photoZ
        self.pre_file = pre_file
        self.data_dir = data_dir
        self.use_today = use_today
        self.drag_ratio = 8.33 / 853  # color scale change per pixel drag
        self.last_opened_roi_file = ''

    def get_last_opened_roi_file(self):
        return self.last_opened_roi_file

    def set_last_opened_roi_file(self, file):
        self.last_opened_roi_file = file

    def select_PhotoZ(self):
        if self.skip_select_photoZ:
            return
        success = False
        while not success:
            self.click_image(self.photoZ_icon)
            if len([l for l in self.get_image_locations(self.photoZ_small_icon)]) > 2:
                return  # already selected
            success = self.click_nth_image(self.photoZ_small_icon, 1)

    def select_array_tab(self):
        self.click_image(self.photoZ_array)

    def click_normalize_2_array_max(self):
        self.select_array_tab()
        self.click_image_if_found(self.photoZ_nor2arraymax)

    def save_background(self, filename=None):
        self.select_array_tab()
        self.click_image("images/save_background.png")
        time.sleep(1)
        if filename is not None:
            pa.hotkey('ctrl', 'a')
            time.sleep(1)
            pa.press(['backspace'])
            time.sleep(1)
            self.type_string(filename)
            time.sleep(1)
        success = self.click_image("images/save_ok.png")
        time.sleep(1)
        if filename is None:
            return self.data_dir + "/Data.dat"
        return filename

    def set_color_upper_bound(self, upper_bound, current_color_bound_setting):
        px_to_drag = int((upper_bound - current_color_bound_setting) / self.drag_ratio)

        self.click_image(self.photoZ_color)
        x, y = self.get_location_next_to_image(self.photoZ_color_upper_bound, 120)

        direction = 1
        if px_to_drag < 0:
            direction = -1
        px_to_drag = abs(px_to_drag)

        while px_to_drag > 300:
            self.click_location_and_drag(x, y, direction * 300, 0)
            px_to_drag -= 300
        if px_to_drag > 0:
            self.click_location_and_drag(x, y, direction * px_to_drag, 0)

    def set_measure_window(self, start, width, sleep_time_window_change=10):
        """
        :param start: Measure window start. if None, do not change
        :param width: Measure window width. if None, do not change
        :return: N/A
        """
        self.click_image(self.photoZ_dsp)
        self.click_image(self.photoZ_main)

        # change the measure window start
        if start is not None:
            self.click_next_to(self.photoZ_measure_window_start, 50)
            pa.hotkey('ctrl', 'a')
            time.sleep(1)
            pa.press(['backspace'])
            time.sleep(1)
            self.type_string(str(int(start)))
            time.sleep(1)
            pa.press(['enter'])
            time.sleep(sleep_time_window_change)

        # change the measure window width
        if width is not None:
            time.sleep(5)
            self.click_next_to(self.photoZ_measure_window_width, 50)
            pa.hotkey('ctrl', 'a')
            time.sleep(1)
            pa.press(['backspace'])
            time.sleep(1)
            self.type_string(str(int(width)))
            time.sleep(1)
            pa.press(['enter'])
            time.sleep(sleep_time_window_change)

    def change_baseline_correction(self, polynomial=True):
        baseline_correction_setting_image = self.photoZ_baseline_start_and_end
        if polynomial:
            baseline_correction_setting_image = self.photoZ_baseline_polynomial
        self.click_image(self.photoZ_baseline)
        time.sleep(1)
        self.click_next_to(self.photoZ_baseline_correction_type, 150)
        time.sleep(1)
        self.move_cursor_off()
        time.sleep(1)
        self.click_image(baseline_correction_setting_image)        
        time.sleep(15)

    def set_polynomial_skip_window(self, skip_window, skip_width=None):
        self.click_image(self.photoZ_baseline)
        self.click_next_to(self.photoZ_poly_skip_start, 50)
        pa.hotkey('ctrl', 'a')
        time.sleep(1)
        pa.press(['backspace'])
        time.sleep(1)
        self.type_string(str(skip_window))
        time.sleep(1)
        pa.press(['enter'])
        time.sleep(13)
        if skip_width is not None:
            pa.press(['tab'])
            time.sleep(1)
            self.type_string(str(skip_width))
            time.sleep(1)
            pa.press(['enter'])
            time.sleep(13)

    def save_map_jpeg(self, filename):
        self.click_image(self.photoZ_save_as_jpeg)
        time.sleep(0.5)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(1)
        pa.press(['backspace'])
        time.sleep(1)
        self.type_string(filename)
        time.sleep(1)
        pa.press(['enter'])

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
        time.sleep(8)

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
        self.select_array_tab()
        self.click_image(self.photoZ_binning)
        pa.hotkey('ctrl', 'a')  # make new folder
        time.sleep(1)
        pa.press(['backspace', '1', 'enter'])

    def select_roi_tab(self):
        self.click_image(self.photoZ_roi_tab, retry_attempts=2)

    def select_save_load_tab(self):
        self.click_image(self.photoZ_save_load_tab, 
                         retry_attempts=5, 
                         confidence_override=0.7,
                         drag=True)

    def save_current_traces(self, dst_file, go_to_tab=False):
        if go_to_tab:
            self.select_save_load_tab()
        time.sleep(1)
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
        if self.get_last_opened_roi_file() == file:
            return
        self.set_last_opened_roi_file(file)
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
        pa.press(['enter'])

    def select_latency_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_image(self.photoZ_value_latency)
        pa.press(['enter'])

    def select_maxamp_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_image(self.photoZ_value_maxamp)
        pa.press(['enter'])

    def select_peaktime_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_image(self.photoZ_value_peaktime)
        pa.press(['enter'])

    def select_half_width_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_image(self.photoZ_value_half_width)
        pa.press(['enter'])

    def select_sd_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_nth_image(self.photoZ_value_sd, 2)
        pa.press(['enter'])

    def select_half_rise_time_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_image(self.photoZ_value_half_rise_time)
        pa.press(['enter'])

    def select_half_decay_time_trace_value(self):
        self.move_cursor_off()
        self.click_next_to(self.photoZ_value, 120)
        self.move_cursor_off()
        self.click_image(self.photoZ_value_half_decay_time)
        pa.press(['enter'])

    def select_MaxAmp_array(self):
        self.select_array_tab()
        self.click_photoZ_background_menu()
        self.click_image(self.photoZ_background_MaxAmp)

    def select_SNR_array(self):
        self.select_array_tab()
        self.click_photoZ_background_menu()
        self.click_image(self.photoZ_background_SNR)

    def click_photoZ_background_menu(self):
        """ Open array background drop-down regardless of
            current selection """
        self.click_next_to(self.photoZ_background_menu, 120)
        self.move_cursor_off()

    def prepare_photoZ(self, select=True):
        if select:
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



