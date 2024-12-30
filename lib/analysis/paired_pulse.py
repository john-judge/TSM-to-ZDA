import pandas as pd
import os
import numpy as np
import pyautogui as pa


class PairedPulseExporter:
    """ Paired Pulse Exporter """

    def __init__(self, data_dir, auto_exporter=None):
        """ Param_file is a path to a csv file """
        self.data_dir = data_dir
        self.auto_exporter = auto_exporter
        self.param_file = os.path.join(self.data_dir, "ppr_catalog.csv")

    def build_shuffle_file_dict(self, subdir):
        ''' Build a shuffle file directory mapping slice/loc to list of IPIs '''
        shuffle_file_dict = {'ipi': {}, 'is_single_pulse_control': {}, 'record_numbers': {}}
        for zda_file in os.listdir(subdir):
            if zda_file.endswith('.zda'):
                # parse slice, location, record from file name
                slice_num, loc_num, rec_num = [int(x) for x in zda_file.split("/")[-1].split('.')[0].split('_')[:3]]
                slic_loc = str(slice_num) + '_' + str(loc_num)
                if slic_loc in shuffle_file_dict['ipi']:
                    shuffle_file_dict['record_numbers'][slic_loc].append(rec_num)
                    continue
                else:
                    shuffle_file_dict['ipi'][slic_loc] = []
                    shuffle_file_dict['is_single_pulse_control'][slic_loc] = []
                    shuffle_file_dict['record_numbers'][slic_loc] = [rec_num]

                # check for corresponding shuffle file
                shuffle_file = f"{slice_num}_{loc_num}shuffle.txt"
                shuffle_filepath = os.path.join(subdir, shuffle_file)
                
                if os.path.exists(shuffle_filepath):

                    # load the file. It should be a 3-column file 
                    shuffle_df = pd.read_csv(os.path.join(subdir, shuffle_file), sep='\t', header=None,
                                             names=['pulse1', 'pulse2', 'is_single_pulse_control'])
                    if shuffle_df.shape[1] != 3:
                        print("Ill-formatted shuffle file: ", shuffle_file)
                    else:
                        # difference of first two columns is the IPI
                        ipi = shuffle_df['pulse2'] - shuffle_df['pulse1']
                        shuffle_file_dict['ipi'][slic_loc] = list(ipi)

                        # the third column is whether the event is a single pulse control
                        is_single_pulse_control = shuffle_df['is_single_pulse_control']
                        shuffle_file_dict['is_single_pulse_control'][slic_loc] = list(is_single_pulse_control)
        return shuffle_file_dict

    def generate_example_param_file(self):
        """ Generate a blank example param file.
            It is a csv file with the following headers:
            - path to zda file
            - measure window start and width for first pulse
            - measure window start and width for second pulse (blank if this is a control zda file)
            - baseline correction window start and width (one for both pulses)
            
            Then walk through the data directory and find all zda files, and create a blank row for each one.

            Create as pandas dataframe and save to csv
        """
        example_params = pd.DataFrame(columns=['zda_file', 'pulse1_start', 'pulse1_width', 'pulse2_start', 'pulse2_width', 'baseline_start', 'baseline_width'])

        for subdir, dirs, files in os.walk(self.data_dir):
            shuffle_file_dict = self.build_shuffle_file_dict(subdir)
            print(shuffle_file_dict)
            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):
                    # parse slice, location, record from file name
                    slice_num, loc_num, rec_num = [int(x) for x in zda_file.split("/")[-1].split('.')[0].split('_')[:3]]
                    
                    example_params_dict = {'zda_file': subdir + '/' + zda_file, 
                                           'pulse1_start': '', 
                                           'pulse1_width': '', 
                                           'pulse2_start': '', 
                                           'pulse2_width': '', 
                                           'baseline_start': '', 
                                           'baseline_width': '',
                                           'IPI': '',   
                                           'is_single_pulse_control': ''}
                    if str(slice_num) + '_' + str(loc_num) in shuffle_file_dict['ipi']:
                        idx_rec = shuffle_file_dict['record_numbers'][str(slice_num) + '_' + str(loc_num)].index(rec_num)
                        if idx_rec <= len(shuffle_file_dict['ipi'][str(slice_num) + '_' + str(loc_num)]) - 1:
                            example_params_dict['IPI'] = shuffle_file_dict['ipi'][str(slice_num) + '_' + str(loc_num)][idx_rec]
                            example_params_dict['is_single_pulse_control'] = shuffle_file_dict['is_single_pulse_control'][
                                                        str(slice_num) + '_' + str(loc_num)][idx_rec]

                    example_params = example_params.append(example_params_dict, ignore_index=True)
        if os.path.exists(self.param_file):
            choice = pa.confirm("Catalog file already exists. Would you like to overwrite it?\n" + 
            self.param_file, buttons=['Yes', 'No'])
            if choice == 'No':
                return
        try:
            example_params.to_csv(self.param_file, index=False)
        except PermissionError:
            pa.alert("Error: Permission denied. Please close the following file and try again.\n" \
                + self.param_file)
            return
        pa.alert("Opening blank PPR catalog file created at " + self.param_file + 
        "\n\nPlease fill in the measure windows and baseline windows (units of Points) for each zda file. \
            \nLeave pulse2 fields blank if the recording is a single-pulse control. \
            \nWhen done, save the file and click 'Export' to export the PPR data.")
        if os.path.exists(self.param_file):
            try:
                os.startfile(self.param_file)
            except FileNotFoundError:
                pa.alert("Error: Could not open file. Please open the file manually.")

    def load_param_file(self):
        """ Load the param file """
        if self.param_file is None:
            pa.alert("No catalog file found. Please generate one first.")

        param_df = None

        try:
            param_df = pd.DataFrame(pd.read_csv(self.param_file))
        except PermissionError:
            pa.alert("Error: Permission denied. Please close the file and try again.")
        except FileNotFoundError:
            pa.alert("Error: File not found. Please generate a catalog file first.")
        except Exception as e:
            pa.alert("Error: " + str(e))

        return param_df

    def check_param_file(self):
        """ Check the param file for errors """
        param_df = self.load_param_file()
        if param_df is None:
            pa.alert("Error: No catalog file found. Please generate one first.")
            return

        errors = []
        for index, row in param_df.iterrows():
            if row['pulse1_start'] == np.nan or row['pulse1_width'] == np.nan or row['baseline_start'] == '' or row['baseline_width'] == np.nan:
                errors.append("Missing values for zda file: " + row['zda_file'])
            if row['pulse2_start'] == np.nan and row['pulse2_width'] != np.nan:
                errors.append("Missing pulse2 start value for zda file: " + row['zda_file'])
            if row['pulse2_start'] != np.nan and row['pulse2_width'] == np.nan:
                errors.append("Missing pulse2 width value for zda file: " + row['zda_file'])
        if len(errors) > 0:
            pa.alert("Errors found in catalog file:\n\n" + "\n".join(errors))
            return False
        return True

    def create_ppr_map(self, param_df):
        """ Turn df into a dictionary with zda file as key and a dictionary of parameters as value """
        ppr_map = {}
        for index, row in param_df.iterrows():
            ppr_map[row['zda_file']] = {'pulse1_start': row['pulse1_start'], 'pulse1_width': row['pulse1_width'], 
            'pulse2_start': row['pulse2_start'], 'pulse2_width': row['pulse2_width'], 'baseline_start': row['baseline_start'], 
            'baseline_width': row['baseline_width']}
        return ppr_map

    def export(self, **kwargs):
        """ Export Paired Pulse Data. This function is run by a worker thread, and
        has access to the vanilla exporter object via self.auto_exporter . """
        stop_event = kwargs.get('stop_event', None)
        self.check_param_file()
        param_df = self.load_param_file()
        if param_df is None:
            return
        ppr_map = self.create_ppr_map(param_df)
        self.auto_exporter.add_ppr_catalog(ppr_map)
        self.auto_exporter.export()
        print(param_df)
        

    def regenerate_ppr_summary_csv(self):
        """ Regenerate the ppr summary csv file """
        param_df = self.load_param_file()
        if param_df is None:
            return
        ppr_map = self.create_ppr_map(param_df)
        self.auto_exporter.add_ppr_catalog(ppr_map)
        self.auto_exporter.export(rebuild_map_only=True)
        pa.alert("PPR summary csv file regenerated.")