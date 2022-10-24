import numpy as np
import threading
import time
import os
import PySimpleGUI as sg
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from webbrowser import open as open_browser

from lib.controller import Controller
from lib.automation import FileDetector
from lib.gui.layouts import Layouts
from lib.gui.event_mapping import EventMapping
from lib.acqui_data import AcquiData


class GUI:

    def __init__(self, production_mode=True,
                 n_group_by_trials=5):
        matplotlib.use("TkAgg")
        sg.theme('DarkGreen4')
        self.production_mode = production_mode
        self.acqui_data = AcquiData()
        self.layouts = Layouts(self.acqui_data)
        self.window = None

        new_rig_settings = os.path.exists("C:/Turbo-SM/SMDATA/")

        data_dir = "./tsm_targets/"  # All files in this directory + subdirectories are loaded
        if new_rig_settings:
            data_dir = None  # auto selects "C:/Turbo-SM/SMDATA/John/mm-dd-yy" on new rig
        self.acqui_data.num_trials = n_group_by_trials  # Treats every n selected files as trials to combine into single ZDA file

        self.controller = Controller(new_rig_settings=new_rig_settings,
                                     should_auto_launch=False,  # set to False as a safety to avoid double-launch
                                     acqui_data=self.acqui_data,
                                     datadir=data_dir)
        self.new_rig_settings = new_rig_settings
        if not self.production_mode:
            print("Data exchange directory:", self.controller.get_data_dir())

        # general state/settings
        self.title = "OrchestraZ"
        self.event_mapping = None

        if production_mode:
            self.define_event_mapping()  # event callbacks used in event loops
            self.main_workflow()

    def load_preference(self):
        raise NotImplementedError

    def save_preference(self):
        raise NotImplementedError

    def get_exchange_directory(self):
        return self.controller.get_data_dir()

    def auto_launch_all(self):
        self.controller.start_up()

    def main_workflow(self):
        right_col = self.layouts.create_right_column(self)
        left_col = self.layouts.create_left_column(self)
        toolbar_menu = self.layouts.create_menu()

        layout = [[toolbar_menu],
                  [sg.Column(left_col),
                   sg.VSeperator(),
                   sg.Column(right_col)]]

        self.window = sg.Window(self.title,
                                layout,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')
        self.main_workflow_loop()
        self.window.close()

    def main_workflow_loop(self, history_debug=False, window=None, exit_event="Exit"):
        if window is None:
            window = self.window
        events = ''
        while True:
            event, values = window.read()
            if history_debug and event is not None and not self.production_mode:
                events += str(event) + '\n'
            if event == exit_event or event == sg.WIN_CLOSED or event == '-close-':
                break
            elif event not in self.event_mapping or self.event_mapping[event] is None:
                print("Not Implemented:", event)
            else:
                ev = self.event_mapping[event]
                if event in values:
                    ev['args']['window'] = window
                    ev['args']['values'] = values[event]
                    ev['args']['event'] = event
                ev['function'](**ev['args'])
        if history_debug and not self.production_mode:
            print("**** History of Events ****\n", events)

    @staticmethod
    def draw_figure(canvas, fig):
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
        figure_canvas_agg.draw_idle()
        figure_canvas_agg.get_tk_widget().pack(fill='none', expand=True)
        return figure_canvas_agg

    # returns True if stop flag is set
    def sleep_and_check_stop_flag(self, sleep_time, interval=1):
        elapsed = 0
        while elapsed < sleep_time:
            time.sleep(interval)
            elapsed += interval
            if self.hardware.get_stop_flag():
                self.hardware.set_stop_flag(False)
                return True
        return False

    def record(self, **kwargs):
        raise NotImplementedError

    def choose_data_dir(self, **kwargs):
        folder = self.browse_for_folder()
        if folder is not None:
            self.controller.set_data_dir(folder)
            print("Selected data directory:", folder)

    @staticmethod
    def notify_window(title, message):
        layout = [[sg.Column([
            [sg.Text(message)],
            [sg.Button("OK")]])]]
        wind = sg.Window(title, layout, finalize=True)
        while True:
            event, values = wind.read()
            # End intro when user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break
        wind.close()

    def browse_for_file(self, file_extensions, multi_file=False, tsv_only=False):
        layout_choice = None
        if not multi_file:
            layout_choice = self.layouts.create_file_browser()
        else:
            layout_choice = self.layouts.create_files_browser()
        file_window = sg.Window('File Browser',
                                layout_choice,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')
        file = None
        # file browser event loop
        while True:
            event, values = file_window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                file_window.close()
                return
            elif event == "file_window.open":
                file = values["file_window.browse"]
                file_ext = file.split('.')
                if len(file_ext) > 0:
                    file_ext = file_ext[-1]
                else:
                    file_ext = ''
                if file_ext not in file_extensions:
                    supported_file_str = " ".join(file_extensions)
                    self.notify_window("File Type",
                                       "Unsupported file type.\nSupported: " + supported_file_str)
                else:
                    break
        file_window.close()
        return file

    def browse_for_save_as_file(self, file_types=(("Tab-Separated Value file", "*.tsv"),)):
        w = sg.Window('Save As',
                      self.layouts.create_save_as_browser(file_types),
                      finalize=True,
                      element_justification='center',
                      resizable=True,
                      font='Helvetica 18')
        new_file = None
        # file browser event loop
        while True:
            event, values = w.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                w.close()
                return
            elif event == "save_as_window.open":
                new_file = values["save_as_window.browse"]
                break
        w.close()
        if new_file is None or len(new_file) < 1:
            return None
        return new_file

    def browse_for_folder(self, recording_notif=True):
        folder_window = sg.Window('Folder Browser',
                                  self.layouts.create_folder_browser(),
                                  finalize=True,
                                  element_justification='center',
                                  resizable=True,
                                  font='Helvetica 18')
        folder = None
        # file browser event loop
        while True:
            event, values = folder_window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                folder_window.close()
                return
            elif event == "folder_window.open":
                folder = values["folder_window.browse"]
                break
        folder_window.close()
        if len(folder) < 1:
            return None
        return folder

    @staticmethod
    def launch_github_page(**kwargs):
        urls = {
            'technical': 'https://github.com/john-judge/TSM-to-ZDA',
            'user': 'https://github.com/john-judge/PhotoLib/blob/master/'
                    'TUTORIAL.md#users-manual-for-pyphoto21-little-dave',  # Update this to user tutorial link
            'issue': 'https://github.com/john-judge/TSM-to-ZDA/issues/new'
        }
        if 'kind' in kwargs and kwargs['kind'] in urls:
            open_browser(urls[kwargs['kind']], new=2)

    @staticmethod
    def launch_youtube_tutorial():
        pass

    @staticmethod
    def launch_little_dave_calendar(**kwargs):
        open_browser('https://calendar.google.com/calendar'
                     '/render?cid=24tfud764rqbe4tcdgvqmi6pdc@'
                     'group.calendar.google.com')

    # Returns True if string s is a valid numeric input
    @staticmethod
    def validate_numeric_input(s, non_zero=False, max_digits=None, min_val=None, max_val=None, decimal=False):
        if decimal:  # decimals: allow removing at most one decimal anywhere
            if len(s) > 0 and s[0] == '.':
                s = s[1:]
            elif len(s) > 0 and s[-1] == '.':
                s = s[:-1]
            elif '.' in s:
                s = s.replace('.', '')
        return type(s) == str \
               and s.isnumeric() \
               and (max_digits is None or len(s) <= max_digits) \
               and (not non_zero or int(s) != 0) \
               and (min_val is None or int(s) >= min_val) \
               and (max_val is None or int(s) <= max_val)

    @staticmethod
    def pass_no_arg_calls(**kwargs):
        for key in kwargs:
            if key.startswith('call'):
                kwargs[key]()

    def validate_and_pass_int(self, **kwargs):
        max_val = None
        if 'max_val' in kwargs:
            max_val = kwargs['max_val']
        fn_to_call = kwargs['call']
        v = kwargs['values']
        window = kwargs['window']
        while len(v) > 0 and not self.validate_numeric_input(v, max_digits=5, max_val=max_val):
            v = v[:-1]
        if len(v) > 0 and self.validate_numeric_input(v, max_digits=5, max_val=max_val):
            fn_to_call(value=int(v))
            window[kwargs['event']].update(v)
            if not self.production_mode:
                print("called:", fn_to_call)
            if 'call2' in kwargs:
                kwargs['call2'](value=int(v))
                if not self.production_mode:
                    print("called:", kwargs['call2'])
        else:
            fn_to_call(value=None)
            window[kwargs['event']].update('')

    def define_event_mapping(self):
        if self.event_mapping is None:
            self.event_mapping = EventMapping(self).get_event_mapping()

    def update_tracking_num_fields(self, no_plot_update=False, **kwargs):
        self.window["Slice Number"].update(self.acqui_data.get_slice_no())
        self.window["Location Number"].update(self.acqui_data.get_location_no())
        self.window["Record Number"].update(self.acqui_data.get_record_no())

    def set_slice(self, **kwargs):
        try:
            value = int(kwargs['value'])
        except TypeError as e:
            print(e)
            return
        self.acqui_data.slice_no = value

    def set_record(self, **kwargs):
        try:
            value = int(kwargs['value'])
        except TypeError as e:
            print(e)
            return
        self.acqui_data.record_no = value

    def set_location(self, **kwargs):
        try:
            value = int(kwargs['value'])
        except TypeError as e:
            print(e)
            return
        self.acqui_data.location_no = value

    def read_list_of_stim_times(self, pulse_file, allowed_times):
        stim_times = []

        # build a list of times
        with open(pulse_file, "r") as filestream:
            for line in filestream:
                line = line.replace("\t", " ").replace("  ", " ").replace(" ", ",")
                line = line.split(",")
                print(line)
                for time in line:
                    time = time.strip()
                    if len(time) > 0:
                        for allowed in allowed_times:
                            if str(allowed) in time:
                                stim_times.append(allowed)
                                break
        return stim_times

    def export_paired_pulse(self, **kwargs):
        """ PP SNR export according to .txt file a list of times (ms)
            separated by commas or whitespace
        """
        pulse_file = self.browse_for_file(file_extensions=['txt', 'csv'])
        if pulse_file is None:
            return
        allowed_times = [20, 50, 100, 0]
        pulse2_times = self.read_list_of_stim_times(pulse_file, allowed_times)

        # get SNR
        success = self.controller.export_paired_pulse(pulse2_times, allowed_times)
        if not success:
            self.notify_window("Invalid Paired Pulse timing file",
                               "Number of seond pulse times, " + str(len(pulse2_times)) + ", read from file does not match"
                               " number of recordings. Do you have the correct data directory selected?")
            print(pulse2_times)


