import pandas as pd
import os
import numpy as np

from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ
from lib.utilities import parse_date


class AutoExporter(AutoPhotoZ):
    def __init__(self, is_export_amp_traces, is_export_snr_traces, is_export_latency_traces, is_export_halfwidth_traces,
                        is_export_traces, is_export_snr_maps, is_export_max_amp_maps, export_trace_prefix, roi_export_option,
                            export_rois_keyword, **kwargs):
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

    def get_roi_filenames(self, subdir, rec_id, roi_keyword):
        """ Return all files that match the rec_id and the roi_keyword in the subdir folder
         However, roi_files cannot have the trace_type keywords in them """
        roi_files = []
        for file in os.listdir(subdir):
            if str(rec_id) in file and roi_keyword in file:
                    if 'amp' not in file and 'snr' not in file and \
                        'latency' not in file and 'halfwidth' not in file:
                        roi_files.append(file)
        return roi_files

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
        return subdir + "/" + "_".join([self.export_trace_prefix, str(slic_id), str(loc_id), str(rec_id), trace_type, roi_prefix]) + ".dat"

    def update_export_map(self, export_map, subdir, slic_id, loc_id, rec_id, trace_type, roi_prefix, filename):
        """ Update the export map with the filename of newly created file"""
        if rec_id not in export_map[subdir][slic_id][loc_id]:
            export_map[subdir][slic_id][loc_id][rec_id] = {}
        if trace_type not in export_map[subdir][slic_id][loc_id][rec_id]:
            export_map[subdir][slic_id][loc_id][rec_id][trace_type] = {}
        export_map[subdir][slic_id][loc_id][rec_id][trace_type][roi_prefix] = filename

    def export(self):
        """ Export all traces and maps """
        data_map = self.create_data_map()
        export_map = dict(data_map)

        # Export traces loop
        for subdir in data_map:
            aPhz = AutoPhotoZ(data_dir=subdir)
            
            for slic_id in data_map[subdir]:
                slic_roi_files = [None]
                if self.roi_export_option == 'Slice':
                    slic_roi_files = self.get_roi_filenames(subdir, slic_id, self.export_rois_keyword)
                if len(slic_roi_files) < 1:
                    slic_roi_files = [None]

                # loop over all slice rois if any
                for slice_roi_file in slic_roi_files:
                    roi_prefix = ''
                    if slice_roi_file is not None:
                        roi_prefix = slice_roi_file.split('.')[0]
                        aPhz.select_roi_tab()
                        aPhz.open_roi_file(subdir + "/" + slice_roi_file)
                        print("Opened ROI file:", slice_roi_file)

                    for loc_id in data_map[subdir][slic_id]:
                        slic_loc_id = str(slic_id) + "_" + str(loc_id)

                        loc_roi_files = [None]
                        if self.roi_export_option == 'Slice_Loc':
                            loc_roi_files = self.get_roi_filenames(subdir, slic_loc_id, self.export_rois_keyword)
                        if len(loc_roi_files) < 1:
                            loc_roi_files = [None]

                        # loop over all location rois if any
                        for loc_roi_file in loc_roi_files:
                            if loc_roi_file is not None:
                                roi_prefix = loc_roi_file.split('.')[0]
                                aPhz.select_roi_tab()
                                aPhz.open_roi_file(subdir + "/" + loc_roi_file)
                                print("Opened ROI file:", loc_roi_file)

                            for zda_file in data_map[subdir][slic_id][loc_id]['zda_files']:

                                zda_id = zda_file.split('/')[-1].split('.')[0]
                                _, _, rec_id = zda_id.split('_')
                                rec_id = int(rec_id)

                                # open zda files
                                print("\n", zda_file)
                                aPhz.open_zda_file(zda_file)
                                
                                rec_roi_files = [None]
                                if self.roi_export_option == 'Slice_Loc_Rec':
                                    rec_roi_files = self.get_roi_filenames(subdir, rec_id, self.export_rois_keyword)
                                if len(rec_roi_files) < 1:
                                    rec_roi_files = [None]

                                # loop over all recording rois if any
                                for rec_roi_file in rec_roi_files:
                                    if rec_roi_file is not None:
                                        roi_prefix = rec_roi_file.split('.')[0]
                                        aPhz.select_roi_tab()
                                        aPhz.open_roi_file(subdir + "/" + rec_roi_file)
                                        print("Opened ROI file:", rec_roi_file)

                                    if self.is_export_amp_traces:
                                        amp_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix)
                                        aPhz.select_maxamp_trace_value()
                                        aPhz.save_trace_values(amp_filename)
                                        print("\tExported:", amp_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp', roi_prefix, amp_filename)
                                    if self.is_export_snr_traces:
                                        snr_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix)
                                        aPhz.select_SNR_trace_value()
                                        aPhz.save_trace_values(snr_filename)
                                        print("\tExported:", snr_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr', roi_prefix, snr_filename)
                                    if self.is_export_latency_traces:
                                        lat_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix)
                                        aPhz.select_latency_trace_value()
                                        aPhz.save_trace_values(lat_filename)
                                        print("\tExported:", lat_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'latency', roi_prefix, lat_filename)
                                    if self.is_export_halfwidth_traces:
                                        hw_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix)
                                        aPhz.select_half_width_trace_value()
                                        aPhz.save_trace_values(hw_filename)
                                        print("\tExported:", hw_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'halfwidth', roi_prefix, hw_filename)
                                    if self.is_export_traces:
                                        trace_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix)
                                        aPhz.save_current_traces(trace_filename, go_to_tab=True)
                                        print("\tExported:", trace_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'trace', roi_prefix, trace_filename)
                                    if self.is_export_snr_maps:
                                        amp_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix)
                                        aPhz.select_MaxAmp_array()
                                        aPhz.save_background(filename=amp_array_filename)
                                        print("\tExported:", amp_array_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'amp_array', roi_prefix, amp_array_filename)
                                    if self.is_export_max_amp_maps:
                                        snr_array_filename = self.get_export_target_filename(subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix)
                                        aPhz.select_SNR_array()
                                        aPhz.save_background(filename=snr_array_filename)
                                        print("\tExported:", snr_array_filename)
                                        self.update_export_map(export_map, subdir, slic_id, loc_id, rec_id, 'snr_array', roi_prefix, snr_array_filename)

        self.generate_summary_csv(export_map)    

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
                for loc_id in export_map[subdir][slic_id]:
                    for rec_id in export_map[subdir][slic_id][loc_id]:

                        tmp_dict = {}
                        for trace_type in export_map[subdir][slic_id][loc_id][rec_id]:
                            if rec_id == 'zda_files':
                                continue
                            for roi_prefix in export_map[subdir][slic_id][loc_id][rec_id][trace_type]:
                                filename = export_map[subdir][slic_id][loc_id][rec_id][trace_type][roi_prefix]
                                if not os.path.exists(filename):
                                    raise FileNotFoundError("File not found:", filename)
                                if self.type_is_trace_value(trace_type):
                                    data = self.read_trace_value_file(filename)
                                else:
                                    # otherwise, just put the filename in the column
                                    data = filename
                                if roi_prefix not in tmp_dict:
                                    tmp_dict[roi_prefix] = {}
                                tmp_dict[roi_prefix][trace_type] = data
                                
                        # unload the tmp_dict into the data_df_dict in the correct order for this recording
                        for roi_prefix in tmp_dict:
                            n = None
                            for trace_type in tmp_dict[roi_prefix]:
                                data = tmp_dict[roi_prefix][trace_type]
                                if type(data) != str:
                                    n = len(data['Value'])
                                    data_df_dict[trace_type] = data['Value'].values
                                    data_df_dict['ROI'] = data['ROI'].values

                            if n is None:
                                print("No trace value data was selected for " + roi_prefix + ": " + trace_type + ". Cannot include in summary csv.")
                                continue
                            data_df_dict['ROI_Set'] = [roi_prefix for _ in range(n)]
                            data_df_dict['Date'] = [date for _ in range(n)]
                            data_df_dict['Slice'] = [slic_id for _ in range(n)]
                            data_df_dict['Location'] = [loc_id for _ in range(n)]
                            data_df_dict['Recording'] = [rec_id for _ in range(n)]

                            '''for trace_type in tmp_dict[roi_prefix]:
                                if type(data) == str:
                                    data_df_dict[trace_type] = [data for _ in range(n)]'''

        if (not 'Date' in data_df_dict) or len(data_df_dict['Date']) < 1:
            print("No data was selected for any roi. Cannot create summary csv.")
        else:
            df = pd.DataFrame(data_df_dict)
            df.to_csv(csv_filename, index=False)
                            

                    
