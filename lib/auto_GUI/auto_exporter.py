import pandas as pd
import os
import numpy as np
import pyautogui as pa
import threading
import math

from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ
from lib.auto_GUI.auto_DAT import AutoDAT
from lib.utilities import parse_date
from lib.analysis.laminar_dist import Line
from lib.analysis.laminar_dist import LaminarROI
from lib.file.ROI_reader import ROIFileReader as ROIFileReaderLegacy

from ZDA_Adventure.maps import *
from ZDA_Adventure.tools import *
from ZDA_Adventure.utility import *
from ZDA_Adventure.measure_properties import *


class AutoExporter(AutoPhotoZ):
    def __init__(self, is_export_amp_traces, is_export_snr_traces, is_export_latency_traces, is_export_halfwidth_traces,
                        is_export_traces, is_export_traces_non_polyfit, is_export_sd_traces, is_export_snr_maps, is_export_max_amp_maps, export_trace_prefix, roi_export_option,
                            export_rois_keyword, electrode_export_option, electrode_export_keyword, zero_pad_ids,
                            microns_per_pixel, is_export_by_trial, num_export_trials, headless_mode=False,
                            skip_window_start=94, skip_window_width=70, measure_window_start=94, measure_window_width=70, progress=None, **kwargs):
        super().__init__(**kwargs)
        self.is_export_amp_traces = is_export_amp_traces
        self.is_export_snr_traces = is_export_snr_traces
        self.is_export_latency_traces = is_export_latency_traces
        self.is_export_halfwidth_traces = is_export_halfwidth_traces
        self.is_export_traces = is_export_traces
        self.is_export_traces_non_polyfit = is_export_traces_non_polyfit
        self.is_export_sd_traces = is_export_sd_traces
        self.is_export_snr_maps = is_export_snr_maps
        self.is_export_max_amp_maps = is_export_max_amp_maps
        self.export_trace_prefix = export_trace_prefix
        self.roi_export_option = roi_export_option
        self.export_rois_keyword = export_rois_keyword
        self.electrode_export_option = electrode_export_option
        self.electrode_export_keyword = electrode_export_keyword
        self.zero_pad_ids = zero_pad_ids
        self.debug = False

        # headless settings (instead of storing in PhotoZ or aPhz)
        self.headless_mode = headless_mode
        self.skip_window_width = skip_window_width
        self.skip_window_start = skip_window_start
        self.measure_window_start = measure_window_start
        self.measure_window_width = measure_window_width
        self.last_opened_roi_file = None

        self.progress = progress
        self.stop_event = kwargs.get('stop_event', threading.Event())

        self.ppr_catalog = None  # for PPR export

        self.microns_per_pixel = 1.0
        try:
            self.microns_per_pixel = float(microns_per_pixel)
        except ValueError:
            print("Could not convert " + str(self.microns_per_pixel) + 
                  "microns per pixel to float. Using default value of 1.0")
            
        self.is_export_by_trial = is_export_by_trial
        self.num_export_trials = num_export_trials

    def load_zda_file(self, filename, baseline_correction=True):
        """ Load a ZDA file and return a numpy array """
        if not os.path.exists(filename):
            print("ZDA file not found: " + filename)
            return None
        if not filename.endswith('.zda'):
            print("File is not a ZDA file: " + filename)
            return None
        # TO DO: enable RLI division by default
        data = DataLoader(filename,
                          number_of_points_discarded=0).get_data(rli_division=False)
        tools = Tools()
        data = tools.T_filter(Data=data)
        data = tools.S_filter(Data=data, sigma=1)
        if baseline_correction:
            data = tools.Polynomial(startPt=self.skip_window_start,
                                    numPt=self.skip_window_width,
                                    Data=data)
        
        return data
    
    def load_roi_file(self, filename):
        """ Load an ROI file and return as a list of lists of [x,y] """
        return ROIFileReader(filename).get_roi_list()

    def get_roi_filenames(self, subdir, rec_id, roi_keyword):
        """ Return all files that match the rec_id and the roi_keyword in the subdir folder
         However, roi_files cannot have the trace_type keywords in them 
         Defaults to [None] if no files are found """
        roi_files = []
        for file in os.listdir(subdir):
            if str(rec_id) in file and roi_keyword in file:
                    if 'amp' not in file and 'snr' not in file and 'sd' not in file and \
                        'latency' not in file and 'halfwidth' not in file and 'trace' not in file:
                        roi_files.append(file)

        if len(roi_files) < 1:
            roi_files = [None]
        return roi_files
    
    def get_electrode_filename(self, subdir, rec_id, electrode_keyword):
        """ Return the first file that matches the rec_id and the electrode_keyword in the subdir folder 
        Defaults to None if no files are found """
        for file in os.listdir(subdir):
            if str(rec_id) in file and electrode_keyword in file:
                return file
        return None

    def create_data_map(self):
        data_map = {}
        # Data mapping loop -- locate and organize all zda files into slice, loc, rec structure 
        for subdir, dirs, files in os.walk(self.data_dir):
            date = parse_date(subdir)
            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):
                    rec_id = zda_file.split('.')[0]
                    print("\n", subdir + "/" + zda_file)
                    slic_id, loc_id, _ = [int(x) for x in rec_id.split("_")]

                    if subdir not in data_map:
                        data_map[subdir] = {}
                    if slic_id not in data_map[subdir]:
                        data_map[subdir][slic_id] = {}
                    if loc_id not in data_map[subdir][slic_id]:
                        data_map[subdir][slic_id][loc_id] = {
                            'zda_files': []
                        }
                    data_map[subdir][slic_id][loc_id]['zda_files'].append(subdir + "/" + zda_file)
        return data_map

    def get_export_target_filename(self, subdir, slic_id, loc_id, rec_id, trace_type, roi_prefix):
        """ Return the filename to store the exported trace data in a .dat file """
        slic_id = self.pad_zeros(str(slic_id))
        loc_id = self.pad_zeros(str(loc_id))
        rec_id = self.pad_zeros(str(rec_id))
        target_fn = subdir + "/" + "_".join([self.export_trace_prefix, slic_id, loc_id, rec_id, trace_type, roi_prefix]) 
        target_fn = target_fn.replace(" ", "_")
        return target_fn + ".dat"

    def update_export_map(self, export_map, subdir, slic_id, loc_id, rec_id, trace_type, roi_prefix, filename):
        """ Update the export map with the filename of newly created file"""
        if rec_id not in export_map[subdir][slic_id][loc_id]:
            export_map[subdir][slic_id][loc_id][rec_id] = {}
        if trace_type not in export_map[subdir][slic_id][loc_id][rec_id]:
            export_map[subdir][slic_id][loc_id][rec_id][trace_type] = {}
        export_map[subdir][slic_id][loc_id][rec_id][trace_type][roi_prefix] = filename

    def estimate_total_zda_files(self, data_map):
        """ Estimate the total files to export -- all traces and maps """
        total_files = 0
        for subdir in data_map:
            for slic_id in data_map[subdir]:
                for loc_id in data_map[subdir][slic_id]:
                    total_files += len(data_map[subdir][slic_id][loc_id]['zda_files'])
        return total_files

    def export(self, rebuild_map_only=False):
        """ Export all traces and maps """
        data_map = self.create_data_map()
        export_map = dict(data_map)
        total_files = self.estimate_total_zda_files(data_map)
        self.progress.set_current_total(total_files, unit='ZDA files')

        for subdir in data_map:
            aPhz = None
            if not self.headless_mode:
                aPhz = AutoPhotoZ(data_dir=subdir)
            for slic_id in data_map[subdir]:
                self.export_slice(subdir, slic_id, aPhz, data_map, export_map, rebuild_map_only)
                if self.stop_event.is_set():
                    return
        self.generate_summary_csv(export_map)
        self.progress.complete()

    def export_slice(self, subdir, slic_id, aPhz, data_map, export_map, rebuild_map_only):
        slic_roi_files = [None]
        if self.roi_export_option == 'Slice':
            slic_roi_files = self.get_roi_filenames(subdir, self.pad_zeros(str(slic_id)), self.export_rois_keyword)
        curr_rois = None
        for slice_roi_file in slic_roi_files:
            roi_prefix = ''
            if slice_roi_file is not None:
                roi_prefix = slice_roi_file.split('.')[0]
                if not self.headless_mode:
                    if not rebuild_map_only:
                        aPhz.select_roi_tab()
                        aPhz.open_roi_file(subdir + "/" + slice_roi_file)
                        print("Opened ROI file:", slice_roi_file)
                    else:
                        aPhz.set_last_opened_roi_file(subdir + "/" + slice_roi_file)
                else:
                    if not rebuild_map_only:
                        curr_rois = self.load_roi_file(subdir + "/" + slice_roi_file)
                        print("Opened ROI file:", slice_roi_file)
                    self.last_opened_roi_file = subdir + "/" + slice_roi_file
            if self.stop_event.is_set():
                return

            for loc_id in data_map[subdir][slic_id]:
                self.export_location(curr_rois, subdir, slic_id, loc_id, roi_prefix, aPhz, data_map, export_map, rebuild_map_only)
                if self.stop_event.is_set():
                    return

    def export_location(self, curr_rois, subdir, slic_id, loc_id, roi_prefix, aPhz, data_map, export_map, rebuild_map_only):
        slic_loc_id = self.pad_zeros(str(slic_id)) + "_" + self.pad_zeros(str(loc_id))

        loc_roi_files = [None]
        if self.roi_export_option == 'Slice_Loc':
            loc_roi_files = self.get_roi_filenames(subdir, slic_loc_id, self.export_rois_keyword)
        
        for loc_roi_file in loc_roi_files:
            if loc_roi_file is not None:
                roi_prefix = loc_roi_file.split('.')[0]
                if not self.headless_mode:
                    if not rebuild_map_only:
                        aPhz.select_roi_tab()
                        aPhz.open_roi_file(subdir + "/" + loc_roi_file)
                        print("Opened ROI file:", loc_roi_file)
                    else:
                        aPhz.set_last_opened_roi_file(subdir + "/" + loc_roi_file)
                else:
                    if not rebuild_map_only:
                        curr_rois = self.load_roi_file(subdir + "/" + loc_roi_file)
                        print("Opened ROI file:", loc_roi_file)
                    self.last_opened_roi_file = subdir + "/" + loc_roi_file
            if self.stop_event.is_set():
                return

            for zda_file in data_map[subdir][slic_id][loc_id]['zda_files']:
                if self.headless_mode:
                    self.export_zda_file_headless(curr_rois, subdir, slic_id, loc_id, zda_file, roi_prefix, export_map, rebuild_map_only)
                else:    
                    self.export_zda_file(subdir, slic_id, loc_id, zda_file, roi_prefix, aPhz, export_map, rebuild_map_only)
                if self.stop_event.is_set():
                    return
                
    def check_if_done(self, zda_file):
        # check if this zda file has already been exported and marked manually as done
        if self.ppr_catalog is None:
            return False
        ppr_params = None
        for ppr_key in self.ppr_catalog:
            if os.path.normpath(zda_file) == os.path.normpath(ppr_key):
                ppr_params = self.ppr_catalog[ppr_key]
                break

        if ppr_params is None or ('done' in ppr_params and ppr_params['done'] == 1):
            print("Skipping PPR export for zda file: ", zda_file)
            if ppr_params is None:
                print("Reason: ppr_params is None")
            elif 'done' in ppr_params and ppr_params['done'] == 1:
                print("Reason: ppr_params['done'] == 1")
            self.progress.increment_progress_value(1)
            return True
        return False

    def export_zda_file_headless(self, curr_rois, subdir, slic_id, loc_id, zda_file, roi_prefix, export_map, rebuild_map_only):
        zda_id = zda_file.split('/')[-1].split('.')[0]
        _, _, rec_id = zda_id.split('_')
        rec_id = int(rec_id)

        if self.check_if_done(zda_file):
            return
        
        loaded_zda_arr = None

        if not rebuild_map_only:
            print("\n", zda_file)
            # Trials * height * width * timepoints
            loaded_zda_arr = self.load_zda_file(zda_file)

        rec_roi_files = [None]
        if self.roi_export_option == 'Slice_Loc_Rec':
            slic_loc_rec_id = self.pad_zeros(str(slic_id)) + "_" + self.pad_zeros(str(loc_id)) + "_" + self.pad_zeros(str(rec_id))
            rec_roi_files = self.get_roi_filenames(subdir, slic_loc_rec_id, self.export_rois_keyword)
            print(rec_roi_files)
            print("found roi files for ", slic_loc_rec_id, ": ")

        for rec_roi_file in rec_roi_files:
            if rec_roi_file is not None:
                roi_prefix = rec_roi_file.split('.')[0]
                if not rebuild_map_only:
                    curr_rois = self.load_roi_file(subdir + "/" + rec_roi_file)
                    print("Opened ROI file:", rec_roi_file)
                self.last_opened_roi_file = subdir + "/" + rec_roi_file
            else:
                roi_prefix = ''
            if self.stop_event.is_set():
                return

            trial_loop_iterations = self.num_export_trials if self.is_export_by_trial else 1

            for i_trial in range(trial_loop_iterations):
                roi_prefix2 = roi_prefix
                if len(roi_prefix) < 2:
                    # pull the last opened roi file from aPhz
                    roi_prefix2 = self.last_opened_roi_file
                    if len(roi_prefix2) > 0:
                        roi_prefix2 = roi_prefix2.split('.')[0].split('/')[-1].split('\\')[-1]
                trial_arr = None
                if self.is_export_by_trial:
                    roi_prefix2 += " trial" + str(i_trial + 1)
                    if not rebuild_map_only:
                        trial_arr = loaded_zda_arr[i_trial, :, :, :]
                else:
                    if not rebuild_map_only:
                        trial_arr = np.average(loaded_zda_arr, axis=0)

                # implement PPR export
                if self.ppr_catalog is None:
                    self.export_single_file_headless(subdir, zda_file, i_trial, trial_arr, curr_rois, slic_id, loc_id, rec_id, roi_prefix2, export_map, rebuild_map_only)
                else:
                    ppr_params = None

                    for ppr_key in self.ppr_catalog:
                        if os.path.normpath(zda_file) == os.path.normpath(ppr_key):
                            ppr_params = self.ppr_catalog[ppr_key]
                            print("Found PPR parameters for zda file: ", zda_file)
                            print(ppr_params)
                            break

                    if ppr_params is None:
                        print("No PPR parameters found for zda file: ", zda_file)
                        print(self.ppr_catalog)
                        return
                    
                    # check if the PPR parameters are not Nan before converting to int
                    pulse1_start = ppr_params.get('pulse1_start', float('nan'))
                    pulse1_width = ppr_params.get('pulse1_width', float('nan'))
                    pulse2_start = ppr_params.get('pulse2_start', float('nan'))
                    pulse2_width = ppr_params.get('pulse2_width', float('nan'))
                    baseline_start = ppr_params.get('baseline_start', float('nan'))
                    baseline_width = ppr_params.get('baseline_width', float('nan'))
                    if not math.isnan(ppr_params['pulse1_start']):
                        pulse1_start = int(ppr_params['pulse1_start'])
                    if not math.isnan(ppr_params['pulse1_width']):
                        pulse1_width = int(ppr_params['pulse1_width'])
                    if not math.isnan(ppr_params['pulse2_start']):
                        pulse2_start = int(ppr_params['pulse2_start'])
                    if not math.isnan(ppr_params['pulse2_width']):
                        pulse2_width = int(ppr_params['pulse2_width'])
                    if not math.isnan(ppr_params['baseline_start']):
                        baseline_start = int(ppr_params['baseline_start'])
                    if not math.isnan(ppr_params['baseline_width']):
                        baseline_width = int(ppr_params['baseline_width'])
                    print("PPR parameters: ", pulse1_start, pulse1_width, pulse2_start, pulse2_width, baseline_start, baseline_width)
                    
                    if not rebuild_map_only:
                        # set baseline window
                        need_to_reload_zda = ((baseline_start != self.skip_window_start) or \
                                              (baseline_width != self.skip_window_width))
                        self.set_polynomial_skip_window_headless(baseline_start, skip_width=baseline_width)
                        # set measure window 1
                        self.set_measure_window_headless(pulse1_start, pulse1_width)
                        # reload zda file and reselect trial if baseline changed
                        if need_to_reload_zda:
                            loaded_zda_arr = self.load_zda_file(zda_file)
                            if self.is_export_by_trial:
                                trial_arr = loaded_zda_arr[i_trial, :, :, :]
                            else:
                                trial_arr = np.average(loaded_zda_arr, axis = 0)
                    self.export_single_file_headless(subdir, zda_file, i_trial, trial_arr, curr_rois, slic_id, loc_id, rec_id, roi_prefix2 + " pulse1", 
                                                     export_map, rebuild_map_only, ppr_pulse=1)

                    # set measure window 2 if it is entered
                    if (not math.isnan(pulse2_start)) or (not math.isnan(pulse2_width)):
                        if not rebuild_map_only:
                            # don't need to reselect 
                            self.set_measure_window_headless(pulse2_start, pulse2_width)
                        self.export_single_file_headless(subdir, zda_file, i_trial, trial_arr, curr_rois, slic_id, loc_id, rec_id, roi_prefix2 + " pulse2", export_map, rebuild_map_only, ppr_pulse=2)
                
                if self.stop_event.is_set():
                    return
            self.progress.increment_progress_value(1)

    def set_polynomial_skip_window_headless(self, skip_start, skip_width=None):
        self.skip_window_start = skip_start
        self.skip_window_width = skip_width

    def set_measure_window_headless(self, start, width):
        self.measure_window_start = start
        self.measure_window_width = width

    def export_zda_file(self, subdir, slic_id, loc_id, zda_file, roi_prefix, aPhz, export_map, rebuild_map_only):
        zda_id = zda_file.split('/')[-1].split('.')[0]
        _, _, rec_id = zda_id.split('_')
        rec_id = int(rec_id)

        if self.check_if_done(zda_file):
            return

        if not rebuild_map_only:
            print("\n", zda_file)
            aPhz.open_zda_file(zda_file)

        rec_roi_files = [None]
        if self.roi_export_option == 'Slice_Loc_Rec':
            slic_loc_rec_id = self.pad_zeros(str(slic_id)) + "_" + self.pad_zeros(str(loc_id)) + "_" + self.pad_zeros(str(rec_id))
            rec_roi_files = self.get_roi_filenames(subdir, slic_loc_rec_id, self.export_rois_keyword)
            print(rec_roi_files)
            print("found roi files for ", slic_loc_rec_id, ": ")

        for rec_roi_file in rec_roi_files:
            if rec_roi_file is not None:
                roi_prefix = rec_roi_file.split('.')[0]
                if not rebuild_map_only:
                    aPhz.select_roi_tab()
                    aPhz.open_roi_file(subdir + "/" + rec_roi_file)
                    print("Opened ROI file:", rec_roi_file)
                else:
                    aPhz.set_last_opened_roi_file(subdir + "/" + rec_roi_file)
            else:
                roi_prefix = ''
            if self.stop_event.is_set():
                return

            trial_loop_iterations = self.num_export_trials if self.is_export_by_trial else 1

            for i_trial in range(trial_loop_iterations):
                roi_prefix2 = roi_prefix
                if len(roi_prefix) < 2:
                    # pull the last opened roi file from aPhz
                    roi_prefix2 = aPhz.get_last_opened_roi_file()
                    if len(roi_prefix2) > 0:
                        roi_prefix2 = roi_prefix2.split('.')[0].split('/')[-1].split('\\')[-1]
                if self.is_export_by_trial:
                    roi_prefix2 += " trial" + str(i_trial + 1)
                    if not rebuild_map_only:
                        ad = AutoDAT(datadir=subdir, processing_sleep_time=14)
                        ad.increment_trial()
                
                # implement PPR export 
                if self.ppr_catalog is None:
                    self.export_single_file(subdir, slic_id, loc_id, rec_id, roi_prefix2, aPhz, export_map, rebuild_map_only)
                else:
                    ppr_params = None

                    for ppr_key in self.ppr_catalog:
                        if os.path.normpath(zda_file) == os.path.normpath(ppr_key):
                            ppr_params = self.ppr_catalog[ppr_key]
                            print("Found PPR parameters for zda file: ", zda_file)
                            print(ppr_params)
                            break

                    if ppr_params is None:
                        print("No PPR parameters found for zda file: ", zda_file)
                        print(self.ppr_catalog)
                        return
                    
                    # check if the PPR parameters are not Nan before converting to int
                    pulse1_start = ppr_params.get('pulse1_start', float('nan'))
                    pulse1_width = ppr_params.get('pulse1_width', float('nan'))
                    pulse2_start = ppr_params.get('pulse2_start', float('nan'))
                    pulse2_width = ppr_params.get('pulse2_width', float('nan'))
                    baseline_start = ppr_params.get('baseline_start', float('nan'))
                    baseline_width = ppr_params.get('baseline_width', float('nan'))
                    if not math.isnan(ppr_params['pulse1_start']):
                        pulse1_start = int(ppr_params['pulse1_start'])
                    if not math.isnan(ppr_params['pulse1_width']):
                        pulse1_width = int(ppr_params['pulse1_width'])
                    if not math.isnan(ppr_params['pulse2_start']):
                        pulse2_start = int(ppr_params['pulse2_start'])
                    if not math.isnan(ppr_params['pulse2_width']):
                        pulse2_width = int(ppr_params['pulse2_width'])
                    if not math.isnan(ppr_params['baseline_start']):
                        baseline_start = int(ppr_params['baseline_start'])
                    if not math.isnan(ppr_params['baseline_width']):
                        baseline_width = int(ppr_params['baseline_width'])
                    print("PPR parameters: ", pulse1_start, pulse1_width, pulse2_start, pulse2_width, baseline_start, baseline_width)
                    
                    if not rebuild_map_only:
                        # set baseline window
                        aPhz.set_polynomial_skip_window(baseline_start, skip_width=baseline_width)
                        # set measure window 1
                        aPhz.set_measure_window(pulse1_start, pulse1_width)
                    self.export_single_file(subdir, slic_id, loc_id, rec_id, roi_prefix2 + " pulse1", aPhz, export_map, rebuild_map_only, ppr_pulse=1)

                    # set measure window 2 if it is entered
                    if (not math.isnan(pulse2_start)) or (not math.isnan(pulse2_width)):
                        if not rebuild_map_only:
                            aPhz.set_measure_window(pulse2_start, pulse2_width)
                        self.export_single_file(subdir, slic_id, loc_id, rec_id, roi_prefix2 + " pulse2", aPhz, export_map, rebuild_map_only, ppr_pulse=2)
                
                if self.stop_event.is_set():
                    return
            self.progress.increment_progress_value(1)

    def export_single_file_headless(self, subdir, zda_file, i_trial, zda_arr, rois, slic_id, loc_id, rec_id, roi_prefix2, export_map, rebuild_map_only, ppr_pulse=None):
        # first, build set of ROI traces 
        roi_traces = []
        if not rebuild_map_only:
            for roi in rois:
                zda_arr_ = zda_arr
                if len(zda_arr.shape) == 3:
                    # should be 4 D to use TraceSelector: trials * height * width * timepoints
                    # make trials dim have length 1
                    zda_arr_ = zda_arr.reshape(1, zda_arr.shape[0], zda_arr.shape[1], zda_arr.shape[2])
                trace = TraceSelector(zda_arr_).get_trace_from_roi(roi)
                roi_traces.append(trace)

            # run measurements if amp, snr, latency, halfwidth are checked
            trace_measurements = []
            if any([self.is_export_amp_traces, self.is_export_halfwidth_traces,
                    self.is_export_latency_traces, self.is_export_snr_traces,
                    self.is_export_sd_traces]):
                for tr in roi_traces:
                    tp = TraceProperties(tr, 
                                        self.measure_window_start,
                                        self.measure_window_width,
                                        0.5,  # assume 2000 Hz
                                        )
                    trace_measurements.append(tp)

        """ exports a single file's traces and maps based on settings """
        if self.is_export_amp_traces:
            amp_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix2)
            if not rebuild_map_only:
                arr = [tp.get_max_amp() for tp in trace_measurements]
                self.save_trace_value_file(amp_filename, arr)
                print("\tExported:", amp_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix2, amp_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_snr_traces:
            snr_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix2)
            if not rebuild_map_only:
                arr = [tp.get_SNR() for tp in trace_measurements]
                self.save_trace_value_file(snr_filename, arr)
                print("\tExported:", snr_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix2, snr_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_latency_traces:
            lat_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix2)
            if not rebuild_map_only:
                arr = [tp.get_half_amp_latency() for tp in trace_measurements]
                self.save_trace_value_file(lat_filename, arr)
                print("\tExported:", lat_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix2, lat_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_halfwidth_traces:
            hw_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix2)
            if not rebuild_map_only:
                arr = [tp.get_half_width() for tp in trace_measurements]
                self.save_trace_value_file(hw_filename, arr)
                print("\tExported:", hw_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix2, hw_filename)

        if self.is_export_sd_traces:
            sd_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'sd', roi_prefix2)
            if not rebuild_map_only:
                arr = [tp.get_SD() for tp in trace_measurements]
                self.save_trace_value_file(sd_filename, arr)
                print("\tExported:", sd_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'sd', roi_prefix2, sd_filename)
                        
        if self.stop_event.is_set():
            return
        if self.is_export_traces:
            trace_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix2)
            if not rebuild_map_only:
                self.save_traces_file(trace_filename, roi_traces)
                print("\tExported:", trace_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix2, trace_filename)
        if self.stop_event.is_set():
            return
        
        if self.is_export_traces_non_polyfit:
            trace_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'trace_non_polyfit', roi_prefix2)
            if not rebuild_map_only:
                zda_arr_no_baseline = self.load_zda_file(zda_file, baseline_correction=False)
                if self.is_export_by_trial:
                    zda_arr_no_baseline = zda_arr_no_baseline[i_trial, :, :, :]
                else:
                    zda_arr_no_baseline = np.average(zda_arr_no_baseline, axis = 0)
                roi_traces_no_baseline = []
                for roi in rois:
                    zda_arr_no_baseline_ = zda_arr_no_baseline
                    if len(zda_arr_no_baseline_.shape) == 3:
                        # should be 4 D to use TraceSelector: trials * height * width * timepoints
                        # make trials dim have length 1
                        zda_arr_no_baseline_ = zda_arr_no_baseline_.reshape(1, zda_arr_no_baseline_.shape[0], zda_arr_no_baseline_.shape[1], zda_arr_no_baseline_.shape[2])
                    trace = TraceSelector(zda_arr_no_baseline_).get_trace_from_roi(roi)
                    roi_traces_no_baseline.append(trace)
                self.save_traces_file(trace_filename, roi_traces_no_baseline)
                print("\tExported:", trace_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'trace_non_polyfit', roi_prefix2, trace_filename)

        if self.stop_event.is_set():
            return
        

        # if either map setting, need to make measurements for every pixel
        if not rebuild_map_only:
            if any([self.is_export_max_amp_maps, self.is_export_snr_maps]):
                tp_map = []
                for i in range(zda_arr.shape[0]):
                    tp_map.append([])
                    for j in range(zda_arr.shape[1]):
                        tp_map[i].append([])
                        tp = TraceProperties(zda_arr[i, j, :], 
                                        self.measure_window_start,
                                        self.measure_window_width,
                                        0.5,  # assume 2000 Hz
                                        )
                        tp_map[i][j] = tp

        if self.is_export_max_amp_maps:
            amp_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix2)
            if not rebuild_map_only:
                arr = np.array(
                    [[tp.get_max_amp() for tp in tp_row] 
                     for tp_row in tp_map]
                )
                self.save_array_file(amp_array_filename, arr)
                print("\tExported:", amp_array_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix2, amp_array_filename)
        
        if self.stop_event.is_set():
            return
        if self.is_export_snr_maps:
            snr_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix2)
            if not rebuild_map_only:
                arr = np.array(
                    [[tp.get_SNR() for tp in tp_row]
                     for tp_row in tp_map]
                )
                self.save_array_file(snr_array_filename, arr)
                print("\tExported:", snr_array_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix2, snr_array_filename)

    def export_single_file(self, subdir, slic_id, loc_id, rec_id, roi_prefix2, aPhz, export_map, rebuild_map_only, ppr_pulse=None):
        if self.is_export_amp_traces:
            amp_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_maxamp_trace_value()
                aPhz.save_trace_values(amp_filename)
                print("\tExported:", amp_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix2, amp_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_snr_traces:
            snr_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_SNR_trace_value()
                aPhz.save_trace_values(snr_filename)
                print("\tExported:", snr_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix2, snr_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_latency_traces:
            lat_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_latency_trace_value()
                aPhz.save_trace_values(lat_filename)
                print("\tExported:", lat_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix2, lat_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_halfwidth_traces:
            hw_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_half_width_trace_value()
                aPhz.save_trace_values(hw_filename)
                print("\tExported:", hw_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix2, hw_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_traces:
            trace_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix2)
            if not rebuild_map_only:
                aPhz.save_current_traces(trace_filename, go_to_tab=True)
                print("\tExported:", trace_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix2, trace_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_traces_non_polyfit:
            trace_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'trace_non_polyfit', roi_prefix2)
            if not rebuild_map_only:
                aPhz.change_baseline_correction(polynomial=False)
                aPhz.save_current_traces(trace_filename, go_to_tab=True)
                print("\tExported:", trace_filename)
                aPhz.change_baseline_correction(polynomial=True)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'trace_non_polyfit', roi_prefix2, trace_filename)
        if self.is_export_sd_traces:
            sd_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'sd', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_sd_trace_value()
                aPhz.save_trace_values(sd_filename)
                print("\tExported:", sd_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'sd', roi_prefix2, sd_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_max_amp_maps:
            amp_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_MaxAmp_array()
                aPhz.save_background(filename=amp_array_filename)
                print("\tExported:", amp_array_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix2, amp_array_filename)
        if self.stop_event.is_set():
            return
        if self.is_export_snr_maps:
            snr_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix2)
            if not rebuild_map_only:
                aPhz.select_SNR_array()
                aPhz.save_background(filename=snr_array_filename)
                print("\tExported:", snr_array_filename)
            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix2, snr_array_filename)

    def add_ppr_catalog(self, ppr_catalog):
        """ ppr catalog is a dict which maps zda files 
        to their corresponding ppr data """
        self.ppr_catalog = ppr_catalog

    def regenerate_summary_csv(self):
        self.export(rebuild_map_only=True)

    def read_array_file(self, filename):
        """ Read in a .dat file and return the numpy array """
        data_arr = pd.read_csv(filename,
                                sep='\t',
                                header=None,
                                names=['Index',  'Value'])
        data_arr = np.array(data_arr['Value']).reshape((80, 80))
        return data_arr

    def read_trace_value_file(self, filename):
        """ Read in a .dat file and return the numpy array """
        return pd.read_csv(filename, sep="\t", header=None, names=['ROI', 'Value'])
    
    def save_array_file(self, filename, arr):
        """ flatten 80x80 to 6400 values and write to array file
            matching format of read_array_file() method (PhotoZ .dat)"""
        # flatten arr
        idx = 1
        with open(filename, mode='w') as f:
            for i in range(arr.shape[1]):
                for j in range(arr.shape[0]):
                    f.write(str(idx) + "\t" + str(arr[j, i]) + "\n")
                    idx += 1

    def save_trace_value_file(self, filename, arr):
        with open(filename, "w") as f:
            for i in range(len(arr)):
                f.write(str(i+1) + "\t" + str(arr[i]) + "\n")

    def save_traces_file(self, filename, traces):
        """ Given a list of traces, save them to columns
        of a .dat file in tab-separated columns with headers
        "Pt" then "ROI1", ROI2, ... """
        if len(traces) < 1:
            return
        with open(filename, "w") as f:
            n_pts = len(traces[0])
            n_rois = len(traces)
            f.write("Pt\t" + 
                    "\t".join(["ROI" + str(i+1) for i in range(n_rois)]) + 
                    "\n")
            for i in range(n_pts):
                f.write(str(i+1) + '\t' + 
                        '\t'.join([str(traces[j][i]) for j in range(n_rois)]) + 
                        '\n')

    def type_is_trace_value(self, trace_type):
        return 'array' not in trace_type and 'trace' != trace_type and 'trace_non_polyfit' != trace_type

    def generate_summary_csv(self, export_map):
        """ Generate a summary csv file with the metrics. Each row identified by date, slice, loc, rec, roi.
            Each column is a metric type: amp, snr, latency, halfwidth, trace, snr_map, max_amp_map 
            Use pandas dataframe, read in text files whose filenames are stored in the export_map 
            
            export_map: dict with keys: subdir, slic_id, loc_id, rec_id, trace_type, roi_prefix, filename"""
        csv_filename = self.data_dir + "/export_summary.csv"
        data_df_dict = {}
        for subdir in export_map:
            date = parse_date(subdir)
            for slic_id in export_map[subdir]:
                stim_file = None
                if self.electrode_export_option == 'Slice':
                    stim_file = self.get_electrode_filename(subdir, self.pad_zeros(str(slic_id)), 
                                                            self.electrode_export_keyword)

                for loc_id in export_map[subdir][slic_id]:

                    slic_loc_id = self.pad_zeros(str(slic_id)) + "_" + self.pad_zeros(str(loc_id))
                    if self.electrode_export_option == 'Slice_Loc':
                        stim_file = self.get_electrode_filename(subdir, slic_loc_id, 
                                                                self.electrode_export_keyword)
                        
                    for rec_id in export_map[subdir][slic_id][loc_id]:

                        rec_slic_loc_id = slic_loc_id + "_" + self.pad_zeros(str(rec_id))
                        if self.electrode_export_option == 'Slice_Loc_Rec':
                            stim_file = self.get_electrode_filename(subdir, rec_slic_loc_id, 
                                                                    self.electrode_export_keyword)

                        tmp_dict = {}
                        for trace_type in export_map[subdir][slic_id][loc_id][rec_id]:
                            if rec_id == 'zda_files':
                                continue
                            for roi_prefix in export_map[subdir][slic_id][loc_id][rec_id][trace_type]:
                                filename = export_map[subdir][slic_id][loc_id][rec_id][trace_type][roi_prefix]
                                if not os.path.exists(filename):
                                    data = None
                                if self.type_is_trace_value(trace_type):
                                    try:
                                        data = self.read_trace_value_file(filename)
                                    except FileNotFoundError:
                                        print("File not found:", filename, "Cannot include in summary csv.")
                                        data = None
                                    if data is not None:
                                        print("Including data from file:", filename)
                                else:
                                    # otherwise, just put the filename in the column
                                    data = filename
                                if roi_prefix not in tmp_dict:
                                    tmp_dict[roi_prefix] = {}
                                tmp_dict[roi_prefix][trace_type] = data
                                
                        # unload the tmp_dict into the data_df_dict in the correct order for this recording
                        for roi_prefix in tmp_dict:
                            n = None
                            rois = []
                            for trace_type in tmp_dict[roi_prefix]:
                                data = tmp_dict[roi_prefix][trace_type]
                                if data is not None and type(data) != str:
                                    n = len(data['Value'])
                                    if 'ROI' not in data_df_dict:
                                        data_df_dict['ROI'] = []
                                    if trace_type not in data_df_dict:
                                        data_df_dict[trace_type] = []
                                    data_df_dict[trace_type] += list(data['Value'].values)
                                    print("Adding data for roi: ", roi_prefix, " trace_type: ", trace_type)
                                    rois = list(data['ROI'].values)

                            # if we have a stim file, also find the ROI file and calculate distance to stim
                            distances = []
                            x_centers = []
                            y_centers = []
                            roi_file = None
                            if roi_prefix is not None and len(roi_prefix) > 0:
                                roi_file = subdir + "/" + roi_prefix.split(" ")[0] + ".dat"
                                if os.path.exists(roi_file):
                                    # load rois 
                                    rois_ = ROIFileReader(roi_file).get_roi_list()
                                    rois_ = [LaminarROI(r, input_diode_numbers=True)
                                            for r in rois_]
                                    rois_points = [roi.get_points() for roi in rois_]

                                    if stim_file is not None:
                                        
                                        stim_point = ROIFileReaderLegacy(subdir + "/" + stim_file).get_roi_list()
                                        stim_point = LaminarROI(stim_point[0], input_diode_numbers=True).get_points()[0]
                                        
                                        # calculate distance from electrode
                                        distances = [Line(stim_point, roi[0]).get_length() * self.microns_per_pixel
                                                    if len(roi) > 0 
                                                    else None
                                                    for roi in rois_points]
                                    elif 'Stim_Distance' in data_df_dict:
                                        print("Warning: stim file not found for roi: ", roi_prefix, "Date",
                                                date, "Slice", slic_id, "Location", loc_id, "Recording", rec_id,
                                                " but Stim_Distance column already exists.")

                                    # x, y pixel locations of center of each roi
                                    centers = [roi.get_center() for roi in rois_]
                                    x_centers = [c[0] for c in centers]
                                    y_centers = [c[1] for c in centers]

                                    
                            if 'Stim_Distance' not in data_df_dict:
                                data_df_dict['Stim_Distance'] = []
                            data_df_dict['Stim_Distance'] += distances
                            if 'X_Center' not in data_df_dict:
                                data_df_dict['X_Center'] = []
                            if 'Y_Center' not in data_df_dict:
                                data_df_dict['Y_Center'] = []
                            if n is None:
                                n = len(data_df_dict['Stim_Distance'])
                            if n is None or n < 1:
                                n = 1  # placeholder row to insert any non-DAT data
                                del data_df_dict['Stim_Distance']  # Stim_Distance was empty if this line was reached
                                del data_df_dict['X_Center']
                                del data_df_dict['Y_Center']
                                if 'ROI_File' not in data_df_dict:
                                    data_df_dict['ROI_File'] = []
                                data_df_dict['ROI_File'].append(roi_file)
                            else:
                                data_df_dict['X_Center'] += x_centers
                                data_df_dict['Y_Center'] += y_centers
                                print("Adding " + str(x_centers) + " centers for rois: ", roi_prefix)

                            print("Adding n = ", n, " rows")

                            if 'Date' not in data_df_dict:
                                data_df_dict['ROI_Set'] = []
                                if len(rois) > 0:
                                    data_df_dict['ROI'] = []
                                data_df_dict['Date'] = []
                                data_df_dict['Slice'] = []
                                data_df_dict['Location'] = []
                                data_df_dict['Recording'] = []
                                
                            data_df_dict['ROI_Set'] += [roi_prefix for _ in range(n)]
                            if len(rois) > 0:
                                data_df_dict['ROI'] += rois
                            data_df_dict['Date'] += [date for _ in range(n)]
                            data_df_dict['Slice'] += [slic_id for _ in range(n)]
                            data_df_dict['Location'] += [loc_id for _ in range(n)]
                            data_df_dict['Recording'] += [rec_id for _ in range(n)]

                            for trace_type in tmp_dict[roi_prefix]:
                                if trace_type in ['trace', 'snr_array', 'amp_array', 'trace_non_polyfit']:
                                    print("Adding filename for roi: ", roi_prefix, " trace_type: ", trace_type)
                                    if trace_type not in data_df_dict:
                                        data_df_dict[trace_type] = []
                                    data = tmp_dict[roi_prefix][trace_type]

                                    # replace spaces with underscores in the file name but not the file path
                                    data_end_filename = data.split("/")[-1]
                                    data = data.replace(data_end_filename, data_end_filename.replace(" ", "_"))
                                    data_df_dict[trace_type] += [data for _ in range(n)]

                            # check if lengths are equal in the data_df_dict
                            for k in data_df_dict:
                                if len(data_df_dict[k]) != len(data_df_dict['Date']) and k != "Stim_Distance":
                                    if self.debug:
                                        raise Exception("Unequal lengths in data_df_dict: ", 
                                                k, len(data_df_dict[k]), len(data_df_dict['Date']),
                                                "Date: ", date, slic_id, loc_id, rec_id, "\n # ROIs in ROI file: ", len(rois), "(roi_prefix: ", roi_prefix, ")")

        key_delete = []    
        unequal_flag = False
        for k in data_df_dict:
            if len(data_df_dict[k]) != len(data_df_dict['Date']):
                unequal_flag = True
                if len(data_df_dict[k]) == 0:
                    key_delete.append(k)
                else:
                    print("Unequal dict list lengths:")
                    print([(len(data_df_dict[k]),k) for k in data_df_dict])
        for k in key_delete:
            del data_df_dict[k]
            print("Deleted empty column: ", k)

        if unequal_flag:
            # try removing just x and y center columns
            if 'X_Center' in data_df_dict:
                del data_df_dict['X_Center']
            if 'Y_Center' in data_df_dict:
                del data_df_dict['Y_Center']

        if (not 'Date' in data_df_dict) or len(data_df_dict['Date']) < 1:
            print("No data was selected for any roi. Cannot create summary csv.")
        else:
            df = pd.DataFrame(data_df_dict)
            try:
                df.to_csv(csv_filename, index=False)
                pa.alert("Exported summary csv to: " + csv_filename + "\n Opening file now.")
                os.startfile(csv_filename)
            except PermissionError:
                pa.alert("Permission error. Do you have " + csv_filename + " open? Please close and then click ok.")
                df.to_csv(csv_filename, index=False)  

    def pad_zeros(self, x, n_digits=2):
        """ Pad zeros to the front of the string integer IF it is enabled """
        if not self.zero_pad_ids:
            return x
        return '0' * (n_digits - len(str(x))) + str(x)
        
                            

                    
