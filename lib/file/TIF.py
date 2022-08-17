import matplotlib.pyplot as plt
import numpy as np
from lib.utilities import *


class TIFLoader:
    """ Load TIFs from file """
    def __init__(self, dic_dir, cam_settings, binning, crop=True, flip_horiz=True):
        self.dic_dir = dic_dir
        self.cam_settings = cam_settings
        self.binning = binning
        self.crop = crop
        self.flip_horiz = flip_horiz

    def load_files(self, target_dict, slice_target=None):

        for filename in os.listdir(self.dic_dir):
            print(filename)
            if filename.endswith(".tif"):

                tif = TIFArrayFile(filename, self.dic_dir,
                                   self.cam_settings,
                                   self.binning,
                                   crop=self.crop,
                                   flip_horiz=self.flip_horiz,
                                   show_image=(str(slice_target) in filename and
                                               'e' in filename))

                img = tif.get_data()
                meta = tif.get_meta()
                slic = meta['slice_number']
                loc = meta['location_number']
                img_type = meta['img_type']

                if slic not in target_dict:
                    target_dict[slic] = {}
                if loc not in target_dict[slic]:
                    target_dict[slic][loc] = {}

                target_dict[slic][loc][img_type] = img


class TIFArrayFile:
    """ A TIF file from disk """
    def __init__(self, filename, dic_dir, cam_settings, binning, crop=True, flip_horiz=True, show_image=False):
        self.filename = filename
        self.dic_dir = dic_dir
        self.data = None
        self.slic = None
        self.loc = None
        self.img_type = None

        self.cam_settings = cam_settings
        self.binning = binning
        self.open_file(show_image=show_image, crop=crop, flip_horiz=flip_horiz)

    def open_file(self, show_image=False, crop=True, flip_horiz=True):
        if self.filename.endswith(".tif"):
            sd = Dataset(self.dic_dir + self.filename)
            sd.clip_data(t_range=[0, 1])
            if crop:
                sd.clip_data(y_range=self.cam_settings['cropping'])
            sd.bin_data(binning=self.binning)
            self.data = sd.get_data()
            meta = sd.get_meta()
            self.slic = meta['slice_number']
            self.loc = meta['location_number']
            self.img_type = meta['img_type']

            self.data = self.data[0, 0, :, :]
            if flip_horiz:
                self.data = np.flip(self.data, axis=1)
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