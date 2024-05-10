import matplotlib.pyplot as plt
from numpy.polynomial import polynomial
import pandas as pd
import numpy as np
from numpy.linalg import LinAlgError


class BaselineCorrection:
    """ Class for trace baseline correction. Module version of code in baseline_proof.ipynb """
    def __init__(self, trace, exclusion_windows=((100,300), (357,552)), 
                 polyorder=8):
        self.trace = trace  # pandas dataframe with 'Pt' and 'ROI#' columns
        self.exclusion_windows = exclusion_windows
        self.polyorder = polyorder
        self.corrected_trace = None
        self.baseline = None

    # fit a polynomial to the trace and subtract it
    def fit_polynomial(self, x, y, t_complete):
        coefs = polynomial.polyfit(x, y, self.polyorder)
        y_fit = polynomial.polyval(t_complete, coefs)
        return y_fit

    def fit_baseline(self, roi, title, plot_no_converge=True):
        trace_cp = self.trace.copy()
        trace_cp = trace_cp.dropna()
        t_complete = np.linspace(0, len(self.trace['Pt']), len(self.trace['Pt']))
        for ew in self.exclusion_windows:
            trace_cp = trace_cp.drop(trace_cp[(trace_cp['Pt'] >= ew[0]) & 
                                      (trace_cp['Pt'] <= ew[1])].index)
        x = trace_cp['Pt']
        y = trace_cp[roi]
        try:
            y_fit1 = self.fit_polynomial(x, y, t_complete)
        except LinAlgError as e:
            print(f"LinAlgError: {e}")
            if plot_no_converge:
                plt.scatter(x, y)
                plt.title(title+ "_" +roi)
                plt.show()
            return None
        corrected_trace = self.trace[roi] - y_fit1

        # insert into trace dataframe
        self.trace.insert(2, 'Baseline_'+roi, y_fit1, True)
        self.trace.insert(2, 'Corrected_'+roi, corrected_trace, True)
        return corrected_trace

    def corrected_trace_with_baseline_plot(self, roi, y_space = 12):
        plt.plot(self.trace[roi], label='Trace')
        plt.plot(self.trace['Baseline_'+roi] + y_space, label='Baseline')
        plt.plot(self.trace['Corrected_'+roi] + 2 * y_space, label='Corrected Trace')
        plt.legend()
        plt.yticks([])
        plt.show()