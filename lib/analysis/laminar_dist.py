import numpy as np
import matplotlib.pyplot as plt


class Line:
    """ An object representing a line in the frame """
    def __init__(self, p1, p2):
        self.x1, self.y1 = p1
        self.x2, self.y2 = p2
        """
        self.slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.y_intercept = self.y1 - self.slope * self.x1
        """

    """
    def get_value_at(self, x):
        return self.get_slope() * x + self.get_y_intercept()

    def get_slope(self):
        return self.slope

    def get_y_intercept(self):
        return self.y_intercept

    def get_intersection(self, line2):
        if line2.get_slope() == self.get_slope():
            return None
        x = (line2.get_y_intercept() - self.get_y_intercept()) / (self.get_slope() - line2.get_slope())
        return [x, self.get_value_at(x)]
    """

    def get_unit_vector(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        length = np.sqrt(x * x + y * y)
        return [x / length, y / length]

    def get_projection_of_segment(self, p1, p2):
        """ get the length of the projection of the segment p1-p2 onto this line """
        uv = self.get_unit_vector()
        input_v = [p2[0] - p1[0], p2[1] - p1[1]]
        return np.abs(uv[0] * input_v[0] + uv[1] * input_v[1])


class LaminarROI:
    """ A layer-like (as opposed to single-cell) ROI spanning the width of a cortex layer or column"""
    def __init__(self, diode_numbers, img_width=80, img_height=80):
        self.w = img_width
        self.h = img_height
        self.points = self.diode_num_to_points(diode_numbers)
        self.center = self.calculate_center_of_mass()

    def get_center(self):
        return self.center

    def get_points(self):
        return self.points

    def calculate_center_of_mass(self):
        avg_pt = [0, 0]
        for pt in self.points:
            avg_pt[0] += pt[0]
            avg_pt[1] += pt[1]
        avg_pt[0] /= len(self.points)
        avg_pt[1] /= len(self.points)
        return avg_pt

    def diode_num_to_points(self, diode_numbers):
        pts = []
        for dn in diode_numbers:
            dn = dn - 1  # to 0-index
            x_px = dn % self.w
            y_px = int(dn / self.w)
            pts.append([x_px, y_px])
        return pts


class LaminarDistance:
    """ Find the distance from stim to center of each ROI along laminar axis """
    def __init__(self, laminar_axis, laminar_rois, stim_pt):
        self.laminar_axis = laminar_axis
        self.laminar_rois = laminar_rois
        self.stim_pt = self.stim_pt

    def get_laminar_dist(self, roi):
        center = roi.get_center()
        proj_dist = self.laminar_axis.get_projection_of_segment(self.stim_pt, center)
        return proj_dist

    def compute_laminar_distances(self):
        dists = []
        for roi in self.laminar_rois:
            dists.append(self.get_laminar_dist(roi))
        return dists


#################### script ####################
# open corners, pick two points p1, p2 that define the edge along which to measure
p1, p2 = # read from file
laminar_axis = Line(p1, p2)

# open all rois as lists of diode numbers, store it in variable rois
rois = # from file
rois = [LaminarROI(r) for r in rois]
# if width is not 80, pull from ZDA file and pass it as img_width argument to LaminarROI(r, img_width=w)

# open stim point roi as a single integer (its diode number) in variable stim_pt
stim_pt = # from file
aux_obj = LaminarROI([stim_pt]).get_points()
stim_pt = aux_obj[0]  # should be a list of len 2, representing px location [x, y]

# run laminar dist computation
laminar_distances = LaminarDistance(laminar_axis, rois, stim_pt)
print(laminar_distances)  # a list of integers with same indexing as rois