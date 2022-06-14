import numpy as np
import threading
import time
import os
import PySimpleGUI as sg
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from lib.controller import Controller
from lib.automation import FileDetector
from lib.gui.daq import DAQViewer
from lib.gui.layouts import Layouts
from lib.gui.event_mapping import EventMapping


class GUI:

    def __init__(self, production_mode=True):
        matplotlib.use("TkAgg")
        sg.theme('DarkBlue12')
        data.gui = self
        self.production_mode = production_mode
        self.dv = DAQViewer(self.data)
        self.layouts = Layouts(data)
        self.window = None

        # general state/settings
        self.title = "Photo21"
        self.event_mapping = None
        self.define_event_mapping()  # event callbacks used in event loops

        self.main_workflow()

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
        self.plot_daq_timeline()
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
                if self.is_recording():
                    self.data.save_metadata_to_json()
                    print("Cleaning up hardware before exiting. Waiting until safe to exit (or at most 3 seconds)...")

                    self.hardware.set_stop_flag(True)
                    timeout = 3
                    while self.hardware.get_stop_flag() and timeout > 0:
                        time.sleep(1)
                        timeout -= 1
                        print(timeout, "seconds")
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

    def is_recording(self):
        return self.freeze_input and not self.data.get_is_loaded_from_file()

    @staticmethod
    def draw_figure(canvas, fig):
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
        figure_canvas_agg.draw_idle()
        figure_canvas_agg.get_tk_widget().pack(fill='none', expand=True)
        return figure_canvas_agg

    def get_trial_sleep_time(self):
        sleep_sec = self.data.get_int_trials()
        if self.data.get_is_schedule_rli_enabled():
            sleep_sec = max(0, sleep_sec - .12)  # attempt to shorten by 120 ms, rough lower bound on time to take RLI
        return sleep_sec

    def get_record_sleep_time(self):
        sleep_sec = self.data.get_int_records()
        return max(0, sleep_sec - self.get_trial_sleep_time())

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
        if self.freeze_input and not self.data.get_is_loaded_from_file():
            file = None
            self.notify_window("File Input Error",
                               "Cannot load file during acquisition")
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
        if self.is_recording():
            new_file = self.data.get_save_dir()
            self.notify_window("Warning",
                               "Please stop recording before exporting data.")
            new_file = None
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
        if recording_notif and self.is_recording():
            folder = self.data.get_save_dir()
            self.notify_window("Warning",
                               "You are changing the save location during acquisition." +
                               "I don't recommend scattering your files. " +
                               "Keeping this save directory:\n" +
                               folder)
        folder_window.close()
        if len(folder) < 1:
            return None
        return folder

    # Pull all file-based data from Data and sync GUI fields
    def sync_gui_fields_from_meta(self):
        w = self.window

        # Hardware settings
        w['Number of Points'].update(self.data.get_num_pts())
        w['int_records'].update(self.data.get_int_records())
        w['num_records'].update(self.data.get_num_records())
        w['Acquisition Onset'].update(self.data.get_acqui_onset())
        w['Acquisition Duration'].update(self.data.get_acqui_duration())
        w['Stimulator #1 Onset'].update(self.data.get_stim_onset(1))
        w['Stimulator #2 Onset'].update(self.data.get_stim_onset(2))
        w['Stimulator #1 Duration'].update(self.data.get_stim_duration(1))
        w['Stimulator #2 Duration'].update(self.data.get_stim_duration(2))
        w['int_trials'].update(self.data.get_int_trials())
        w['num_trials'].update(self.data.get_num_trials())
        w['-CAMERA PROGRAM-'].update(self.data.display_camera_programs[self.data.get_camera_program()])
        self.dv.update()


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

    def set_acqui_onset(self, **kwargs):
        v = kwargs['values']
        while len(v) > 0 and not self.validate_numeric_input(v, decimal=True, max_val=5000):
            v = v[:-1]
        if self.validate_numeric_input(v, decimal=True, max_val=5000):
            num_frames = float(v) // self.data.get_int_pts()
            self.data.set_acqui_onset(float(num_frames))
            self.window['Acquisition Onset'].update(v)
            self.dv.update()

    def set_num_pts(self, suppress_resize=False, **kwargs):
        v = kwargs['values']

        while len(v) > 0 and not self.validate_numeric_input(v, decimal=True, max_val=5000):
            v = v[:-1]
        if len(v) > 0 and self.validate_numeric_input(v, decimal=True, max_val=5000):
            acqui_duration = float(v) * self.data.get_int_pts()
            self.data.set_num_pts(value=int(v), prevent_resize=suppress_resize)  # Data method resizes data
            self.window["Number of Points"].update(v)
            self.window["Acquisition Duration"].update(str(acqui_duration))
        else:
            self.data.set_num_pts(value=0, prevent_resize=suppress_resize)  # Data method resizes data
            self.window["Number of Points"].update('')
            self.window["Acquisition Duration"].update('')
        self.dv.update()
        self.update_tracking_num_fields(no_plot_update=True)
        if self.data.core.get_is_temporal_filter_enabled():
            filter_type = self.data.core.get_temporal_filter_options()[
                self.data.core.get_temporal_filter_index()]
            sigma_t = self.data.core.get_temporal_filter_radius()
            if not self.data.validate_filter_size(filter_type, sigma_t):
                self.notify_window("Invalid Settings",
                                   "Measure window is too small for the"
                                   " default cropping needed for the temporal filter"
                                   " settings. \nUntil measure window is widened or "
                                   " filtering radius is decreased, temporal filtering will"
                                   " not be applied to traces.")

    def plot_daq_timeline(self):
        fig = self.dv.get_fig()
        self.draw_figure(self.window['daq_canvas'].TKCanvas, fig)
        self.dv.update()

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

    # for passing to channel-based setters
    def validate_and_pass_channel(self, **kwargs):
        fns_to_call = []
        for k in kwargs:
            if k.startswith('call'):
                fns_to_call.append(kwargs[k])
        v = kwargs['values']
        ch = kwargs['channel']
        window = kwargs['window']
        while len(v) > 0 and not self.validate_numeric_input(v, max_digits=6):
            v = v[:-1]
        if len(v) > 0 and self.validate_numeric_input(v, max_digits=6):
            for fn in fns_to_call:
                fn(value=int(v), channel=ch)
            window[kwargs['event']].update(v)
            if not self.production_mode:
                print("called:", fns_to_call)
        else:
            for fn in fns_to_call:
                fn(value=0, channel=ch)
            window[kwargs['event']].update('')

        # update DAQ timeline visualization
        self.dv.update()

    def set_num_trials(self, **kwargs):
        v = kwargs['values']
        self.data.set_num_trials(int(v))

    def define_event_mapping(self):
        if self.event_mapping is None:
            self.event_mapping = EventMapping(self).get_event_mapping()

    def update_tracking_num_fields(self, no_plot_update=False, **kwargs):
        self.window["Slice Number"].update(self.data.get_slice_num())
        self.window["Location Number"].update(self.data.get_location_num())
        self.window["Record Number"].update(self.data.get_record_num())
        self.window["Trial Number"].update(self.data.get_current_trial_index())
        self.window["File Name"].update(self.data.db.get_current_filename(no_path=True,
                                                                          extension=self.data.db.extension))

    def set_current_trial_index(self, **kwargs):
        if 'value' in kwargs:
            if kwargs['value'] is None:
                value = None
            else:
                value = int(kwargs['value'])
            self.data.set_current_trial_index(value)

    def set_slice(self, **kwargs):
        value = int(kwargs['value'])
        self.data.set_slice(value)

    def set_record(self, **kwargs):
        value = int(kwargs['value'])
        self.data.set_record(value)

    def set_location(self, **kwargs):
        value = int(kwargs['value'])
        self.data.set_location(value)
