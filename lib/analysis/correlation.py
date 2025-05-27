import numpy as np
from scipy import signal
from statsmodels.tsa.stattools import grangercausalitytests
import gc
import matplotlib.pyplot as plt
import random


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

    def compute_correlation(self, set1, set2, method='max_cross_corr', max_lag=12, lag=None, plot_rate=0.1):
        """
        Compute the functional connectivity matrix between two sets of time series.

        Args:
            set1: List of time series (e.g., pixels) from the first set.
            set2: List of time series (e.g., pixels) from the second set.
            plot_rate: What fraction of the time series to plot.

        Returns:
            A 2D NumPy array representing the functional connectivity matrix.
        """

        if method not in ['pearson', 'max_cross_corr', 'granger']:
            raise ValueError("Unsupported method.")

        def max_cross_corr(ts1, ts2, lag=max_lag):
            """
            if ts2 is a lagged signal, computes the
            maximum cross-correlation between ts1 and ts2 within a lag up to LAG
            """
            corr = signal.correlate(ts1, ts2, mode='full')
            lags = signal.correlation_lags(len(ts1), len(ts2), mode='full')
            
            corr = corr[(lags > 0) & (lags <= lag)]
            return min(1, np.max(corr) / 40)

        def pearson_corr(ts1, ts2, lag=lag, normalize=True, plot_rate=plot_rate):
            """
            Compute the Pearson correlation coefficient between two time series.
            """
            ts1 = np.array(ts1)
            ts2 = np.array(ts2)
            if lag is None:
                lag = 0
            # shift ts2 forward by lag
            ts1_, ts2_ = self._apply_measure_windows_and_lag_ts(ts1, ts2, lag, normalize=normalize, plot_rate=plot_rate)
            res = np.corrcoef(ts1_, ts2_)[0, 1]

            return res

        def granger_causality(ts1, ts2, max_lag=max_lag):
            """
            Compute the Granger causality between two time series. Does the first
            time series cause the second one?
            """
            ts1 = np.array(ts1).reshape(-1, 1)
            ts2 = np.array(ts2).reshape(-1, 1)
            test_result = grangercausalitytests(np.hstack((ts2, ts1)), max_lag, verbose=False)
            
            p_values = [1 - test[0]['ssr_ftest'][1] for test in test_result.values()]
            lags = np.array(list(test_result.keys()))
            return p_values, lags

        corr_function = pearson_corr if method == 'pearson' else max_cross_corr \
            if method == 'max_cross_corr' else granger_causality \
            if method == 'granger' else None

        is_lag_analysis = (method in ['max_cross_corr', 'granger'])

        # need to apply measure winndows after the lag is applied
        # to avoid correlation artifacts
        #if self.measure_windows:
        #    set1 = self._apply_measure_windows(set1)
        #    set2 = self._apply_measure_windows(set2)

        num_rows = len(set1)
        num_cols = len(set2)
        fc_matrix = None
        if not is_lag_analysis:
            fc_matrix = np.zeros((num_rows, num_cols))
        else:
            fc_matrix = np.zeros((num_rows, num_cols, max_lag))

        for i, ts1 in enumerate(set1):
            for j, ts2 in enumerate(set2):
                if not is_lag_analysis:
                    fc_matrix[i, j] = corr_function(ts1, ts2)
                else:
                    p_values, lags = corr_function(ts1, ts2, max_lag)
                    fc_matrix[i, j, :] = p_values

        if is_lag_analysis:
            return fc_matrix, lags
        return fc_matrix

    def _apply_measure_windows(self, time_series_set):
        """
        Apply the measure windows to the time series.

        Args:
            time_series: List of time series.

        Returns:
            A list of time series with measure windows applied.
        """
        filtered_series = []
        for ts in time_series_set:
            filtered_series.append(self._apply_measure_windows_ts(filtered_ts))
        return filtered_series

    def _apply_measure_windows_ts(self, ts):
        """
        Apply the measure windows to the time series.

        Args:
            time_series: a single time series.

        Returns:
            A time series with measure windows applied.
        """
        
        filtered_ts = []
        for start, end in self.measure_windows:
            filtered_ts.extend(ts[start:end])
        return filtered_ts


    def _apply_measure_windows_and_lag_ts(self, ts1, ts2, lag, normalize=True, plot_rate=0.1):
        """
        Apply the measure windows to the time series. AND lag 
        ts2, and prevent artifacts in the correlation calculation
        via bleeding between the two time series.

        Args:
            time_series: a single time series.

        Returns:
            A time series with measure windows applied.
        """
        
        filtered_ts1 = []
        filtered_ts2 = []
        for start, end in self.measure_windows:
            ts_subsections1 = ts1[start:end]
            ts_subsections2 = ts2[start:end]
            if normalize: # normalize both to the same max
                ts_subsections1 = ts_subsections1 / np.max(ts_subsections1)
                ts_subsections2 = ts_subsections2 / np.max(ts_subsections2)
                
            # apply lag to ts2
            ts_subsections2 = ts_subsections2[lag:]
            ts_subsections1 = ts_subsections1[:len(ts_subsections2)]
            filtered_ts1.extend(ts_subsections1)
            filtered_ts2.extend(ts_subsections2)

        if random.random() < plot_rate:
            # plot the time series    
            plt.plot(filtered_ts1, label='ts1')
            plt.plot(filtered_ts2, label='ts2')
            plt.title(f'Lag: {lag}')
            plt.legend()
            plt.show()
        

        return filtered_ts1, filtered_ts2
