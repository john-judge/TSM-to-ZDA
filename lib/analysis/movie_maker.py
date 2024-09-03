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

from lib.auto_GUI.auto_PhotoZ import AutoPhotoZ


class MovieMaker:
    """ Make a series of measure windows from PhotoZ into a movie """

    def __init__(self, data_dir, start_frame, end_frame, frame_step_size, overwrite_existing, ms_per_frame=0.5) -> None:
        self.data_dir = data_dir
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_step_size = frame_step_size
        self.overwrite_existing = overwrite_existing
        self.ms_per_frame = ms_per_frame

    def are_all_frames_present(self, output_dir, start_frame, end_frame, frame_step_size):
        for frame in range(start_frame, end_frame+1, frame_step_size):
            filename = output_dir + str(frame) + ".jpg"
            if not os.path.exists(filename):
                return False
        return

    def make_movie(self):

        pa.alert("Make sure PhotoZ is initalized, maximized, and the color bound is set to 1." + \
                 " In the PhotoZ Array tab, Nor2ArrayMax and Trace boxes should be turned off." + \
                 "\n\nMovieMaker will begin by estimating and setting the global color bound to the max SNR for " + \
                    "the entire recording. This will be done for each recording in the data directory." + \
                    " \n\nPress OK to continue.")
        
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
                    time.sleep(13)

                    # estimate the SNR max across all frames
                    aPhz.set_measure_window(self.start_frame, 
                                            self.end_frame+1 - self.start_frame,
                                            sleep_time_window_change=17)
                    filename = aPhz.save_background()
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
                
                    # turn frames into movies
                    images = []
                    img_filenames = []
                    for frame in range(self.start_frame, self.end_frame+1, self.frame_step_size):
                        filename = output_dir + str(frame) + ".jpg"
                        if self.overwrite_existing or not os.path.exists(filename):
                            # change frame
                            aPhz.set_measure_window(frame, None)

                            # export this frame
                            aPhz.save_map_jpeg(filename)
                            print("File created:", filename)

                        try:
                            images.append(imageio.imread(filename))
                            img_filenames.append(filename)
                        except Exception as e:
                            pass

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

    def add_time_annotations(self, movie_filename, start_frame, frame_step_size, img_filenames):
        # add time annotations
        frames = []
        final_images = []
        t_frame = 0

        for filename in img_filenames:
            img = cv2.imread(filename)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.putText(img, str(t_frame)[:3] + " ms",
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
            imageio.mimsave(movie_filename, final_images)
            print("CREATED ANNOTATED MOVIE:", annotated_movie_filename)
        except Exception as e:
            print("Not creating annotated movie for " + movie_filename)
            print(e)





