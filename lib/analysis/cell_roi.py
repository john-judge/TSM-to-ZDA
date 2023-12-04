import matplotlib.pyplot as plt

from lib.analysis.laminar_dist import *
from lib.analysis.align import *


class OverlapCounterROI:

    def __init__(self, roi_list1, roi_list2, width=80, height=80):
        self.roi_list1 = roi_list1
        self.roi_list2 = roi_list2
        self.w = width
        self.h = height

    def calculate_num_unique_px(self, r):
        """ count number of pixels occupied by roi """
        rmap = {}
        for roi in r:
            for px in roi:
                rmap[px] = True
        return len(rmap.keys())

    def get_num_occupied(self):
        """ Return number of array px occupied by each roi list """
        #total_area = self.w * self.h
        r1 = self.calculate_num_unique_px(self.roi_list1)
        r2 = self.calculate_num_unique_px(self.roi_list2)
        return [r1, r2]

    @staticmethod
    def do_rois_overlap(roi1, roi2):
        for px in roi1:
            if px in roi2:
                return True
        return False

    def get_num_rois_overlap(self):
        n_overlap = 0
        for roi1 in self.roi_list1:
            for roi2 in self.roi_list2:
                if self.do_rois_overlap(roi1, roi2):
                    n_overlap += 1
                    break
        return n_overlap


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

