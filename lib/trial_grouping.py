import numpy as np


class TrialGrouper:

    def __init__(self, n_group_by_trials):
        self.n_group_by_trials = n_group_by_trials

    def concatenate_trials(self, trial_data):
        trial_data['raw_data'] = np.concatenate(trial_data['raw_data'],
                                                axis=0)
        if trial_data['raw_data'].shape[0] != self.n_group_by_trials:
            raise TypeError("Trial axis is wrong shape:",
                            trial_data['raw_data'].shape)
        trial_data['fp_data'] = np.concatenate(trial_data['fp_data'],
                                               axis=0)
        if trial_data['fp_data'].shape[0] != self.n_group_by_trials:
            raise TypeError("Trial axis is wrong shape:",
                            trial_data['fp_data'].shape)

    def make_groupings(self, datasets, verbose=True):
        trial_datasets = []
        trial_data = None
        if self.n_group_by_trials > 1:
            trial_ct = 0
            for data in datasets:
                if trial_ct % self.n_group_by_trials == 0:
                    if trial_data is not None:
                        self.concatenate_trials(trial_data)
                        trial_datasets.append(trial_data)
                    # next dataset
                    trial_data = {
                        'raw_data': [],
                        'meta': data['meta'],
                        'fp_data': [],
                        'rli': data['rli']  # only uses RLI of first file
                    }
                    trial_data['meta']['number_of_trials'] = self.n_group_by_trials
                    if verbose:
                        print("trial group", len(trial_datasets))
                # collect raw_data, fp_data, and rli
                i_trial = trial_ct % self.n_group_by_trials
                trial_data['raw_data'].append(data['raw_data'])
                trial_data['fp_data'].append(data['fp_data'])
                trial_ct += 1
                if verbose:
                    print("\t", data['filename'])
            # final set
            if trial_data is not None:
                self.concatenate_trials(trial_data)
                trial_datasets.append(trial_data)
            datasets = trial_datasets
            if verbose:
                print("# of trial-grouped datasets:", len(datasets))
        return trial_datasets
