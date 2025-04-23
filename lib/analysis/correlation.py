import numpy as np

class FunctionalConnectivityMatrix:
    """
    Given two sets of time series, compute the functional connectivity matrix
    connecting the two sets of time series as a bipartite graph.
    The connectivity matrix is computed by calculating the correlation between
    each pair of time series, one from each set.
    The resulting matrix is a square matrix where the rows correspond to the
    time series from the first set and the columns correspond to the time series
    from the second set.

    Optionally, parameter MEASURE_WINDOWS can be used to specify only the time 
    ranges that should be considered for the correlation calculation.

    The correlation is computed using the Pearson correlation coefficient, 
    mutual information, or other correlation measures.
    """

    def __init__(self, measure_windows=None):
        self.measure_windows = measure_windows

    def compute_correlation(self, set1, set2, method='pearson'):
        """
        Compute the functional connectivity matrix between two sets of time series.

        Args:
            set1: List of time series (e.g., pixels) from the first set.
            set2: List of time series (e.g., pixels) from the second set.

        Returns:
            A 2D NumPy array representing the functional connectivity matrix.
        """
        if method not in ['pearson']:
            raise ValueError("Unsupported method. Only 'pearson' is currently implemented.")

        corr_function = np.corrcoef if method == 'pearson' else None
        
        if self.measure_windows:
            set1 = self._apply_measure_windows(set1)
            set2 = self._apply_measure_windows(set2)

        num_rows = len(set1)
        num_cols = len(set2)
        fc_matrix = np.zeros((num_rows, num_cols))

        for i, ts1 in enumerate(set1):
            for j, ts2 in enumerate(set2):
                fc_matrix[i, j] = corr_function(ts1, ts2)[0, 1]

        return fc_matrix

    def _apply_measure_windows(self, time_series):
        """
        Apply the measure windows to the time series.

        Args:
            time_series: List of time series.

        Returns:
            A list of time series with measure windows applied.
        """
        filtered_series = []
        for ts in time_series:
            filtered_ts = []
            for start, end in self.measure_windows:
                filtered_ts.extend(ts[start:end])
            filtered_series.append(filtered_ts)
        return filtered_series


class DynamicFC(FunctionalConnectivityMatrix):
    """ Given two sets series of time traces --
        these are two lists (representing two barrels) of several lists 
        (representating several recordings) of time traces (each one for 
        a single pixel in that barrel), compute the dynamic FC matrices
        (one FC matrix per time windows given for each pair of recordings).
    
    MEASURE_WINDOWS is a list of list of tuples. There is one list
    for each pair of recordings, and each tuple in the list
    represents the start and end time of a window to consider for the
    correlation calculation. If MEASURE_WINDOWS is not provided, the
    entire time series is used for the correlation calculation.
    
    The resulting dynamic FC matrices are stored in a dict of dicts, mapping
    recording index to measure window index to the corresponding
    functional connectivity matrix. Each functional connectivity matrix is
    a square matrix where the rows correspond to the time series (pixels) from the first
    set and the columns correspond to the time series (pixels) from the second set.
    
    """

    def compute_dynamic_fc(self, set1, set2):
        """
        Compute dynamic FC matrices for each measure window.

        Args:
            set1: List of time series (e.g., pixels) from the first set.
            set2: List of time series (e.g., pixels) from the second set.

        Returns:
            A dictionary mapping recording index to measure window index to the
            corresponding functional connectivity matrix.
        """
        dynamic_fc = {}
        for rec_idx, windows in enumerate(self.measure_windows):
            dynamic_fc[rec_idx] = {}
            for win_idx, (start, end) in enumerate(windows):
                set1_window = [ts[start:end] for ts in set1]
                set2_window = [ts[start:end] for ts in set2]
                dynamic_fc[rec_idx][win_idx] = self.compute_correlation(set1_window, set2_window)
        return dynamic_fc


class StaticFC(FunctionalConnectivityMatrix):
    """ Given two sets series of time traces --
    these are two lists (representing two barrels) of several lists 
    (representating several recordings) of time traces (each one for 
    a single pixel in that barrel), compute the static FC matrices
    (one FC matrix across all measure windows and recordings).

    Optionally, parameter MEASURE_WINDOWS can be used to specify only the time 
    ranges that should be considered for the correlation calculation.

    The correlation is computed using the Pearson correlation coefficient, 
    mutual information, or other correlation measures. All traces for a 
    single pixel are concatenated across all measure windows and recordings
    before the correlation calculation is performed, so that a single
    functional connectivity matrix is computed.
    """

    def compute_static_fc(self, set1, set2):
        """
        Compute a single static FC matrix.

        Args:
            set1: List of time series (e.g., pixels) from the first set.
            set2: List of time series (e.g., pixels) from the second set.

        Returns:
            A 2D NumPy array representing the static functional connectivity matrix.
        """
        concatenated_set1 = self._concatenate_time_series(set1)
        concatenated_set2 = self._concatenate_time_series(set2)
        return self.compute_correlation(concatenated_set1, concatenated_set2)

    def _concatenate_time_series(self, time_series):
        """
        Concatenate time series across all measure windows.

        Args:
            time_series: List of time series.

        Returns:
            A list of concatenated time series.
        """
        concatenated_series = []
        for ts in time_series:
            concatenated_ts = []
            for start, end in self.measure_windows:
                concatenated_ts.extend(ts[start:end])
            concatenated_series.append(concatenated_ts)
        return concatenated_series