import pandas as pd
import os
import numpy as np
import pyautogui as pa

from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ
from lib.auto_GUI.auto_DAT import AutoDAT
from lib.utilities import parse_date
from lib.analysis.laminar_dist import * 
from lib.file.ROI_reader import ROIFileReader


class AutoExporter(AutoPhotoZ):
    def __init__(self, is_export_amp_traces, is_export_snr_traces, is_export_latency_traces, is_export_halfwidth_traces,
                        is_export_traces, is_export_snr_maps, is_export_max_amp_maps, export_trace_prefix, roi_export_option,
                            export_rois_keyword, electrode_export_option, electrode_export_keyword, zero_pad_ids,
                            microns_per_pixel, is_export_by_trial, num_export_trials, **kwargs):
        super().__init__(**kwargs)
        self.is_export_amp_traces = is_export_amp_traces
        self.is_export_snr_traces = is_export_snr_traces
        self.is_export_latency_traces = is_export_latency_traces
        self.is_export_halfwidth_traces = is_export_halfwidth_traces
        self.is_export_traces = is_export_traces
        self.is_export_snr_maps = is_export_snr_maps
        self.is_export_max_amp_maps = is_export_max_amp_maps
        self.export_trace_prefix = export_trace_prefix
        self.roi_export_option = roi_export_option
        self.export_rois_keyword = export_rois_keyword
        self.electrode_export_option = electrode_export_option
        self.electrode_export_keyword = electrode_export_keyword
        self.zero_pad_ids = zero_pad_ids

        self.microns_per_pixel = 1.0
        try:
            self.microns_per_pixel = float(microns_per_pixel)
        except ValueError:
            print("Could not convert " + str(self.microns_per_pixel) + 
                  "microns per pixel to float. Using default value of 1.0")
            
        self.is_export_by_trial = is_export_by_trial
        self.num_export_trials = num_export_trials

    def get_roi_filenames(self, subdir, rec_id, roi_keyword):
        """ Return all files that match the rec_id and the roi_keyword in the subdir folder
         However, roi_files cannot have the trace_type keywords in them 
         Defaults to [None] if no files are found """
        roi_files = []
        for file in os.listdir(subdir):
            if str(rec_id) in file and roi_keyword in file:
                    if 'amp' not in file and 'snr' not in file and \
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
        return subdir + "/" + "_".join([self.export_trace_prefix, slic_id, loc_id, rec_id, trace_type, roi_prefix]) + ".dat"

    def update_export_map(self, export_map, subdir, slic_id, loc_id, rec_id, trace_type, roi_prefix, filename):
        """ Update the export map with the filename of newly created file"""
        if rec_id not in export_map[subdir][slic_id][loc_id]:
            export_map[subdir][slic_id][loc_id][rec_id] = {}
        if trace_type not in export_map[subdir][slic_id][loc_id][rec_id]:
            export_map[subdir][slic_id][loc_id][rec_id][trace_type] = {}
        export_map[subdir][slic_id][loc_id][rec_id][trace_type][roi_prefix] = filename

    def export(self, rebuild_map_only=False):
        """ Export all traces and maps """
        data_map = self.create_data_map()
        export_map = dict(data_map)

        # Export traces loop
        for subdir in data_map:
            aPhz = AutoPhotoZ(data_dir=subdir)
            
            for slic_id in data_map[subdir]:
                slic_roi_files = [None]
                if self.roi_export_option == 'Slice':
                    slic_roi_files = self.get_roi_filenames(subdir, self.pad_zeros(str(slic_id)), 
                                                            self.export_rois_keyword)

                # loop over all slice rois if any
                for slice_roi_file in slic_roi_files:
                    roi_prefix = ''
                    if slice_roi_file is not None:
                        roi_prefix = slice_roi_file.split('.')[0]
                        if not rebuild_map_only:
                            aPhz.select_roi_tab()
                            aPhz.open_roi_file(subdir + "/" + slice_roi_file)
                            print("Opened ROI file:", slice_roi_file)

                    for loc_id in data_map[subdir][slic_id]:
                        slic_loc_id = self.pad_zeros(str(slic_id)) + "_" + self.pad_zeros(str(loc_id))

                        loc_roi_files = [None]
                        if self.roi_export_option == 'Slice_Loc':
                            loc_roi_files = self.get_roi_filenames(subdir, slic_loc_id, self.export_rois_keyword)

                        # loop over all location rois if any
                        for loc_roi_file in loc_roi_files:
                            if loc_roi_file is not None:
                                roi_prefix = loc_roi_file.split('.')[0]
                                if not rebuild_map_only:
                                    aPhz.select_roi_tab()
                                    aPhz.open_roi_file(subdir + "/" + loc_roi_file)
                                    print("Opened ROI file:", loc_roi_file)

                            for zda_file in data_map[subdir][slic_id][loc_id]['zda_files']:

                                zda_id = zda_file.split('/')[-1].split('.')[0]
                                _, _, rec_id = zda_id.split('_')
                                rec_id = int(rec_id)

                                # open zda files
                                if not rebuild_map_only:
                                    print("\n", zda_file)
                                    aPhz.open_zda_file(zda_file)
                                
                                rec_roi_files = [None]
                                if self.roi_export_option == 'Slice_Loc_Rec':
                                    slic_loc_rec_id = slic_loc_id + "_" + self.pad_zeros(str(rec_id))
                                    rec_roi_files = self.get_roi_filenames(subdir, slic_loc_rec_id, 
                                                                           self.export_rois_keyword)
                                    print(rec_roi_files)
                                    print("found roi files for ", slic_loc_rec_id, ": ")

                                # loop over all recording rois if any
                                for rec_roi_file in rec_roi_files:
                                    if rec_roi_file is not None:
                                        roi_prefix = rec_roi_file.split('.')[0]
                                        if not rebuild_map_only:
                                            aPhz.select_roi_tab()
                                            aPhz.open_roi_file(subdir + "/" + rec_roi_file)
                                            print("Opened ROI file:", rec_roi_file)
                                    else:
                                        roi_prefix = ''

                                    trial_loop_iterations = self.num_export_trials
                                    if not self.is_export_by_trial:
                                        trial_loop_iterations = 1

                                    for i_trial in trial_loop_iterations:
                                        roi_prefix2 = roi_prefix
                                        if self.is_export_by_trial:
                                            roi_prefix2 += "_trial" + str(i_trial)
                                            ad = AutoDAT(data_dir=subdir, processing_sleep_time=14)
                                            ad.increment_trial()

                                        if self.is_export_amp_traces:
                                            amp_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.select_maxamp_trace_value()
                                                aPhz.save_trace_values(amp_filename)
                                                print("\tExported:", amp_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix2, amp_filename)
                                        if self.is_export_snr_traces:
                                            snr_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.select_SNR_trace_value()
                                                aPhz.save_trace_values(snr_filename)
                                                print("\tExported:", snr_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix2, snr_filename)
                                        if self.is_export_latency_traces:
                                            lat_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.select_latency_trace_value()
                                                aPhz.save_trace_values(lat_filename)
                                                print("\tExported:", lat_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix2, lat_filename)
                                        if self.is_export_halfwidth_traces:
                                            hw_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.select_half_width_trace_value()
                                                aPhz.save_trace_values(hw_filename)
                                                print("\tExported:", hw_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix2, hw_filename)
                                        if self.is_export_traces:
                                            trace_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.save_current_traces(trace_filename, go_to_tab=True)
                                                print("\tExported:", trace_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix2, trace_filename)
                                        if self.is_export_max_amp_maps:
                                            amp_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.select_MaxAmp_array()
                                                aPhz.save_background(filename=amp_array_filename)
                                                print("\tExported:", amp_array_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix2, amp_array_filename)
                                        if self.is_export_snr_maps:
                                            snr_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix2)
                                            if not rebuild_map_only:
                                                aPhz.select_SNR_array()
                                                aPhz.save_background(filename=snr_array_filename)
                                                print("\tExported:", snr_array_filename)
                                            self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix2, snr_array_filename)

        self.generate_summary_csv(export_map)

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

    def type_is_trace_value(self, trace_type):
        return 'array' not in trace_type and 'trace' != trace_type

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

                            if n is None:
                                print("No trace value data was selected for " + roi_prefix + ": " + trace_type + ". Cannot include in summary csv.")
                                continue

                            # if we have a stim file, also find the ROI file and calculate distance to stim
                            distances = [None for _ in range(n)]
                            if stim_file is not None and roi_prefix is not None:
                                roi_file = subdir + "/" + roi_prefix + ".dat"
                                if os.path.exists(roi_file):
                                    # load rois 
                                    rois_ = ROIFileReader(roi_file).get_roi_list()
                                    rois_ = [LaminarROI(r, input_diode_numbers=True).get_points()
                                            for r in rois_]
                                    
                                    stim_point = ROIFileReader(subdir + "/" + stim_file).get_roi_list()
                                    stim_point = LaminarROI(stim_point[0], input_diode_numbers=True).get_points()[0]
                                    
                                    # calculate distance from electrode
                                    distances = [Line(stim_point, roi[0]).get_length() * self.microns_per_pixel
                                                if len(roi) > 0 
                                                else None
                                                for roi in rois_]
                            if 'Stim_Distance' not in data_df_dict:
                                data_df_dict['Stim_Distance'] = []
                            data_df_dict['Stim_Distance'] += distances
                            

                            if 'Date' not in data_df_dict:
                                data_df_dict['ROI_Set'] = []
                                data_df_dict['Date'] = []
                                data_df_dict['Slice'] = []
                                data_df_dict['Location'] = []
                                data_df_dict['Recording'] = []
                                
                            data_df_dict['ROI_Set'] += [roi_prefix for _ in range(n)]
                            data_df_dict['ROI'] += rois
                            data_df_dict['Date'] += [date for _ in range(n)]
                            data_df_dict['Slice'] += [slic_id for _ in range(n)]
                            data_df_dict['Location'] += [loc_id for _ in range(n)]
                            data_df_dict['Recording'] += [rec_id for _ in range(n)]

                            for trace_type in tmp_dict[roi_prefix]:
                                if trace_type in ['trace', 'snr_array', 'amp_array']:
                                    print("Adding filename for roi: ", roi_prefix, " trace_type: ", trace_type)
                                    if trace_type not in data_df_dict:
                                        data_df_dict[trace_type] = []
                                    data = tmp_dict[roi_prefix][trace_type]
                                    data_df_dict[trace_type] += [data for _ in range(n)]
                                    
        for k in data_df_dict:
            if len(data_df_dict[k]) != len(data_df_dict['Date']):
                print("Unequal dict list lens:")
                print([(len(data_df_dict[k]),k) for k in data_df_dict])

        if (not 'Date' in data_df_dict) or len(data_df_dict['Date']) < 1:
            print("No data was selected for any roi. Cannot create summary csv.")
        else:
            df = pd.DataFrame(data_df_dict)
            try:
                df.to_csv(csv_filename, index=False)
                pa.alert("Exported summary csv to: " + csv_filename)
            except PermissionError:
                pa.alert("Permission error. Do you have " + csv_filename + " open? Please close and then click ok.")
                df.to_csv(csv_filename, index=False)  

    def pad_zeros(self, x, n_digits=2):
        """ Pad zeros to the front of the string integer IF it is enabled """
        if not self.zero_pad_ids:
            return x
        return '0' * (n_digits - len(str(x))) + str(x)
        
                            

                    
