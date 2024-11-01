import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class TraceMetrics:
    """ Class to calculate metrics from a trace that are not available in PhotoZ """

    def __init__(self, traces):
        """ Traces is a pandas dataframe with columns: Pt, ROI1(trace), ROI2(trace), ... """
        self.traces = traces

    def get_trace_length(self):
        return len(self.trace)
    
    def get_max_amp_times(self, measure_window=(96, 150), method='linear_interpolation', ms_per_pt=0.5):
        """ Returns the times of the peak in the traces.
            measure_window: window to measure [start, end], in Pts.
            method: 'linear_interpolation' or '<fn>_function_fit' 
            ms_per_pt: time per point in ms."""
        max_amp_times = []
        trace = self.traces[measure_window[0]:measure_window[1]]
        if method == 'linear_interpolation':
            

            # first find max of sliding window of 4 points in trace
            sliding_window_trace = trace.rolling(window=4).mean()  # the index is the right edge of the window
            i_max = sliding_window_trace.idxmax()
            for col_name, i_maxx in i_max.items():
                if col_name != "Pt":
                    i_maxx_start = i_maxx - 3
                    i_maxx_end = i_maxx
                    max_window_trace = trace.loc[i_maxx_start:i_maxx_end, [col_name]]
                    i_max1 = max_window_trace.idxmax().values[0]
                    i_max_less = max(i_max1 - 1, i_maxx_start)
                    i_max_more = min(i_max1 + 1, i_maxx_end)
                    if trace.loc[i_max_less, [col_name]].values[0] > trace.loc[i_max_more, [col_name]].values[0]:
                        i_max2 = i_max_less
                    else:
                        i_max2 = i_max_more
                    # assume the max is between i_max1 and i_max2, and interpolate
                    max1 = trace.loc[i_max1, [col_name]].values[0]
                    max2 = trace.loc[i_max2, [col_name]].values[0]
                    fraction_max2_over_sum = max2 / (max1 + max2)
                    if fraction_max2_over_sum < 0 or fraction_max2_over_sum > 1:
                        raise ValueError("Interpolation fraction out of bounds:", fraction_max2_over_sum, max_window_trace)
                    if i_max2 > i_max1:
                        i_max_interp = float(i_max1) + fraction_max2_over_sum
                    else:
                        i_max_interp = float(i_max1) - fraction_max2_over_sum
                    max_amp_times.append(i_max_interp * ms_per_pt )  # converted to ms            
        
        elif 'function_fit' in method:  # otherwise, use a function fit to extract time of peak
            raise ValueError('Method not implemented')
        
        return max_amp_times # already ms converted
    
    def show_traces(self, measure_window=None, legend=True, ms_per_pt=0.5, colors=None, 
                    stim_time=None, headroom=0.4, ylim=None, save_path=None):
        """ Plots the traces. By default stack all traces in the same plot """
        traces = self.traces
        if measure_window is not None:
            traces = self.traces[measure_window[0]:measure_window[1]]
        last_max = 0
        if colors is None:
            colors=['r', 'b', 'g', 'y', 'm', 'c', 'k']
        i_color = 0
        for col_name in traces.columns:
            if col_name != "Pt":
                plt.plot(traces["Pt"] * ms_per_pt, 
                         traces[col_name] + last_max, 
                         label=col_name,
                         c=colors[i_color])
                i_color = (i_color + 1) % len(colors)
                if headroom is None:
                    last_max += traces[col_name].max() * 1.05 # with 5% headroom
                else:
                    last_max += headroom
        if stim_time is not None:
            plt.axvline(x=stim_time, color='k', linestyle='--', label='Stimulus')
        plt.xlabel("Time (ms)")
        if ylim is not None:
            plt.ylim(ylim)
        plt.yticks([])
        if legend:
            plt.legend()
        if measure_window is not None:
            plt.xlim(measure_window[0] * ms_per_pt, measure_window[1] * ms_per_pt)

        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        if save_path is not None:
            plt.savefig(save_path)

        plt.show()

    @staticmethod
    def guassian_function(x, a, b, c):
        return a * np.exp(-b * (x - c)**2)
    
    @staticmethod
    def exponential_function(x, a, b, c):
        return a * np.exp(-b * (x - c))
    
    @staticmethod
    def double_exponential_function(x, a1, b1, c1, a2, b2, c2):
        return a1 * np.exp(-b1 * (x - c1)) + a2 * np.exp(-b2 * (x - c2))
    
    @staticmethod
    def alpha_function(x, a, tau, x_0):
        return a * (x - x_0) * np.exp(-(x - x_0) / tau)
    
    @staticmethod
    def double_alpha_function(x, a1, tau1, x_01, a2, tau2, x_02):
        return a1 * (x - x_01) * np.exp(-(x - x_01) / tau1) + a2 * (x - x_02) * np.exp(-(x - x_02) / tau2)
    
    @staticmethod
    def triple_alpha_function(x, a1, tau1, x_01, a2, tau2, x_02, a3, tau3, x_03):
        return a1 * (x - x_01) * np.exp(-(x - x_01) / tau1) + a2 * (x - x_02) * np.exp(-(x - x_02) / tau2) + a3 * (x - x_03) * np.exp(-(x - x_03) / tau3)
    
    def fit_trace_to_function(self, function_type, measure_window=(98, 200), p0=None, plot=True, headroom=0.2):
        """ Fits a trace to a function and returns the parameters of the function """
        function_map = {'gaussian': self.guassian_function,
                        'exponential': self.exponential_function,
                        'double_exponential': self.double_exponential_function,
                        'alpha': self.alpha_function,
                        'double_alpha': self.double_alpha_function,
                        'triple_alpha': self.triple_alpha_function}
        function = function_map[function_type]
        trace = None
        if 'exponential' in function_type:
            trace = self.traces[:measure_window[1]]
        else:
            trace = self.traces[measure_window[0]:measure_window[1]]
        x_all = trace["Pt"]
        last_max = 0
        fit_metadata = {}
        for col_name in trace.columns:
            if col_name != "Pt":
                y = trace[col_name]

                # if exponential, trim measure window to x(y_max) : end
                if 'exponential' in function_type:
                    y_max = y.max()
                    i_max = y.idxmax()
                    x = x_all[i_max:]
                    y = y[i_max:]
                else:
                    x = x_all

                if p0 is None:
                    if function_type == 'double_alpha':
                        p0 = [0.2, 6, 100, -0.002, 370, 270]
                    elif function_type == 'triple_alpha':
                        p0 = [0.2, 6, 100, -0.002, 370, 270, -1, 2, 100]
                    elif function_type == 'alpha':
                        p0 = [2.0, 4, 80]
                    elif function_type == 'exponential':
                        p0 = [0.3, 0.01, 80]
                    elif function_type == 'double_exponential':
                        p0 = [2.0, 0.01, 80, 0.5, 0.01, 300]
                if plot:
                    plt.plot(x, y + last_max, 
                            label=col_name)
                
                try:
                    popt, pcov = curve_fit(function, x, y, p0=p0)
                except RuntimeError as e:
                    print("Error fitting function to trace:", e)
                    if plot:
                        last_max += trace[col_name].max() * 1.05 # with 5% headroom
                    continue
                y_fit = function(x, *popt)
                if plot:
                    plt.plot(x, y_fit + last_max, 
                            label='fit', linestyle='--')
                    if headroom is None:
                        last_max += trace[col_name].max() * 1.05 # with 5% headroom
                    else:
                        last_max += headroom
                # plt.legend()
                perr = np.sqrt(np.diag(pcov))

                # residual sum of squares
                ss_res = np.sum((y - y_fit) ** 2)

                # total sum of squares
                ss_tot = np.sum((y - np.mean(y)) ** 2)

                # r-squared
                r2 = 1 - (ss_res / ss_tot)
                if r2 > 0:
                    fit_metadata[col_name] = [r2, perr, popt, pcov]
        if plot:
            plt.xlabel("Time (Pt)")
            plt.yticks([])
            plt.show()
        return fit_metadata
    
    def frequency_decomposition(self, measure_window=(98, 200), plot=True, xlim=[20, 1000]):
        """ Decomposes the trace into its frequency components """
        
        trace = self.traces[measure_window[0]:measure_window[1]]
        x = trace["Pt"]
        last_max = 0
        for col_name in trace.columns:
            if col_name != "Pt":
                y = trace[col_name]
                yf = np.fft.fft(y)
                N = len(yf)
                plot_start_pt = N // 2
                xf = np.fft.fftfreq(N, 0.5) * 1000
                if plot:
                    plt.plot(xf[:plot_start_pt], 
                             2.0/N * np.abs(yf[:plot_start_pt]) + last_max, 
                             label=col_name)
                    last_max += .3
        plt.xlim(xlim)
        plt.xlabel("Frequency (Hz)")
        plt.show()
    