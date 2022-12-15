import numpy as np


class ROIFileReader:
    """ Reads ROI data from PhotoZ dat file, as diode numbers """
    def __init__(self, filename):
        self.rois = []
        self.read_file(filename)

    """ Format:
    < # ROIs >
    < Region #1 index (0) >
    < Region #1 size >
    < Region #1 index (0) >   needed for unknown reason
    < Region #1 list start >
    ...
    < Region #1 list end >
    < Region #2 index (1) >
    < Region #2 size >
    < Region #2 index (1) >   needed for unknown reason
    < Region #2 list start >
    ...
    < Region #2 list end >
    ...
    """
    def get_roi_list(self):
        return self.rois

    def read_file(self, filename):
        """ populates rois as a doubly-nested
            list of diode numbers from file
        """
        with open(filename, 'r') as f:
            lines = f.readlines()
            num_regions = int(lines[0])
            # print("File has", num_regions, "regions.")
            i = 1
            for j in range(num_regions):
                region_size = int(lines[i+1]) - 1
                # print("Region has", region_size, "pixels")
                i += 3  # skip index and other extra line
                next_region = []
                for k in range(region_size):
                    next_region.append(int(lines[i]))
                    # print(lines[i], "(i = " + str(i) + ")")
                    i += 1
                self.rois.append(next_region)
            if i < len(lines) - 1:
                print("Unread lines:", lines[i:])
