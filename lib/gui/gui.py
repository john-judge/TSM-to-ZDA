import numpy as np
import threading
import time
import os
import PySimpleGUI as sg
import matplotlib
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from webbrowser import open as open_browser
import json
import inspect

from lib.controller import Controller
from lib.automation import FileDetector
from lib.gui.layouts import Layouts
from lib.gui.event_mapping import EventMapping
from lib.acqui_data import AcquiData
from lib.gui.progress import Progress


class GUI:

    def __init__(self, production_mode=True,
                 n_group_by_trials=5,
                 camera_program=4):
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

        self.controller = Controller(camera_program,
                                     new_rig_settings=new_rig_settings,
                                     should_auto_launch=False,  # set to False as a safety to avoid double-launch
                                     acqui_data=self.acqui_data,
                                     datadir=data_dir)
        self.new_rig_settings = new_rig_settings
        if not self.production_mode:
            print("Data exchange directory:", self.controller.get_data_dir())

        # general state/settings
        self.title = "OrchestraZ"
        self.event_mapping = None
        self.progress = None

        if production_mode:
            self.define_event_mapping()  # event callbacks used in event loops
            self.main_workflow()
        
    def load_preference(self):
        # open pa dialogue to choose a json file
        pref_file = self.browse_for_file(file_extensions=['json'])
        if pref_file is None:
            return
        
        # load json file
        with open(pref_file, "r") as f:
            save_dict = json.load(f)

        ad_dict = save_dict["AcquiData"]
        c_dict = save_dict["Controller"]
        print("Loaded preference file attributes:",
              save_dict)

        # set AcquiData and Controller objects from save dict
        self.acqui_data.set_save_attributes(ad_dict)
        self.controller.set_save_attributes(c_dict)

        self.update_gui_from_save_dict(save_dict)

    def save_preference(self):
        # open pa dialogue to choose a json file to save to
        pref_file = self.browse_for_save_as_file(file_types=(("JSON file", "*.json"),))
        if pref_file is None:
            return
        
        # pull save dicts from AcquiData and Controller objects

        ad_dict = self.acqui_data.get_save_dict()
        c_dict = self.controller.get_save_dict()
        
        # orgnize dicts into a single dict
        save_dict = {"AcquiData": ad_dict, "Controller": c_dict}

        # save dict to json file
        with open(pref_file, "w") as f:
            json.dump(save_dict, f)

    def update_gui_from_save_dict(self, save_dict):
        self.update_tracking_num_fields()
        self.window["num_trials"].update(save_dict['AcquiData']['num_trials'])
        self.window["int_trials"].update(save_dict['AcquiData']['int_trials'])
        self.window["Skip Points"].update(save_dict['AcquiData']['num_skip_points'])
        self.window["Flatten Points"].update(save_dict['AcquiData']['num_flatten_points'])
        self.window["Initial Delay"].update(save_dict['AcquiData']['init_delay'])

        self.window["Collect Points"].update(save_dict['AcquiData']['num_points'])
        self.window["Extra Points"].update(save_dict['AcquiData']['num_extra_points'])
        self.window["Paired Pulse"].update(save_dict['AcquiData']['is_paired_pulse_recording'])
        self.window["PPR Start"].update(save_dict['AcquiData']['ppr_ipi_interval'][0])
        self.window["PPR End"].update(save_dict['AcquiData']['ppr_ipi_interval'][1])
        self.window["PPR Interval"].update(save_dict['AcquiData']['ppr_ipi_interval'][2])
        self.window["SS End"].update(save_dict['AcquiData']['steady_state_freq_end'])
        self.window["SS Start"].update(save_dict['AcquiData']['steady_state_freq_start'])
        self.window["SS Interval"].update(save_dict['AcquiData']['steady_state_freq_interval'])
        self.window["MM Start Pt"].update(save_dict['AcquiData']['mm_start_pt'])
        self.window["MM End Pt"].update(save_dict['AcquiData']['mm_end_pt'])
        self.window["MM Frame Interval"].update(save_dict['AcquiData']['mm_interval'])
        self.window["Overwrite Frames"].update(save_dict['AcquiData']['mm_overwrite_frames'])

        self.window["New rig settings"].update(save_dict['Controller']['new_rig_settings'])
        self.window["+ Pulser"].update(save_dict['Controller']['should_auto_launch_pulser'])
        self.window["Create Pulser IPI Settings"].update(save_dict['Controller']['should_create_pulser_settings'])
        self.window["Convert Files Switch"].update(save_dict['Controller']['should_convert_files'])        
        self.window["Shorten recording"].update(save_dict['Controller']['shorten_recording'])
        self.window["Fan"].update(save_dict['Controller']['is_fan_enabled'])
        self.window["Today subdir"].update(save_dict['Controller']['use_today_subdir'])
        self.window["ppr_alignment_settings"].update(save_dict['Controller']['ppr_alignment'])
        self.window["PPR Control"].update(save_dict['Controller']['should_take_ppr_control'])
        self.window["Amplitude Trace Export"].update(save_dict['Controller']['is_export_amp_traces'])
        self.window["SNR Trace Export"].update(save_dict['Controller']['is_export_snr_traces'])
        self.window["Latency Trace Export"].update(save_dict['Controller']['is_export_latency_traces'])
        self.window["Halfwidth Trace Export"].update(save_dict['Controller']['is_export_halfwidth_traces'])
        self.window["Trace Export"].update(save_dict['Controller']['is_export_traces'])
        self.window['Trace_export_non_polyfit'].update(save_dict['Controller']['is_export_traces_non_polyfit'])
        self.window["SD Export"].update(save_dict['Controller']['is_export_sd_traces'])
        self.window["SNR Map Export"].update(save_dict['Controller']['is_export_snr_maps'])
        self.window["Max Amp Map Export"].update(save_dict['Controller']['is_export_max_amp_maps'])
        self.window["Export Trace Prefix"].update(save_dict['Controller']['export_trace_prefix'])
        self.window["roi_export_options"].update(save_dict['Controller']['roi_export_idx'])
        self.window["electrode_export_options"].update(save_dict['Controller']['electrode_export_idx'])
        self.window["Electrode Export Keyword"].update(save_dict['Controller']['export_electrode_keyword'])
        self.window["ROIs Export Keyword"].update(save_dict['Controller']['export_rois_keyword'])
        self.window["IDs Zero-Padded"].update(save_dict['Controller']['zero_pad_ids'])
        self.window["Microns per Pixel"].update(save_dict['Controller']['microns_per_pixel'])
        self.window["Num Export Trials"].update(save_dict['Controller']['num_export_trials'])
        self.window["Export by trial"].update(save_dict['Controller']['is_export_by_trial'])

        self.window.refresh()

    def get_exchange_directory(self):
        return self.controller.get_data_dir()

    def auto_launch_all(self):
        self.controller.start_up()

    def main_workflow(self):
        right_col = self.layouts.create_right_column(self)
        left_col = self.layouts.create_left_column(self)
        toolbar_menu = self.layouts.create_menu()
        progress_bar = self.layouts.create_progress_bar()

        layout = [[toolbar_menu + progress_bar],
                  [sg.Column(left_col),
                   sg.VSeperator(),
                   sg.Column(right_col)]]

        self.window = sg.Window(self.title,
                                layout,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')

        self.progress = Progress(self.window)
        self.controller.set_progress(self.progress)

        self.main_workflow_loop()
        self.window.close()

    def main_workflow_loop(self, history_debug=False, window=None, exit_event="Exit"):
        if window is None:
            window = self.window
        events = ''
        current_task = None
        stop_event = None
        while True:
            event, values = window.read()

            if history_debug and event is not None and not self.production_mode:
                events += str(event) + '\n'
            if event == exit_event or event == sg.WIN_CLOSED or event == '-close-':
                break
            elif event not in self.event_mapping or self.event_mapping[event] is None:
                if event == 'cancel_button':
                    print("Requesting current task to cancel...")
                    stop_event.set()
                    if current_task is not None:
                        current_task.join()
                        print("Current task cancelled.")
                        self.progress.complete()
                else:
                    print("Not Implemented:", event)
            else:
                ev = self.event_mapping[event]
                if event in values:
                    ev['args']['window'] = window
                    ev['args']['values'] = values[event]
                    ev['args']['event'] = event
                
                # threading to avoid blocking the GUI. Discard task if one is already running
                if current_task is None or not current_task.is_alive():

                    # copy ev['args'] to new dict
                    event_dict = {}
                    for key in ev['args']:
                        event_dict[key] = ev['args'][key]
                    stop_event = threading.Event()
                    
                    # for unstoppable events, filter out stop_event kwarg
                    if 'kwargs' in [param.name for param in inspect.signature(ev['function']).parameters.values()]:
                        event_dict['stop_event'] = stop_event

                    # Some events are stoppable from the cancel button, so they are run in a separate thread
                    if 'stoppable' in ev:
                        print('Starting stoppable thread for', ev['function'])
                        current_task = threading.Thread(target=ev['function'],
                                    kwargs=event_dict,
                                    daemon=True)
                        current_task.start()
                    else:
                        print("Running event from main thread (unstoppable)")
                        ev['function'](**event_dict)
                else:
                    print("OrchZ daemon is busy. Ignoring event:", event)
            
            # in case current task finishes or raises exception without marking progress as complete
            if current_task is not None and not current_task.is_alive():
                self.progress.complete()

        if history_debug and not self.production_mode:
            print("**** History of Events ****\n", events)

    '''@staticmethod
    def draw_figure(canvas, fig):
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
        figure_canvas_agg.draw_idle()
        figure_canvas_agg.get_tk_widget().pack(fill='none', expand=True)
        return figure_canvas_agg'''

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

    def launch_ppr_wizard(self, **kwargs):
        ppr_layout = self.layouts.create_ppr_wizard()
        ppr_window = sg.Window('PPR Export Wizard',
                                ppr_layout,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')
        ppr_window['ppr_wizard_image'].update(filename='images/orchz/ppr_wizard.png',
                                              size=(400, 400))
        while True:
            event, values = ppr_window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            elif event == "ppr_generate_catalog":
                self.controller.generate_ppr_catalog()
            elif event == "start_ppr_export":
                # worker thread is stoppable but cannot interact with Tkinter GUI
                # therefore, no stop event is passed until now and 
                # this method is not stoppable but the worker thread is

                stop_event = threading.Event()

                current_task = threading.Thread(target=self.controller.export_ppr_data,
                                                kwargs={'stop_event': stop_event},
                                                daemon=True)
                current_task.start()
            elif event == "regenerate_ppr_summary":
                self.controller.regenerate_ppr_summary()
            else:
                print("Not Implemented:", event)
        ppr_window.close()

    def launch_roi_wizard(self, **kwargs):
        roi_layout = self.layouts.create_roi_wizard(self.controller)
        roi_window = sg.Window('ROI Export Wizard',
                                roi_layout,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')
        roi_window['roi_wizard_image'].update(filename='images/orchz/roi_wizard.png',
                                              size=(400, 400))
        while True:
            event, values = roi_window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            elif event == "roi_wizard_create_rois":
                # worker thread is stoppable but cannot interact with Tkinter GUI
                # therefore, no stop event is passed until now and 
                # this method is not stoppable but the worker thread is

                stop_event = threading.Event()

                current_task = threading.Thread(target=self.controller.roi_wizard_create_rois,
                                                kwargs={'stop_event': stop_event},
                                                daemon=True)
                current_task.start()
            elif event in self.event_mapping:
                ev = self.event_mapping[event]

                # none of these events are stoppable
                if event in values:
                    ev['args']['window'] = window
                    ev['args']['values'] = values[event]
                    ev['args']['event'] = event

                event_dict = {}
                for key in ev['args']:
                    event_dict[key] = ev['args'][key]
                ev['function'](**event_dict)

            else:
                print("Not Implemented:", event)
        roi_window.close()

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
                kwargs[key](**kwargs)

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


