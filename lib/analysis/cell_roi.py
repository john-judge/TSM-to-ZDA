import matplotlib.pyplot as plt
import numpy as np
import os
import random
import pyautogui as pa

from lib.analysis.laminar_dist import *
from lib.analysis.align import *
from lib.file.ROI_reader import ROIFileReader
from lib.file.ROI_writer import ROIFileWriter
from lib.analysis.barrel_roi import Barrel_ROI_Creator


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
                            str(width) + " by " + str(height) + " array." +
                            "Continuing but with fewer ROIs.")

        self.px_per_roi = n_px_per_roi
        self.overlap_counter = OverlapCounterROI([], [])
        self.centers = []

    def get_roi_centers(self):
        return self.centers

    def do_rois_overlap(self, r1, r2):
        return self.overlap_counter.do_rois_overlap(r1, r2)

    def get_random_point(self):
        return [
            random.randint(0, self.w-1),
            random.randint(0, self.h-1)
        ]

    def take_random_sample(self):
        roi_list = []

        # track whether we've failed to add any new ROIs recently (due to overlap)
        n_failures = 0

        while len(roi_list) < self.max_rois:

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
            else:
                # track failures to guarantee halting
                n_failures += 1
            if n_failures > int(self.max_rois * 2):
                return roi_list
            
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

class ROIWizard:
    """ 
    A class that helps with ROI creation.
        rw = ROIWizard(self.get_data_dir(), self.roi_wizard_pixels_per_roi, self.roi_wizard_max_rois)
        rw.create_rois()
    """

    def __init__(self, data_dir, n_px_per_roi, max_rois, 
            electrode_location=None, barrel_boundary_file=None, roi_keyword='roi', 
            output_keyword='roi_rand_', do_not_overwrite=True, roi_type='Random'):
        self.data_dir = data_dir
        self.n_px_per_roi = n_px_per_roi
        self.max_rois = max_rois
        self.electrode_location = electrode_location

        # a list of two points on the barrel boundary intersecting at L2/3-L4 and L4-L5 boundaries
        self.barrel_boundary_file = barrel_boundary_file  
        self.roi_keyword = roi_keyword
        self.output_keyword = output_keyword
        self.do_not_overwrite = do_not_overwrite
        self.roi_type = roi_type  # Random or Band/Stripes

    def get_roi_filename(self, subdir, roi_idx, file):
        roi_type_short = 'rand' if self.roi_type == 'Random' else 'band'
        return subdir + '/' + file.split('.dat')[0] +self.output_keyword + "_" + roi_type_short +"_" + str(roi_idx) + '.dat'

    def create_band_rois(self, barrel_rois, barrel_roi_map):
        new_rois = {i: [] for i in range(len(barrel_rois))}
        if self.barrel_boundary_file is None:
            pa.alert("Need to specify barrel boundary location for band ROIs! No band ROIs generated")
            return new_rois
        br_creator = Barrel_ROI_Creator()

        # and get barrel boundary location
        barrel_boundary = ROIFileReader(self.barrel_boundary_file).get_roi_list()

        # the first ROI should be 2 points along the barrel boundary (to define barrel axis)
        barrel_boundary = LaminarROI(barrel_boundary[0], input_diode_numbers=True).get_points()[0]
        
        barrel_axis = Line(stim_point, barrel_boundary)
        new_rois = brc.get_striped_rois(barrel_rois, barrel_axis)  # default: 5 px per stripe

        return new_rois

    def create_rand_rois(self, barrel_rois, barrel_roi_map):
        roi_sampler = RandomROISample(self.n_px_per_roi, max_rois=self.max_rois)

        # take sample of MAX_ROIS random pixels from barrel ROIs
        new_rois = {i: [] for i in range(len(barrel_rois))}
        nr_map = {}
        while(any([len(new_rois[k]) < self.max_rois for k in new_rois])):
            i, j = roi_sampler.get_random_point()
            px_string = str(j) + ',' + str(i)
            if px_string not in barrel_roi_map \
                or (j,i) in nr_map:
                continue
            else:
                barrel_idx = barrel_roi_map[px_string]
                if len(new_rois[barrel_idx]) < self.max_rois:
                    new_rois[barrel_idx].append([j, i])
                nr_map[(j, i)] = 1
        print(len(new_rois))
        return new_rois

    def create_rois(self):
        data_file_map = {}
        files_created = []
        for subdir, dirs, files in os.walk(self.data_dir):

            for file in files:
                if self.roi_keyword in file and file.endswith('.dat'):

                    # load barrel file (lists of lists of diode numbers)
                    barrel_rois = ROIFileReader(subdir + '/' + file).get_roi_list()

                    # convert from diode to pixel
                    barrel_rois = [LaminarROI(roi, input_diode_numbers=True).get_points()
                                for roi in barrel_rois]
                    
                    # map pixel to ROI number
                    barrel_roi_map = {}
                    for i in range(len(barrel_rois)):
                        for px in barrel_rois[i]:
                            px_string = str(px[0]) + ',' + str(px[1])
                            barrel_roi_map[px_string] = i

                    # create new ROIs
                    new_rois = None
                    if self.roi_type == 'Random':
                        new_rois = self.create_rand_rois(barrel_rois, barrel_roi_map)
                    elif self.roi_type == 'Bands/Stripes':
                        new_rois = self.create_band_rois(barrel_rois, barrel_roi_map)

                    # convert pixels to diode numbers
                    roi_cr = ROICreator(None)
                    for k in new_rois:
                        new_rois[k] = [[roi_cr.convert_point_to_diode_number(px)] for px in new_rois[k]]

                    # write each new ROI to a separate file
                    rfw = ROIFileWriter()
                    selected_zda_dir = subdir 
                    subdir_shortened = subdir.split('\\selected_zda')[0]
                    if subdir_shortened not in data_file_map:
                        data_file_map[subdir_shortened] = {}
                    data_file_map[subdir_shortened][file] = []
                    for barrel_idx in new_rois:
                        rand_roi_file = self.get_roi_filename(selected_zda_dir, barrel_idx, file)
                        if not os.path.exists(rand_roi_file) or not self.do_not_overwrite:
                            rfw.write_regions_to_dat(rand_roi_file, new_rois[barrel_idx])
                            print("Wrote " + rand_roi_file)
                            files_created.append(rand_roi_file)
                        data_file_map[subdir_shortened][file].append(rand_roi_file)
        pa.alert("Created " + str(len(files_created)) + "ROI files:\n" + 
            '\n'.join(files_created))
