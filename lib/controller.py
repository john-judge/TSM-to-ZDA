from lib.utilities import *
import threading


class Controller:
    def __init__(self, camera_program=4,
                 new_rig_settings=False,
                 should_auto_launch=False,
                 slice_no=1, location_no=1,
                 recording_no=1, filename_base="Untitled",
                 filename_start_no=1,
                 filename_end_no=5,
                 datadir=None,
                 filename_PhotoZ_format=True):

        self.new_rig_settings = new_rig_settings
        self.should_auto_launch = should_auto_launch
        self.is_launched = False

        self.selected_filenames = []
        self.slice_no = slice_no
        self.location_no = location_no
        self.recording_no = recording_no
        self.filename_base = filename_base
        self.filename_start_no = filename_start_no
        self.filename_end_no = filename_end_no

        self.datadir = datadir
        if datadir is None:
            self.datadir = "./tsm_targets/05-31-22"  # All files in this directory + subdirectories are loaded
            if self.new_rig_settings:
                self.datadir = "C:/Turbo-SM/SMDATA/John/06-06-22"  # on new rig

        # Less commonly changed settings
        self.assign_ascending_recording_numbers = True
        self.filename_PhotoZ_format = filename_PhotoZ_format  # whether to write slice_loc_rec.zda as filename. Else reuse *.tsm -> *.zda
        self.apply_preprocess = False  # apply data inversing and polyfit baseline correction to save time in PhotoZ
        self.file_type = '.tsm'

        self.t_cropping = [0, -1]  # to handle artifacts
        self.cam_settings = CameraSettings().get_program_settings(camera_program)
        self.binning = int(self.cam_settings['height'] / 80)  # recommended binning, adjust as desired

    def start_up(self):
        # opens TurboSM, PhotoZ, Pulser, and some helpful file explorers
        if not self.is_launched and self.should_auto_launch:
            al = AutoLauncher()
            aTSM = AutoTSM()
            if self.new_rig_settings:
                aPhz = AutoPhotoZ()
            else:
                aPhz = AutoPhotoZ('C:/.../tsm_targets/')

            # launch and prep PhotoZ
            al.launch_photoZ()
            aPhz.prepare_photoZ()
            al.launch_pulser()

            # file explorers
            al.launch_recycle()
            al.launch_tsm_to_zda_files()
            al.launch_turboSMDATA()

            # launch and prep TSM
            al.launch_turboSM()
            aTSM.prepare_TSM()

            self.is_launched = True

    def run_recording_schedule_background(self,
                                          trials_per_recording=5,
                                          trial_interval=15,
                                          number_of_recordings=1,
                                          recording_interval=30):
        aTSM = AutoTSM()
        threading.Thread(target=aTSM.run_recording_schedule,
                         args=(trials_per_recording,
                               trial_interval,
                               number_of_recordings,
                               recording_interval),
                         daemon=True).start()

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

    def process_files(self, n_group_by_trials=5):
        data_loader = DataLoader()
        if self.file_type == '.tsm':
            data_loader.load_all_tsm(data_dir=self.datadir, verbose=False)

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
            if i % 10 == 0:
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
                             self.recording_no,
                             self.cam_settings,
                             self.assign_ascending_recording_numbers)
        for data in datasets:
            mm.fill(data, self.slice_no, self.location_no)

        # Run this cell at most once
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
            if i % 10 == 0:
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

            if i % 10 == 0:
                print(data['fp_data'].shape)

                fig, ax = plt.subplots()
                ax.plot(fp_data_final[0, self.t_cropping[0]:self.t_cropping[1], :])

        # group data by trials
        tg = TrialGrouper(n_group_by_trials)
        datasets = tg.make_groupings(datasets)

        # Write data
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

            zda_writer = ZDA_Writer()
            zda_writer.write_zda_to_file(raw_data, meta, data['filename'] + ".zda", rli, fp_data)
            print("Written to " + data['filename'] + ".zda")
