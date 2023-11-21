import matplotlib.pyplot as plt

from lib.analysis.laminar_dist import *
from lib.analysis.align import *


class SingleCellFinder:

    def __init__(self, snr_map, td_tomato_maps):
        self.snr_map = snr_map
        self.td_tomato_maps = td_tomato_maps

    def take_cross_section_of_arrays(self, i_row, x_limits=None):
        """ i_row is row of SNR map, take corresponding of td_tomato_maps"""
        n, m = self.td_tomato_maps[0].shape
        min_td_row = int(i_row * n / self.snr_map.shape[0])
        max_td_row = int((i_row + 1) * n / self.snr_map.shape[0])

        x0_td, x1_td = None, None
        if x_limits is not None:
            x0, x1 = x_limits
            x0_td = int(x0 / 80 * m)
            x1_td = int(x1 / 80 * m)
            td_tomatos = [np.average(td_map[min_td_row:max_td_row, x0_td:x1_td], axis=0)
                          for td_map in self.td_tomato_maps]
            snr = self.snr_map[i_row, x0:x1]
        else:
            td_tomatos = [np.average(td_map[min_td_row:max_td_row, :], axis=0)
                            for td_map in self.td_tomato_maps]
            snr = self.snr_map[i_row, :]
        return {'snr': snr,
                'td_tomato': td_tomatos,
                 'td_tomato_lines': [min_td_row, max_td_row],
                 'td_tomato_x_limits': [x0_td, x1_td]}

