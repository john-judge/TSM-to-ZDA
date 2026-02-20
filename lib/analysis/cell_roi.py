import matplotlib.pyplot as plt
import numpy as np
import os
import random
import pyautogui as pa

from lib.analysis.laminar_dist import *
from lib.analysis.align import *
from lib.file.ROI_reader import ROIFileReader as ROIFileReaderLegacy
from lib.file.ROI_writer import ROIFileWriter
from lib.analysis.barrel_roi import Barrel_ROI_Creator

from lib.analysis.roi_annotator import MaxSNRROIAnnotator
from ZDA_Adventure.utility import *
from ZDA_Adventure.tools import *
from ZDA_Adventure.measure_properties import TraceProperties


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

    def take_random_sample(self, mask=None):
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
            if not self.do_rois_overlap(mask, potential_roi):
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
            electrode_location=None, stripe_dir_file_option='Slice', stripe_dir_keyword=None, roi_keyword='roi', 
            output_keyword='_output_', do_not_overwrite=False, roi_type='Random',
            roi_file_keyword=None,
            roi_file_pad_zeros=False,
            skip_window_start=0,
            skip_window_width=0,
            measure_window_start=0,
            measure_window_width=0,
            enable_temporal_filter=True,
            enable_spatial_filter=False,
            spatial_filter_sigma=1.0,):
        self.data_dir = data_dir
        self.n_px_per_roi = n_px_per_roi
        self.max_rois = max_rois
        self.electrode_location = electrode_location

        self.stripe_dir_keyword = stripe_dir_keyword
        self.roi_keyword = roi_keyword
        self.output_keyword = output_keyword
        self.do_not_overwrite = do_not_overwrite
        self.roi_type = roi_type  # Random or Band/Stripes or Ladder

        self.roi_file_keyword = roi_file_keyword
        self.roi_file_pad_zeros = roi_file_pad_zeros  # True: pad rec_id before searching for roi files

        self.skip_window_start = skip_window_start
        self.skip_window_width = skip_window_width
        self.measure_window_start = measure_window_start
        self.measure_window_width = measure_window_width

        self.enable_temporal_filter = enable_temporal_filter
        self.enable_spatial_filter = enable_spatial_filter
        self.spatial_filter_sigma = spatial_filter_sigma

        # Ladder
        self.corners_keyword = 'corners'

    def get_roi_input_filenames(self, subdir, rec_id, roi_keyword, shallow_search=False):
        """ Return all files that match the rec_id and the roi_keyword in the subdir folder
         However, roi_files cannot have the trace_type keywords in them 
         Defaults to [None] if no files are found """
        roi_files = []
        keywords_to_exclude = ['amp', 'snr', 'sd', 'latency', 'halfwidth', 'trace', 'stim_time']
        for file in os.listdir(subdir):
            if str(rec_id) in file and roi_keyword in file:
                    if not any(exclude_kw in file for exclude_kw in keywords_to_exclude):
                        roi_files.append(file)
        if not shallow_search:
            # also search in subdirectories of subdir
            for root, dirs, files in os.walk(subdir):
                # prepend the relative path to the file
                relative_path = os.path.relpath(root, subdir)

                for file in files:
                    file_path = os.path.join(relative_path, file)
                    #print("search relative path for ROIs:", relative_path, file_path)
                    if str(rec_id) in file_path and roi_keyword in file_path:
                        if not any(exclude_kw in file_path for exclude_kw in keywords_to_exclude):
                            if file_path not in roi_files:
                                roi_files.append(file_path)
        if len(roi_files) < 1:
            roi_files = [None]
        return roi_files

    def get_roi_filename(self, subdir, roi_idx, file):
        roi_type_short = {"Random": "rand", 
                          "Bands/Stripes": "band", 
                          "Ladder": 'ladder',
                          "3x3 SNR Maximal": "snr3x3",
                          "5x5 SNR Maximal": "snr5x5"}[self.roi_type]
        if roi_idx == "":
            return subdir + '/' + file.split('.dat')[0] +self.output_keyword + "_" + roi_type_short + '.dat'
        return subdir + '/' + file.split('.dat')[0] +self.output_keyword + "_" + roi_type_short +"_" + str(roi_idx) + '.dat'

    def get_stripe_dir_files(self, subdir, file):
        stripe_dir_files = os.listdir(subdir)
        file_prefix = file.split('.dat')[0]
        if self.stripe_dir_keyword is not None:
            stripe_dir_files = [f for f in stripe_dir_files if self.stripe_dir_keyword in f]
        stripe_dir_files = [f for f in stripe_dir_files if (file_prefix in f and f.endswith('.dat'))]
        # append full path
        stripe_dir_files = [subdir + '/' + f for f in stripe_dir_files]
        return stripe_dir_files

    def get_corners_file(self, subdir, file):
        file_prefix = file.split('.dat')[0]
        corner_files = os.listdir(subdir)
        corner_files = [f for f in corner_files if self.corners_keyword in f and f.endswith('.dat')]
        corner_files = [f for f in corner_files if not (self.output_keyword in f)]
        corner_files = [f for f in corner_files if file_prefix in f]
        corner_files = [subdir + '/' + f for f in corner_files]  # append full path
        print("Looking for corners files. Found: " + str(corner_files))
        return corner_files

    def read_corners_file(self, corner_file):
        with open(corner_file, 'r') as f:
            lines = f.readlines() 
        corners = [int(x) for x in lines[4:]] # the last 4 lines are diode numbers of corners
        return corners

    def create_ring_rois(self, barrel_rois, barrel_roi_map, subdir):
        pa.alert("Not implemented.")

    def create_ladder_rois(self, barrel_rois, barrel_roi_map, subdir, file, data_file_map):
        print("Creating ladder ROIs for " + subdir + '/' + file)
        new_rois = {i: [] for i in range(len(barrel_rois))}
        corner_files = self.get_corners_file(subdir, file)
        if len(corner_files) == 0:
            print("No corners file found for " + subdir + '/' + file + ". Skipping.")
            return new_rois
        corners = self.read_corners_file(corner_files[0])
        layer_axes = LayerAxes(corners)
        laminar_axis, laminar_axis_2 = layer_axes.get_layer_axes()

        roi_cr = ROICreator(layer_axes)
        rois = roi_cr.get_rois()  # creates list of LaminarROI objects


        # write these ROIs to file
        output_roi_file = self.get_roi_filename(subdir, "", file)  # no barrel_idx
        if not os.path.exists(output_roi_file) or not self.do_not_overwrite:
            output_roi_file = roi_cr.write_roi_file(output_roi_file, "")

        # append to data_file_map
        subdir_shortened = subdir.split('\\selected_zda')[0]
        if subdir_shortened not in data_file_map:
            data_file_map[subdir_shortened] = {}
        if file not in data_file_map[subdir_shortened]:
            data_file_map[subdir_shortened][file] = []
        data_file_map[subdir_shortened][file].append(output_roi_file)
        
        return output_roi_file
    
    def pad_zeros(self, x, n_digits=2):
        """ Pad zeros to the front of the string integer """
        return '0' * (n_digits - len(str(x))) + str(x)
        
    def create_snr_maximal_rois(self, box_size=3):
        ''' Create ROIs that greedily maximize SNR in box_size x box_size regions within barrel ROIs '''
        pa.alert("We will loop through zda files and process SNR maximal ROIs. Input: roi centers read from" + 
                 " roi files in the format specified in the Auto Exporter tab (except your roi file option"
                 " has been temporarily overridden to Slice_Loc_Rec)")
        data_file_map = {}
        files_created = []
        prev_slic, prev_loc, prev_roi_file = None, None, None
        slic, loc, rec = None, None, None
        roi_file = None
        for subdir, dirs, files in os.walk(self.data_dir):

            msra = MaxSNRROIAnnotator(subdir, roi_scan_radius=(box_size-1)//2,
                                      measure_window_start=self.measure_window_start,
                                      measure_window_width=self.measure_window_width)

            for file in files:
                
                if file.endswith('.zda'):
                    zda_full_path = subdir + '/' + file

                    prev_slic = slic
                    prev_loc = loc
                    prev_roi_file = roi_file

                    # get rec_id from filename
                    rec_id = file.split('.')[0]
                    slic, loc, rec = rec_id.split('_')

                    if not self.roi_file_pad_zeros:
                        rec_id = '_'.join([str(int(slic)), str(int(loc)), str(int(rec))])  # remove leading zeros
                    else:
                        rec_id = '_'.join([self.pad_zeros(slic), self.pad_zeros(loc), self.pad_zeros(rec)])

                    roi_input_filenames = self.get_roi_input_filenames(subdir, rec_id, self.roi_file_keyword, shallow_search=True)
                    roi_file = roi_input_filenames[0]
                    if roi_file is None:
                        if prev_slic == slic and prev_loc == loc:
                            roi_file = prev_roi_file

                    if roi_file is None:
                        print("No ROI file found for " + subdir + '/' + rec_id + ", and no previous file to fall back on. Skipping.")
                        continue

                    # load file (lists of lists of diode numbers)
                    try:
                        rois = ROIFileReader(subdir + '/' + roi_file).get_roi_list()
                    except ValueError:
                        print("Error reading " + subdir + '/' + roi_file + ". Skipping.")
                        continue
                    print("Creating ROIs for " + subdir + '/' + roi_file)

                    # load zda file 
                    dl = DataLoader(zda_full_path)

                    zda_arr = tools.Polynomial(startPt=self.skip_window_start,
                                                numPt=self.skip_window_width,
                                                Data=zda_arr)
                    
                    zda_arr = dl.get_data(rli_division=False)
                    tools = Tools()
                    if self.enable_temporal_filter:
                        zda_arr = tools.T_filter(Data=zda_arr)
                    if self.enable_spatial_filter:
                        zda_arr = tools.S_filter(Data=zda_arr, sigma=self.spatial_filter_sigma)

                    zda_arr = np.mean(zda_arr, axis=0)  # average across trials
                    new_rois = []
                    for roi in rois:
                        roi_center = roi[0]
                        if len(roi) > 1:
                            roi_center = LaminarROI(roi, input_diode_numbers=False).get_center()
                            
                        x, y = roi_center
                        new_roi = msra._build_max_snr_roi(zda_arr, x, y)
                        new_rois.append(new_roi)

                    # convert pixels to diode numbers
                    roi_cr = ROICreator(None)
                    for i in range(len(new_rois)):
                        new_rois[i] = [roi_cr.convert_point_to_diode_number(px)
                                                    for px in new_rois[i]]
                    
                    print(new_rois)
                    # write new ROIs to file
                    rfw = ROIFileWriter()
                    output_roi_file = self.get_roi_filename(subdir, "", rec_id)
                    rfw.write_regions_to_dat(output_roi_file, new_rois)
                    print("Wrote " + output_roi_file)
                    files_created.append(output_roi_file)
        pa.alert("Created " + str(len(files_created)) + "ROI files:\n" + 
            '\n'.join(files_created))

            
    def create_band_rois(self, barrel_rois, barrel_roi_map, subdir, file):
        new_rois = {i: [] for i in range(len(barrel_rois))}
        str_dir_files = self.get_stripe_dir_files(subdir, file)
        if len(str_dir_files) == 0:
            return new_rois
        barrel_boundary_file = str_dir_files[0]
        br_creator = Barrel_ROI_Creator()

        # and get barrel boundary location
        barrel_boundary = ROIFileReaderLegacy(barrel_boundary_file).get_roi_list()

        # the first ROI should be 2 points along the barrel boundary (to define barrel axis)
        barrel_boundary = LaminarROI(barrel_boundary[0], input_diode_numbers=True).get_points()
        bound1, bound2 = barrel_boundary[0], barrel_boundary[1]
        
        barrel_axis = Line(bound1, bound2)
        new_rois = br_creator.get_striped_rois(barrel_rois, barrel_axis, roi_dimensions=self.n_px_per_roi)

        return new_rois

    def create_rand_rois(self, barrel_rois, barrel_roi_map):
        '''take sample of MAX_ROIS random pixels from barrel ROIs'''
        
        new_rois = {i: [] for i in range(len(barrel_rois))}
        roi_sampler = RandomROISample(self.n_px_per_roi, max_rois=self.max_rois)

        # remove any barrel_rois that are smaller than n_px_per_roi * 5
        barrel_rois = [roi for roi in barrel_rois if len(roi) > self.n_px_per_roi * 5]

        # if barrel_rois is empty, return empty new_rois
        if len(barrel_rois) == 0:
            return new_rois

        nr_map = {}
        if self.n_px_per_roi == 1:
            while(any([len(new_rois[k]) < self.max_rois for k in new_rois])):
                i, j = roi_sampler.get_random_point()
                px_string = str(j) + ',' + str(i)
                if px_string not in barrel_roi_map \
                    or (j,i) in nr_map:
                    continue
                else:
                    barrel_idx = barrel_roi_map[px_string]
                    if len(new_rois[barrel_idx]) < self.max_rois:
                        new_rois[barrel_idx].append([[j, i]])
                    nr_map[(j, i)] = 1
            print(len(new_rois))
            return new_rois
        elif self.n_px_per_roi > 1:
            for i in range(len(barrel_rois)):
                roi_sampler = RandomROISample(self.n_px_per_roi, max_rois=self.max_rois)
                new_rois[i] = roi_sampler.take_random_sample(mask=barrel_rois[i])
            return new_rois

    def create_rois(self):
        data_file_map = {}
        files_created = []
        if self.roi_type == '3x3 SNR Maximal':
            return self.create_snr_maximal_rois(box_size=3)
        elif self.roi_type == '5x5 SNR Maximal':
            return self.create_snr_maximal_rois(box_size=5)
        pa.alert("Input ROI files will be read from:\n" + self.data_dir + "obeying the following rules:\n" +
            "- ROI files must contain the keyword: " + self.roi_keyword + "\n" +
            "- ROI files must end with .dat\n" +
            "- ROI files must NOT contain the keyword: " + self.stripe_dir_keyword + "\n" +
            "- ROI files must NOT contain the keyword: " + self.output_keyword + "\n" +
            "- ROI files must NOT contain the keyword: " + self.corners_keyword + "\n")
        for subdir, dirs, files in os.walk(self.data_dir):

            for file in files:
                if self.roi_keyword in file and file.endswith('.dat') \
                    and self.stripe_dir_keyword not in file \
                        and  self.output_keyword not in file \
                        and self.corners_keyword not in file:

                    # load barrel file (lists of lists of diode numbers)
                    try:
                        barrel_rois = ROIFileReaderLegacy(subdir + '/' + file).get_roi_list()
                    except ValueError:
                        print("Error reading " + subdir + '/' + file + ". Skipping.")
                        continue
                    print("Creating ROIs for " + subdir + '/' + file)

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
                    if self.roi_type == 'Ladder':
                        ladder_roi_filename = self.create_ladder_rois(barrel_rois, barrel_roi_map, subdir, file, data_file_map)
                        continue  # ladder ROI are written to file in create_ladder_rois -> laminar_dist.py -> ROICreator
                    if self.roi_type == 'Random':
                        new_rois = self.create_rand_rois(barrel_rois, barrel_roi_map)
                    elif self.roi_type == 'Bands/Stripes':
                        new_rois = self.create_band_rois(barrel_rois, barrel_roi_map, subdir, file)

                    if new_rois is None:
                        continue

                    # new_rois maps i -> a list of ROIs. remove any empty ROIs
                    for k in new_rois:
                        new_rois[k] = [roi for roi in new_rois[k] if len(roi) > 0]

                    # convert pixels to diode numbers
                    roi_cr = ROICreator(None)
                    for k in new_rois:
                        for i_roi in range(len(new_rois[k])):
                            new_rois[k][i_roi] = [roi_cr.convert_point_to_diode_number(px)
                                                    for px in new_rois[k][i_roi]]
                    
                    print(new_rois)
                    # write each new ROI to a separate file
                    rfw = ROIFileWriter()
                    subdir_shortened = subdir.split('\\selected_zda')[0]
                    if subdir_shortened not in data_file_map:
                        data_file_map[subdir_shortened] = {}
                    data_file_map[subdir_shortened][file] = []
                    for barrel_idx in new_rois:
                        if len(new_rois[barrel_idx]) == 0:
                            continue
                        output_roi_file = self.get_roi_filename(subdir, barrel_idx, file)
                        if not os.path.exists(output_roi_file) or not self.do_not_overwrite:
                            rfw.write_regions_to_dat(output_roi_file, new_rois[barrel_idx])
                            print("Wrote " + output_roi_file)
                            files_created.append(output_roi_file)
                        data_file_map[subdir_shortened][file].append(output_roi_file)
        pa.alert("Created " + str(len(files_created)) + "ROI files:\n" + 
            '\n'.join(files_created))
