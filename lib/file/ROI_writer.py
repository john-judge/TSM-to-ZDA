import numpy as np


class ROIFileWriter:
    """ Writes ROI data to DAT file to be loaded into PhotoZ """
    def __init__(self):
        self.all_regions = None
        self.regions_by_pixel = None

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

    def get_regions_by_pixel(self, limit=None):
        regions = self.regions_by_pixel
        if limit is not None:
            regions = regions[:limit]
        return regions

    def get_regions(self, limit=None):
        regions = self.all_regions
        if limit is not None:
            regions = regions[:limit]
        return regions

    def export_clusters(self, filename, labels, sampled_points, w, limit=None):
        regions = self.convert_clusters_to_roi_list(labels, sampled_points, w)
        self.write_regions_to_dat(filename, regions, limit=limit)
        if limit is not None:
            regions = regions[:limit]
        return regions

    def convert_clusters_to_roi_list(self, cluster_labels, sampled_points, w):
        n_regions = max(cluster_labels)
        regions = [[] for _ in range(n_regions + 1)]
        self.regions_by_pixel = [[] for _ in range(n_regions + 1)]
        points_seen = {}
        for i in range(len(cluster_labels)):
            if cluster_labels[i] <= n_regions:
                pt = sampled_points[i, 1] * w + sampled_points[i, 0]
                if pt not in points_seen:
                    regions[cluster_labels[i]].append(pt)
                    self.regions_by_pixel[cluster_labels[i]].append([sampled_points[i, 0],
                                                                     sampled_points[i, 1]])
                    points_seen[pt] = True
        self.all_regions = regions
        return regions

    def write_regions_to_dat(self, filename, regions, limit=None):
        """ Regions as a doubly-nested list """
        if limit is not None:
            regions = regions[:limit]
        with open(filename, 'w') as f:
            f.write(str(len(regions)) + "\n")
            for i in range(len(regions)):
                f.write(str(i) + "\n")
                f.write(str(len(regions[i]) + 1) + "\n")  # +1 for PhotoZ reason
                f.write(str(i) + "\n")  # needed for unknown reason
                for px in regions[i]:
                    f.write(str(px) + "\n")
        print("Regions written to:", filename)
