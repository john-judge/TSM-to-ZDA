import matplotlib.pyplot as plt
import numpy as np
import random

from lib.analysis.laminar_dist import *
from lib.analysis.align import *


class OverlapCounterROI:
    """ Counts ROIs, finds their overlap """

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


class RandomROISample:
    """ An ROI object that creates random samples of specified size.
        Max ROIs is specified, but as many as possible under the limit are created."""

    def __init__(self, n_px_per_roi, max_rois=100, width=80, height=80):
        self.w = width
        self.h = height
        self.max_rois = max_rois
        if max_rois * n_px_per_roi > self.w * self.h:
            print(str(max_rois) +
                            " ROIs each of " +
                            str(n_px_per_roi) + " pixels is too large for " +
                            str(width) + " by " + str(height) + " array.")

        self.px_per_roi = n_px_per_roi
        self.overlap_counter = OverlapCounterROI([], [])
        self.centers = []

    def get_roi_centers(self):
        return self.centers

    def do_rois_overlap(self, r1, r2):
        return self.overlap_counter.do_rois_overlap(r1, r2)

    def get_random_point(self):
        return [
            random.randint(0, self.w),
            random.randint(0, self.h)
        ]

    def take_random_sample(self):
        roi_list = []

        # track whether we've failed to add any new ROIs recently (due to overlap)
        previous_roi_failures = [False]

        while len(roi_list) < self.max_rois:
            if all(previous_roi_failures):
                return roi_list

            # randomly sample and look for overlaps.
            center = self.get_random_point()
            potential_roi = self.create_circle_roi(center)

            failure = False
            for roi in roi_list:
                if self.do_rois_overlap(roi, potential_roi):
                    failure = True
                    break
            if not failure:
                roi_list.append(potential_roi)
                self.centers.append(center)
            previous_roi_failures.append(failure)

            # we only care about tracking the last MAX_ROIS // 2 attempts
            allowed_failures = int(self.max_rois / 2)
            if len(previous_roi_failures) > allowed_failures:
                previous_roi_failures = previous_roi_failures[:allowed_failures]

        return roi_list

    def create_circle_roi(self, center):
        """ Create an ROI of the px num located at center"""
        dist_matrix = np.zeros((self.w, self.h))
        n_smallest_distances = []
        for i in range(self.w):
            for j in range(self.h):
                d = Line([i, j], center).get_length()
                dist_matrix[i][j] = d
                if len(n_smallest_distances) < 1 or d < n_smallest_distances[-1]:
                    n_smallest_distances.append(d)
                    n_smallest_distances.sort()
                    if len(n_smallest_distances) > self.px_per_roi:
                        n_smallest_distances.pop()

        eff_radius = n_smallest_distances[-1]
        roi = []
        for i in range(self.w):
            for j in range(self.h):
                if dist_matrix[i][j] <= eff_radius:
                    roi.append([i, j])
                if len(roi) >= self.px_per_roi:
                    return roi[:self.px_per_roi]
        return roi[:self.px_per_roi]



