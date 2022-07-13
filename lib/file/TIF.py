import matplotlib.pyplot as plt
import numpy as np
from lib.utilities import *


class TIFArrayFile:
    """ A TIF file from disk """
    def __init__(self, filename, dic_dir, cam_settings, binning, show_image=False):
        self.filename = filename
        self.dic_dir = dic_dir
        self.data = None
        self.slic = None
        self.loc = None
        self.img_type = None

        self.cam_settings = cam_settings
        self.binning = binning
        self.open_file(show_image=show_image)

    def open_file(self, show_image=False):
        if self.filename.endswith(".tif"):
            sd = Dataset(self.dic_dir + self.filename)
            sd.clip_data(y_range=self.cam_settings['cropping'],
                         t_range=[0, 1])
            sd.bin_data(binning=self.binning)
            self.data = sd.get_data()
            meta = sd.get_meta()
            self.slic = meta['slice_number']
            self.loc = meta['location_number']
            self.img_type = meta['img_type']

            self.data = self.data[0, 0, :, :]
            if show_image:
                plt.imshow(self.data,
                           cmap="gray")
        else:
            print("Not a .TIF file:", self.filename)

    def get_data(self):
        return self.data

    def get_meta(self):
        return {
            'slice_number': self.slic,
            'location_number': self.loc,
            'img_type': self.img_type
        }