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
            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):
                    example_params = example_params.append({'zda_file': subdir + '/' + zda_file, 
                    'pulse1_start': '', 'pulse1_width': '', 'pulse2_start': '', 'pulse2_width': '', 'baseline_start': '', 
                    'baseline_width': ''}, ignore_index=True)
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