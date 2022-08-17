from lib.utilities import *
import threading
import time
import os
from datetime import date
import winshell
from lib.automation import FileDetector
from lib.auto_GUI.auto_DAT import AutoDAT


class Controller:
    def __init__(self, camera_program=4,
                 acqui_data=None,
                 new_rig_settings=False,
                 should_auto_launch=False,
                 filename_base="Untitled",
                 filename_start_no=1,
                 filename_end_no=5,
                 datadir=None,
                 filename_PhotoZ_format=True):

        self.acqui_data = acqui_data

        self.new_rig_settings = new_rig_settings
        self.should_auto_launch = should_auto_launch
        self.should_convert_files = True
        self.export_snr_only = True
        self.export_second_pulse_snr_only = False

        self.selected_filenames = []
        self.filename_base = filename_base
        self.filename_start_no = filename_start_no
        self.filename_end_no = filename_end_no

        self.aTSM = None
        self.aLauncher = AutoLauncher()

        self.datadir = datadir
        self.new_rig_default_dir = "C:/Turbo-SM/SMDATA/John/"
        self.stashed_dir = datadir
        self.today = date.today().strftime("%m-%d-%y")
        self.use_today_subdir = True
        if datadir is None:
            self.datadir = "./tsm_targets/"  # All files in this directory + subdirectories are loaded
            self.set_new_rig_settings(values=new_rig_settings)  # may change data dir if new_rig is true

        # Less commonly changed settings
        self.assign_ascending_recording_numbers = True
        self.filename_PhotoZ_format = filename_PhotoZ_format  # whether to write slice_loc_rec.zda as filename. Else reuse *.tsm -> *.zda
        self.apply_preprocess = False  # apply data inversing and polyfit baseline correction to save time in PhotoZ
        self.file_type = '.tsm'
        self.auto_export_maps_prefix = 'SNR'

        self.t_cropping = [0, -1]  # to handle artifacts
        self.cam_settings = CameraSettings().get_program_settings(camera_program)
        self.binning = int(self.cam_settings['height'] / 80)  # recommended binning, adjust as desired

    def get_data_dir(self, no_date=False):
        if no_date or not self.use_today_subdir:
            return self.datadir
        return self.datadir + self.today

    def set_data_dir(self, folder):
        if not folder.endswith("/"):
            folder = folder + "/"
        self.datadir = folder

    def start_up_PhotoZ(self):
        aPhz = AutoPhotoZ(self.get_data_dir(no_date=True), use_today=self.use_today_subdir)
        # launch and prep PhotoZ
        self.aLauncher.launch_photoZ()
        aPhz.prepare_photoZ()  # to do: load .pre, set filers etc06-06

    def start_up_TurboSM(self):
        self.aTSM = AutoTSM(data_dir=self.get_data_dir(no_date=True))
        # launch and prep TSM
        self.aLauncher.launch_turboSM()
        self.aTSM.prepare_TSM()

    def empty_recycle_bin(self):
        winshell.recycle_bin().empty(confirm=True,
                                     show_progress=True,
                                     sound=True)

    def open_data_folder(self):
        self.aLauncher.launch_folder(self.get_data_dir())

    def start_up_Pulser(self):
        self.aLauncher.launch_pulser()
        aPlsr = AutoPulser()
        aPlsr.prepare_pulser()

    def start_up(self, force_launch=True):
        # opens TurboSM, PhotoZ, Pulser, and some helpful file explorers
        if self.should_auto_launch or force_launch:
            self.start_up_PhotoZ()
            self.start_up_Pulser()
            self.open_data_folder()
            self.start_up_TurboSM()

    def record(self, **kwargs):
        self.run_recording_schedule()
        if self.should_convert_files:
            self.detect_and_convert()

    def run_recording_schedule(self,
                               trials_per_recording=5,
                               trial_interval=15,
                               number_of_recordings=1,
                               recording_interval=30,
                               background=False):
        self.aTSM = AutoTSM(data_dir=self.get_data_dir(no_date=True))
        if self.acqui_data is not None:
            trials_per_recording = self.acqui_data.num_trials
            trial_interval = self.acqui_data.int_trials
            number_of_recordings = self.acqui_data.num_records
            recording_interval = self.acqui_data.int_records
        if not background:
            self.aTSM.run_recording_schedule(
                trials_per_recording=trials_per_recording,
                trial_interval=trial_interval,
                number_of_recordings=number_of_recordings,
                recording_interval=recording_interval
            )
        else:
            threading.Thread(target=self.aTSM.run_recording_schedule,
                             args=(trials_per_recording,
                                   trial_interval,
                                   number_of_recordings,
                                   recording_interval),
                             daemon=True).start()

    def detect_and_convert(self, detection_loops=1, **kwargs):
        new_files = []
        # archive directory
        dst_dir = self.get_data_dir() \
                  + "/" + str(self.acqui_data.slice_no) \
                  + "_" + str(self.acqui_data.location_no)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        print("Searching for new files in:", self.get_data_dir())
        fd = FileDetector(directory=self.get_data_dir())
        for i in range(detection_loops):
            time.sleep(3)
            fd.detect_files()
            new_files += fd.get_unprocessed_file_list()
            if len(new_files) >= self.acqui_data.num_trials:
                new_files.sort()
                print("Preparing to process into ZDA file(s)... ")
                time.sleep(5)  # wait for TurboSM to safely finish writing to disk

                # process new files
                n_process = len(new_files) - (len(new_files) % self.acqui_data.num_trials)
                self.select_files(selected_filenames=new_files[:n_process],
                                  slice_no=self.acqui_data.slice_no,
                                  location_no=self.acqui_data.location_no,
                                  recording_no=self.acqui_data.record_no)
                self.process_files(no_plot=True)
                self.acqui_data.record_no += int(len(new_files) / self.acqui_data.num_trials)

                # auto-archive processed files by moving them to a directory 'slice-loc'
                for pro_file in new_files[:n_process]:
                    stripped_file = pro_file.split("/")[-1]
                    dst_file = dst_dir + "/" + stripped_file
                    os.rename(pro_file, dst_file)
                    # tbn file
                    os.rename(pro_file[:-4] + ".tbn", dst_file[:-4] + ".tbn")

                new_files = new_files[n_process:]

    def select_files(self, selected_filenames=None,
                     slice_no=1,
                     location_no=1,
                     recording_no=1,
                     filename_base="Untitled",
                     filename_start_no=1,
                     filename_end_no=5):

        self.slice_no = slice_no
        self.location_no = location_no
        self.recording_no = recording_no
        self.filename_base = filename_base
        self.filename_start_no = filename_start_no
        self.filename_end_no = filename_end_no

        if selected_filenames is not None:
            self.selected_filenames = selected_filenames
            return selected_filenames

        selected_filenames = []
        for i in range(filename_start_no, filename_end_no + 1):
            nm = str(i)
            while len(nm) < 3:
                nm = "0" + nm
            selected_filenames.append(filename_base + nm)

        self.selected_filenames = selected_filenames
        return selected_filenames

    def is_recording(self):
        return self.aTSM is not None and self.aTSM.is_recording

    def process_files(self, no_plot=False):
        n_group_by_trials = self.acqui_data.num_trials
        data_loader = DataLoader()
        if self.file_type == '.tsm':
            data_loader.load_all_tsm(data_dir=self.get_data_dir(), verbose=False)

        print(data_loader.get_n_files_loaded(), "files loaded.")

        # Select data of interest
        selected_datasets = [data_loader.select_data_by_keyword(fn) for fn in self.selected_filenames]

        for i in range(len(self.selected_filenames) - 1, 0):
            if selected_datasets[i] is None:
                del selected_datasets[i]
                del self.selected_filenames[i]

        print("# datasets to analyze:", len(selected_datasets))
        if len(selected_datasets) % n_group_by_trials != 0:
            print("Cannot group", len(selected_datasets), "trials into groups of", str(n_group_by_trials) + ".")
        n_discard = int(len(selected_datasets) % n_group_by_trials)
        print("Discarding last", n_discard, "files.")
        if n_discard > 0:
            del selected_datasets[-n_discard:]
            del self.selected_filenames[-n_discard:]
        print("New # datasets to analyze:", len(selected_datasets))

        # binning and cropping
        for i in range(len(selected_datasets)):
            sd = selected_datasets[i]
            if sd is None:
                print("Dataset not found:", self.selected_filenames[i])
            else:
                sd.clip_data(y_range=self.cam_settings['cropping'], t_range=self.t_cropping)
                sd.bin_data(binning=self.binning)

        # load data
        datasets = [{'filename': self.selected_filenames[i],
                     'raw_data': selected_datasets[i].get_data(),
                     'meta': selected_datasets[i].get_meta(),
                     'rli': selected_datasets[i].get_rli(),
                     'fp_data': selected_datasets[i].get_fp_data()}
                    for i in range(len(selected_datasets))]

        # if we're just one off for image dimension, auto-correct for the user
        for i in range(len(datasets)):
            data = datasets[i]
            if data['raw_data'].shape[2] - data['raw_data'].shape[3] == 1:
                data['raw_data'] = raw_data[:, :, :-1, :]
            elif data['raw_data'].shape[3] - data['raw_data'].shape[2] == 1:
                data['raw_data'] = data['raw_data'][:, :, :, :-1]

            data['rli_high_cp'] = np.copy(data['raw_data'][0, 0, :, :]).astype(np.uint16)

            # view frames
            if i % 10 == 0 and not no_plot:
                fig, axes = plt.subplots(1, 2)
                axes[0].imshow(data['raw_data'][0, 0, :, :], cmap='gray')
                axes[1].imshow(data['raw_data'][0, -1, :, :], cmap='jet')
                plt.show()

                plt.subplots()
                plt.plot(data['raw_data'][0, :, 0, 0])

            # final check
            if data['raw_data'].shape[2] != data['raw_data'].shape[3]:
                raise Exception("PhotoZ will not work with non-square array! Adjust cropping and/or binning")

        # Fill in missing metadata as needed
        mm = MissingMetadata(n_group_by_trials,
                             self.acqui_data.record_no,
                             self.cam_settings,
                             self.assign_ascending_recording_numbers)
        for data in datasets:
            mm.fill(data, self.acqui_data.slice_no, self.acqui_data.location_no)

        if self.apply_preprocess:
            for data in datasets:
                # Apply baseline correction here. Because PhotoZ chokes on baseline correcting TurboSM data
                tr = Tracer()
                # data inversing
                data['raw_data'] = -data['raw_data']

                # Need to subtract off the low-frequency voltage drift. First-order correction
                tr.correct_background(data['meta'], data['raw_data'])

        for i in range(len(datasets)):
            data = datasets[i]

            # normalize raw data to 12-bit range
            data['fp_data'] = normalize_bit_range(data['fp_data'])
            data['raw_data'] = normalize_bit_range(data['raw_data'])

            # view frames
            if i % 10 == 0 and not no_plot:
                fig, axes = plt.subplots(1, 2)
                print(data['raw_data'].shape)
                axes[0].imshow(data['raw_data'][0, 0, :, :], cmap='jet')
                axes[1].imshow(data['raw_data'][0, -1, :, :], cmap='jet')
                plt.show()

        # resize FP data
        for i in range(len(datasets)):
            data = datasets[i]
            meta = data['meta']
            fp_data = data['fp_data']

            fp_data_final = np.zeros((1, fp_data.shape[0], meta['num_fp_pts']))
            fp_data_final[0, :, :fp_data.shape[1]] = fp_data[:, :]
            data['fp_data'] = np.swapaxes(fp_data_final, 2, 1)[:, :, self.t_cropping[0]:self.t_cropping[1]]

            if i % 10 == 0 and not no_plot:
                print(data['fp_data'].shape)

                fig, ax = plt.subplots()
                ax.plot(fp_data_final[0, self.t_cropping[0]:self.t_cropping[1], :])

        # group data by trials
        tg = TrialGrouper(n_group_by_trials)
        datasets = tg.make_groupings(datasets)

        # Write data
        zda_writer = ZDA_Writer()
        files_created = []
        for data in datasets:
            meta = data['meta']
            raw_data = data['raw_data']
            rli = data['rli']
            fp_data = data['fp_data']
            if self.filename_PhotoZ_format:
                slic = str(meta['slice_number'])
                if len(slic) < 2:
                    slic = "0" + slic
                loc = str(meta['location_number'])
                if len(loc) < 2:
                    loc = "0" + loc
                rec = str(meta['record_number'])
                if len(rec) < 2:
                    rec = "0" + rec
                data['filename'] = slic + "_" + loc + "_" + rec

            zda_writer.write_zda_to_file(raw_data, meta, data['filename'] + ".zda", rli, fp_data)
            files_created.append(data['filename'] + ".zda")
            print("Written to " + data['filename'] + ".zda")

        # move created files to target directory
        target_dir = self.get_data_dir(no_date=False) + "/converted_zda"
        previous_dir = os.getcwd()
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        try:
            for f in files_created:
                os.rename(previous_dir + "/" + f, target_dir + "/" + f)
        except Exception as e:
            print(e)
            print("Could not move some or all files to selected directory."
                  " Look in", previous_dir, "instead.")
            return
        print("Created file(s) in", target_dir)

    def set_convert_files_switch(self, **kwargs):
        self.should_convert_files = kwargs['values']

    def set_use_today_subdir(self, **kwargs):
        self.use_today_subdir = kwargs['values']

    def set_new_rig_settings(self, **kwargs):
        self.new_rig_settings = kwargs['values']
        if self.new_rig_settings:
            self.stashed_dir = self.get_data_dir(no_date=True)
            self.set_data_dir(self.new_rig_default_dir)
        else:
            self.set_data_dir(self.stashed_dir)

    def auto_export_maps(self):
        if self.export_snr_only:
            AutoDAT(datadir=self.get_data_dir(),
                    file_prefix=self.auto_export_maps_prefix).save_snr_background_data()
        else:
            AutoDAT(datadir=self.get_data_dir()).save_3_kinds_all_background_data()

    def set_export_snr_only(self, **kwargs):
        self.export_snr_only = kwargs["values"]

    def set_export_second_pulse_snr_only(self, **kwargs):
        self.export_second_pulse_snr_only = kwargs["values"]

    def set_auto_export_maps_prefix(self, **kwargs):
        self.auto_export_maps_prefix = kwargs["values"]

    def export_paired_pulse(self, pulse2_times, allowed_times):
        ad = AutoDAT(datadir=self.get_data_dir(),
                     file_prefix=self.auto_export_maps_prefix)
        if not self.export_second_pulse_snr_only:
            ad.save_snr_background_data()
        else:
            ad.get_zda_file_list()
        if len(pulse2_times) != ad.get_file_count():
            print("ZDA file count:", ad.get_file_count())
            return False
        ad.change_file_prefix(self.auto_export_maps_prefix + "_2PP")
        ad.save_snr_background_data_at_times(pulse2_times, allowed_times)
        return True
