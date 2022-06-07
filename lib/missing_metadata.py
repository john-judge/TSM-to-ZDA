import numpy as np


# metadata to populate in ZDA. Modify as needed.
class MissingMetadata:

    def __init__(self, n_group_by_trials, recording_no, cam_settings, assign_ascending_recording_numbers):
        self.n_group_by_trials = n_group_by_trials
        self.trial_ct = 0
        self.recording_no = recording_no
        self.cam_settings = cam_settings
        self.assign_ascending_recording_numbers = assign_ascending_recording_numbers

    def fill(self, data, slice_no, location_no):
        meta = data['meta']
        raw_data = data['raw_data']
        rli = data['rli']

        data['meta']['version'] = 5
        data['meta']['slice_number'] = slice_no
        data['meta']['location_number'] = location_no
        data['meta']['record_number'] = self.recording_no
        if self.assign_ascending_recording_numbers:
            if self.trial_ct % self.n_group_by_trials == 0:
                self.recording_no += 1
            self.trial_ct += 1
        data['meta']['camera_program'] = self.cam_settings['camera_program']

        data['meta']['interval_between_trials'] = 2
        data['meta']['acquisition_gain'] = 1
        data['meta']['time_RecControl'] = 5

        data['meta']['reset_onset'] = 1
        data['meta']['reset_duration'] = 5
        data['meta']['shutter_onset'] = 5
        data['meta']['shutter_duration'] = 5

        data['meta']['stimulation1_onset'] = 20
        data['meta']['stimulation1_duration'] = 1
        data['meta']['stimulation2_onset'] = 0
        data['meta']['stimulation2_duration'] = 0

        data['meta']['acquisition_onset'] = 1
        data['meta']['interval_between_samples'] = self.cam_settings['interval_between_samples']

        data['meta']['raw_width'] = raw_data.shape[2]
        data['meta']['raw_height'] = raw_data.shape[3]
        data['meta']['points_per_trace'] = raw_data.shape[1]
        data['meta']['number_of_trials'] = raw_data.shape[0]
        data['meta']['num_fp_pts'] = 8
        num_diodes = int(meta['raw_width'] * meta['raw_height'] + meta['num_fp_pts'])
        data['rli'] = {}
        data['rli']['rli_low'] = np.zeros((1, num_diodes),
                                          dtype=np.uint16)
        data['rli']['rli_high'] = np.zeros((1, num_diodes),
                                           dtype=np.uint16)
        data['rli']['rli_high'][0, :meta['raw_width'] * meta['raw_height']] = data['rli_high_cp'].reshape(-1)
        data['rli']['rli_max'] = np.ones((1, num_diodes),
                                         dtype=np.uint16)