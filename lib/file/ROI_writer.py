import numpy as np


class ROIFileWriter:
    """ Writes ROI data to DAT file to be loaded into PhotoZ """
    def __init__(self):
        pass

    """ Format:
    < # ROIs >
    < Region #1 index (0) >
    < Region #1 size >
    < Region #1 list start >
    ...
    < Region #1 list end >
    < Region #2 index (1) >
    < Region #2 size >
    < Region #2 list start >
    ...
    < Region #2 list end >
    ...
    """

    def export_clusters(self, filename, labels, sampled_points, w):
        regions = self.convert_clusters_to_roi_list(labels, sampled_points, w)
        self.write_regions_to_dat(filename, regions)

    def convert_clusters_to_roi_list(self, cluster_labels, sampled_points, w):
        n_regions = max(cluster_labels)
        regions = [[] for _ in range(n_regions + 1)]
        points_seen = {}
        for i in range(len(cluster_labels)):
            pt = sampled_points[i, 1] * w + sampled_points[i, 0]
            if pt not in points_seen:
                regions[cluster_labels[i]].append(pt)
                points_seen[pt] = True
        return regions

    def write_regions_to_dat(self, filename, regions):
        """ Regions as a doubly-nested list """
        i = 0
        with open(filename, 'w') as f:
            f.write(str(len(regions)) + "\n")
            for i in range(len(regions)):
                f.write(str(i) + "\n")
                f.write(str(len(regions[i])) + "\n")
                for px in regions[i]:
                    f.write(str(px) + "\n")
