import time
import os
import cv2
import numpy as np
import pandas as pd
import pyautogui as pa
import shutil
import imageio
from PIL import Image, ImageDraw
import random
import matplotlib.pyplot as plt
from matplotlib.figure import figaspect

from ZDA_Adventure.maps import *
from ZDA_Adventure.tools import *
from ZDA_Adventure.utility import *
from ZDA_Adventure.measure_properties import *

from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ


class MovieMaker:
    """ Make a series of measure windows from PhotoZ into a movie """

    def __init__(self, data_dir, start_frame, end_frame, frame_step_size,
     overwrite_existing, headless_mode, skip_window_start=0, skip_window_width=0, ms_per_frame=0.5, progress=None, **kwargs) -> None:
        self.data_dir = data_dir
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_step_size = frame_step_size
        self.overwrite_existing = overwrite_existing
        self.headless_mode = headless_mode
        self.skip_window_start = skip_window_start
        self.skip_window_width = skip_window_width
        self.ms_per_frame = ms_per_frame

        self.progress = progress
        self.stop_event = kwargs['stop_event']

    def are_all_frames_present(self, output_dir, start_frame, end_frame, frame_step_size):
        for frame in range(start_frame, end_frame+1, frame_step_size):
            filename = output_dir + str(frame) + ".jpg"
            if not os.path.exists(filename):
                return False
        return

    def estimate_total_time(self):
        total_time = 0
        for subdir, dirs, files in os.walk(self.data_dir):
            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):
                    total_time += (self.end_frame - self.start_frame) // self.frame_step_size
        return total_time
    
    def load_zda_file(self, filename, baseline_correction=True, spatial_filter=False):
        """ Load a ZDA file and return a numpy array """
        if not os.path.exists(filename):
            print("ZDA file not found: " + filename)
            return None
        if not filename.endswith('.zda'):
            print("File is not a ZDA file: " + filename)
            return None
        # TO DO: enable RLI division by default
        data_loader = DataLoader(filename,
                          number_of_points_discarded=0)
        data = data_loader.get_data(rli_division=False)

        tools = Tools()
        data = tools.T_filter(Data=data)
        if spatial_filter:
            data = tools.S_filter(Data=data, sigma=1)
        if baseline_correction:
            data = tools.Polynomial(startPt=self.skip_window_start,
                                    numPt=self.skip_window_width,
                                    Data=data)
        
        return data
    
    def make_movie_headless(self):
        for subdir, dirs, files in os.walk(self.data_dir):

            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):
                    rec_id = zda_file.split('.')[0]
                    print(rec_id)
                    # movie dir
                    output_dir = subdir + "/analysis" + rec_id + "/"
                    try:
                        os.makedirs(output_dir)
                    except Exception as e:
                        pass
                    if self.stop_event.is_set():
                        return
                    
                    # zda_arr has shape (trials, height, width, num_frames)
                    zda_arr = self.load_zda_file(subdir + "/" + zda_file)
                    print(zda_arr.shape)
                    zda_arr = np.average(zda_arr, axis=0)

                    # create imshows of each frame, normalized to max across movie range
                    images = []
                    img_filenames = []
                    recording_max = np.max(zda_arr[ :, :, self.start_frame:self.end_frame+1]) * 1.05  # 5% headroom
                    for frame in range(self.start_frame, self.end_frame+1, self.frame_step_size):
                        filename = output_dir + str(frame) + ".jpg"
                        if self.overwrite_existing or not os.path.exists(filename):
                            fig, ax = plt.subplots(figsize=figaspect(1))
                            im = ax.imshow(zda_arr[:, :, frame], 
                                            vmin=0, vmax=recording_max, 
                                            cmap='jet', 
                                            aspect='auto')
                            ax.axis('off')
                            plt.tight_layout()
                            plt.savefig(filename, dpi=150)
                            plt.close(fig)
                            print("File created:", filename)
                            if self.stop_event.is_set():
                                return

                        try:
                            images.append(imageio.imread(filename))
                            img_filenames.append(filename)
                        except Exception as e:
                            pass
                        self.progress.increment_progress_value(1)
                    # create gif
                    created_movie = False
                    movie_filename = output_dir + rec_id + 'movie.gif'
                    try:
                        imageio.mimsave(movie_filename, images)
                        print("CREATED MOVIE:", rec_id + 'movie.gif')
                        created_movie = True
                    except Exception as e:
                        if not created_movie:
                            print("Not creating movie for " + rec_id)
                        print(e)
                    self.add_time_annotations(movie_filename, self.start_frame, self.frame_step_size, img_filenames)
        self.progress.complete()

    def make_movie(self):

        self.progress.set_current_total(self.estimate_total_time(), unit='frames')

        if not self.headless_mode:
            pa.alert("Make sure PhotoZ is initalized, maximized, and the color bound is set to 1." + \
                    " In the PhotoZ Array tab, Nor2ArrayMax and Trace boxes should be turned off." + \
                    "\n\nMovieMaker will begin by estimating and setting the global color bound to the max SNR for " + \
                        "the entire recording. This will be done for each recording in the data directory." + \
                        " \n\nPress OK to continue.")
        else:
            print("Running in headless mode... PhotoZ not needed.")
            self.make_movie_headless()
            return
        
        current_color_bound_setting = 1.0
        for subdir, dirs, files in os.walk(self.data_dir):

            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):

                    rec_id = zda_file.split('.')[0]
                    print(rec_id)
                    # movie dir
                    output_dir = subdir + "/analysis" + rec_id + "/"
                    try:
                        os.makedirs(output_dir)
                    except Exception as e:
                        pass
                    if self.stop_event.is_set():
                        return

                    # determine if we are even missing any jpg'd frames
                    need_to_open_zda = True
                    for frame in range(self.start_frame, self.end_frame+1, self.frame_step_size):
                        filename = output_dir + str(frame) + ".jpg"
                        if not os.path.exists(filename):
                            need_to_open_zda = True
                            break
                    if not need_to_open_zda and not self.overwrite_existing:
                        continue

                    recording_max_snr = 3.0  # should get changed

                    aPhz = AutoPhotoZ(data_dir=subdir)
                    # open the PhotoZ file
                    aPhz.select_PhotoZ()

                    print("\n\nOpening", zda_file)
                    aPhz.open_zda_file(subdir + "/" + zda_file)
                    if self.stop_event.is_set():
                        return
                    time.sleep(13)

                    # estimate the SNR max across all frames
                    aPhz.set_measure_window(self.start_frame, 
                                            self.end_frame+1 - self.start_frame,
                                            sleep_time_window_change=17)
                    filename = aPhz.save_background()
                    if self.stop_event.is_set():
                        return
                    print("Saved intermed_snr_df file:", filename)
                    if filename is not None:  # otherwise, sticks with default rec max

                        # open Data.dat and read in the array max
                        intermed_snr_df = pd.read_csv(filename, 
                                                    sep='\t', 
                                                    header=None, 
                                                    names=['Index',  'Values'])
                        recording_max_snr = intermed_snr_df['Values'].max()

                        recording_max_snr *= 1.05  # 5% higher for headroom
                        recording_max_snr = round(recording_max_snr, 2)

                    # set the normalization to be consistent across entire video
                    aPhz.set_color_upper_bound(recording_max_snr, current_color_bound_setting)
                    print("Moved color upper bound from", current_color_bound_setting, "to", recording_max_snr)
                    current_color_bound_setting = recording_max_snr

                    # set measure window width to 1
                    aPhz.set_measure_window(None, self.frame_step_size, sleep_time_window_change=17)
                    if self.stop_event.is_set():
                        return
                    # turn frames into movies
                    images = []
                    img_filenames = []
                    for frame in range(self.start_frame, self.end_frame+1, self.frame_step_size):
                        filename = output_dir + str(frame) + ".jpg"
                        if self.overwrite_existing or not os.path.exists(filename):
                            # change frame
                            aPhz.set_measure_window(frame, None)
                            if self.stop_event.is_set():
                                return

                            # export this frame
                            aPhz.save_map_jpeg(filename)
                            print("File created:", filename)
                            if self.stop_event.is_set():
                                return

                        try:
                            images.append(imageio.imread(filename))
                            img_filenames.append(filename)
                        except Exception as e:
                            pass
                        self.progress.increment_progress_value(1)

                    # create gif
                    created_movie = False
                    movie_filename = output_dir + rec_id + 'movie.gif'
                    try:
                        imageio.mimsave(movie_filename, images)
                        print("CREATED MOVIE:", rec_id + 'movie.gif')
                        created_movie = True

                    except Exception as e:
                        if not created_movie:
                            print("Not creating movie for " + rec_id)
                        print(e)
                    self.add_time_annotations(movie_filename, self.start_frame, self.frame_step_size, img_filenames)
        self.progress.complete()

    def add_time_annotations(self, movie_filename, start_frame, frame_step_size, img_filenames):
        # add time annotations
        frames = []
        final_images = []
        t_frame = 0

        for filename in img_filenames:
            img = cv2.imread(filename)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.putText(img, str(round(t_frame,1)) + " ms",
                (5, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255)
            )
            t_frame += (frame_step_size / 2)
            cv2.imwrite(filename, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

            final_images.append(imageio.imread(filename))

        annotated_movie_filename = movie_filename.split(".")[0] + "_annotated.gif"
        try:
            imageio.mimsave(annotated_movie_filename, final_images)
            print("CREATED ANNOTATED MOVIE:", annotated_movie_filename)
        except Exception as e:
            print("Not creating annotated movie for " + movie_filename)
            print(e)





