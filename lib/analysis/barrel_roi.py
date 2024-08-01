from lib.analysis.cell_roi import RandomROISample
from lib.analysis.laminar_dist import *



class Barrel_ROI_Creator():

    def __init__(self, max_rois=100):
        self.max_rois = max_rois

    def get_rand_roi_filename(self, subdir, barrel_idx, file):
        return subdir + '/' + file.split('.dat')[0] +'ROIs-rand_' + str(barrel_idx) + '.dat'
    
    def get_stripe_roi_filename(self, subdir, barrel_idx, file):
        return subdir + '/' + file.split('.dat')[0] +'ROIs-stripe_' + str(barrel_idx) + '.dat'
    
    def create_barreL_roi_map(self, barrel_rois):
        barrel_roi_map = {}
        for i in range(len(barrel_rois)):
            for px in barrel_rois[i]:
                px_string = str(px[0]) + ',' + str(px[1])
                barrel_roi_map[px_string] = i
        return barrel_roi_map
    
    def get_rand_rois(self, barrel_rois, roi_dimensions=1):
        """ Creates random circular rois in the barrel roi. Barrel ROI is list of list of [x, y] points that define the barrel.
            Returns list of rois. """
        barrel_roi_map = self.create_barreL_roi_map(barrel_rois)

        new_rois = {i: [] for i in range(len(barrel_rois))}
        nr_map = {}

        roi_sampler = RandomROISample(roi_dimensions)
        while(any([len(new_rois[k]) < self.max_rois for k in new_rois])):
                i, j = roi_sampler.get_random_point()
                px_string = str(j) + ',' + str(i)
                if px_string not in barrel_roi_map \
                    or (j,i) in nr_map:
                    continue
                else:
                    barrel_idx = barrel_roi_map[px_string]
                    if len(new_rois[barrel_idx]) < self.max_rois:
                        new_rois[barrel_idx].append([j, i])
                    nr_map[(j, i)] = 1
        return new_rois
    
    def get_barrel_idx_of_point(self, barrel_roi_map, px):
        px_string = str(px[0]) + ',' + str(px[1])
        if px_string not in barrel_roi_map:
            return None
        return barrel_roi_map[px_string]
    
    def get_ring_rois(self, stim_point, num_rings=3, roi_dimensions=5, h=80, w=80):
        """ Creates concentric ring rois surrounding the stim_point. """

        # format of output is barrel_idx: [roi1, roi2, ...]
        # where roi1, roi2, ... are lists of [x, y] points that define the roi
        new_rois = {i: [] for i in range(num_rings)}

        for i in range(h):
            for j in range(w):
                dist = Line(stim_point, [j, i]).get_length()

                # which ring is this point in?
                ring_idx = np.abs(int(dist / roi_dimensions))
                if ring_idx >= num_rings:
                    continue
                new_rois[ring_idx].append([j, i])
        return new_rois

    def get_striped_rois(self, barrel_rois, barrel_axis:Line, roi_dimensions=5, h=80, w=80):
        """ Creates striped rois perpendicular to the given barrel axis"""

        barrel_roi_map = self.create_barreL_roi_map(barrel_rois)

        # format of output is barrel_idx: [roi1, roi2, ...]
        # where roi1, roi2, ... are lists of [x, y] points that define the roi
        new_rois = {i: [] for i in range(len(barrel_rois))}

        # method: loop over all points. Calculate its distance along the barrel axis and which barrel it is in
        # then add it to the roi whose range it falls into. 
        # ROIs are in the order of shortest to longest distance along the barrel axis
        reference_point = barrel_axis.get_end_point()

        for i in range(h):
            for j in range(w):

                dist = barrel_axis.get_displacement_along_segment(reference_point, [j, i])

                # which barrel is this point in?
                barrel_idx = self.get_barrel_idx_of_point(barrel_roi_map, [j, i])
                if barrel_idx is None:
                    continue
                roi_idx = np.abs(int(dist / roi_dimensions))
                while roi_idx >= len(new_rois[barrel_idx]):
                    new_rois[barrel_idx].append([])
                new_rois[barrel_idx][roi_idx].append([j, i])

        return new_rois


        