import numpy as np
import pandas as pd


class DATArrayFile:
    """ A DAT file representing a PhotoZ array (e.g. SNR or Amp map) """
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.open_file()

    def open_file(self):
        self.data = np.fromfile(self.filename,
                                dtype=np.float64,
                                sep='\t')
        length = int(self.data.shape[0] / 2)
        self.data = self.data.reshape((length, 2))[:, 1]
        square_side = int(np.sqrt(length))
        self.data = self.data.reshape((square_side, square_side))

    def get_data(self):
        return self.data

    def normalize(self):
        self.data = self.data - np.min(self.data)
        self.data = self.data / np.max(self.data)

class TracesDAT:
    """ A DAT file representing traces for several ROIs """

    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.open_file()

    def open_file(self):
        self.data = pd.read_csv(self.filename, sep='\t', header=0, index_col=0)

    def get_data(self):
        return self.data