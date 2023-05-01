import time
import os
import math
import numpy as np
import cv2
import pandas as pd
import pyautogui as pa
import shutil
import imageio
from PIL import Image, ImageDraw

from lib.auto_GUI.auto_GUI_base import AutoGUIBase
from lib.auto_GUI.auto_DAT import AutoDAT
from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ
from lib.analysis.laminar_dist import *
from lib.file.TIF import *
from lib.analysis.align import ImageAlign
from lib.utilities import *


""" Input: DIC images (fluorescent RLI and DIC) 
    Allows user to draw ROIs, aligns to PhotoZ data
    Output: generate ROI .dat files for PhotoZ 
"""

class ImageDrawToROI:
    """ Perform ROI drawing for all slic/loc in this data dir """
    def __init__(self, data_dir, camera_program=4):

        # data_dir must contain zda in 'selected_zda' subdir and images in 'dic' dir
        self.data_dir = data_dir
        self.dic_dir = data_dir + "/dic/"
        self.selected_zda_dir = data_dir + "/selected_zda/"
        self.avoided_subdir = ['notUsable', 'mm_hidden']

        # load all images in dic dir
        self.image_data = {}
        self.binning = int(2048 / 400)  # if want size similar to RLI
        self.camera_program = camera_program

        # align RLI and DIC and record the RLI's image boundaries within the DIC image.
        self.dic_coordinates = [[8, 6], [80, 12], [2, 69], [76, 74]]
        self.im_align = ImageAlign(self.dic_coordinates)

    def load_dic_images(self, dic_dir, slice_target_id=None):
        cam_settings = CameraSettings().get_program_settings(self.camera_program)
        TIFLoader(dic_dir,
                  cam_settings,
                  self.binning,
                  crop=False,
                  flip_horiz=True).load_files(self.image_data, slice_target=slice_target_id)

    def clear_dic_images(self):
        self.image_data.clear()

    def draw_ROI(self, roi_filename_prefixes, which_image_to_annotate, slice_target_id=None):
        """ roi_filename_prefixes is a list of files to draw and write ROI to disk,
            which_image_to_annotate is a list of ['f', 'e',....] specifying what DIC image to draw on
        """
        image_data = self.image_data
        for subdir, dirs, files in os.walk(self.data_dir):
            if any([x in subdir for x in self.avoided_subdir]):
                continue
            if 'dic' in dirs and 'selected_zda' in dirs:
                dic_dir = subdir + "/dic/"
                selected_zda_dir = subdir + "/selected_zda/"
                already_drawn_slic_loc = {}
                # take selected zda and expand into separate subdir for each zda file
                for analysis_rec_dir in os.listdir(selected_zda_dir):
                    for zda_file in os.listdir(selected_zda_dir + analysis_rec_dir + "/"):
                        if zda_file.endswith('.zda'):
                            rec_id = zda_file.split('.')[0]
                            slic_id, loc_id, _ = [int(x) for x in rec_id.split("_")]
                            print(rec_id)
                            # output dir
                            output_dir = selected_zda_dir + "/analysis" + rec_id + "/"
                            try:
                                os.makedirs(output_dir)
                            except Exception as e:
                                pass

                            # read in 8-bit single TIF images to array, apply same cropping/binning
                            self.load_dic_images(dic_dir)

                            # align RLI and DIC and record the RLI's image boundaries within the DIC image.
                            dic_coordinates = [[8, 6], [80, 12], [2, 69], [76, 74]]
                            img_aligner = ImageAlign(dic_coordinates)

                            for slic in self.image_data:
                                for loc in self.image_data[slic]:

                                    if slic != slic_id or loc != loc_id:
                                        continue

                                    # if already drawn, no need to ask user again
                                    if str(slic_id) + "_" + str(loc_id) in already_drawn_slic_loc:
                                        # just copy them over
                                        for fn_prefix in roi_filename_prefixes:
                                            src_dir = already_drawn_slic_loc[str(slic_id) + "_" + str(loc_id)]
                                            src_file = src_dir + fn_prefix + ".dat"
                                            shutil.copy(src_file, output_dir + fn_prefix + ".dat")
                                        continue

                                    print(slic, loc)

                                    # DICs
                                    fluor = None
                                    if 'f' in self.image_data[slic][loc]:
                                        fluor = self.image_data[slic][loc]['f']
                                    elif 'fe' in self.image_data[slic][loc]:
                                        fluor = self.image_data[slic][loc]['fe']
                                    # img = self.image_data[slic][loc]['i']

                                    dic_electrode = None
                                    if 'e' in self.image_data[slic][loc]:
                                        dic_electrode = self.image_data[slic][loc]['e']
                                    else:
                                        dic_electrode = fluor

                                    dic_electrode = np.array(dic_electrode, dtype=np.uint8)
                                    orig_arr_shape = dic_electrode.shape

                                    try:
                                        os.makedirs(output_dir)
                                    except OSError:
                                        pass

                                    # visualize for validation
                                    plt.imshow(fluor, cmap='gray')

                                    # ask user to select site of stim and layer/barrel borders
                                    for i in range(len(roi_filename_prefixes)):
                                        fn_prefix = roi_filename_prefixes[i]
                                        img_type = which_image_to_annotate[i]
                                        print("Selecting ROI:", fn_prefix)

                                        draw_on_img = dic_electrode
                                        if img_type == 'f':
                                            draw_on_img = fluor
                                        img_roi, roi_coords = img_aligner.draw_single_roi_on_image(draw_on_img)

                                        img_roi = np.array(img_roi)

                                        for pt in roi_coords:
                                            x, y = pt
                                            plt.plot(x, y, marker="*", color='green')

                                        # transform coordinates -- Actual alignment work done here
                                        roi_coords = img_aligner.transform_from_dic_coordinates({'ROI': roi_coords},
                                                                                                orig_arr_shape)['ROI']

                                        # write to file
                                        roi_filename = output_dir + fn_prefix + ".dat"
                                        img_aligner.write_roi_to_files(roi_coords, roi_filename)
                                        print("Wrote " + fn_prefix + " file to", output_dir)



                                    plt.show()

                                    # mark this slice/loc already drawn
                                    already_drawn_slic_loc[str(slic_id) + "_" + str(loc_id)] = output_dir
                            self.clear_dic_images()
