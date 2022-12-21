import numpy as np
import matplotlib.pyplot as plt


class Line:
    """ An object representing a line in the frame """

    def __init__(self, p1, p2):
        self.x1, self.y1 = p1
        self.x2, self.y2 = p2

    def get_start_point(self):
        return [self.x1, self.y1]

    def get_end_point(self):
        return [self.x2, self.y2]

    def get_line_repr(self):
        return [[self.x1, self.y1], [self.x2, self.y2]]

    def get_length(self):
        dx = self.x1 - self.x2
        dy = self.y1 - self.y2
        return dx * dx + dy * dy

    def is_line_in_bounds(self, w, h):
        """ True if line is within the square w x h"""
        return (0 <= self.x1 < w
                and 0 <= self.y1 < h
                and 0 <= self.x2 < w
                and 0 <= self.y2 < h)

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

    def is_point_at_edge(self, x, y):
        return x == 0 or y == 0 or x == self.w - 1 or y == self.h - 1


class ROICreator:
    """ Given two laminar axes and an ROI width,
        create as many ROIs as possible from start until edge
        The Laminar axes input should be guaranteed
        to be in form [start, edge] vectors. This property
        is guarantteed in LayerAxes.construct_axes method """
    def __init__(self, laminar_axes, width=80, height=80, roi_width=3):
        self.w, self.h = width, height
        self.roi_width = roi_width
        self.axis1, self.axis2 = laminar_axes

    def create_roi_from_bounds(self, perpend):
        roi = []

        distance = round(perpend.get_length(), ndigits=0)

        # start point is where perpend1 starts
        x, y = perpend.get_start_point()

        laminar_walk_direction = self.axis1.get_unit_vector()
        columnar_walk_direction = perpend.get_unit_vector()
        for j in range(distance):
            for i in range(self.roi_width):
                x += laminar_walk_direction[0]
                y += laminar_walk_direction[1]
                roi.append([round(x, ndigits=0), round(y, ndigits=0)])
            # increment down column now
            x += columnar_walk_direction[0]
            y += columnar_walk_direction[1]
        return roi

    def get_rois(self):
        rois = self.create_rois()  # list of list of points

        # convert to list of list of diode numbers
        raise NotImplementedError

        # convert to list of LaminarROI objects
        return rois

    def create_rois(self):
        """ Returns a list of lists of points """
        rois = []

        perpendicular = Line(self.axis1.get_start_point(), self.axis2.get_start_point())

        n_rois_created = 0
        while perpendicular.is_line_in_bounds(self.w, self.h):

            # increment perpendicular
            new_start_pt = perpendicular.get_start_point() + self.axis1.get_unit_vector() * self.roi_width
            new_end_pt = perpendicular.get_end_point() + self.axis2.get_unit_vector() * self.roi_width
            new_perpendicular = Line(new_start_pt, new_end_pt)
            if new_perpendicular.is_line_in_bounds(self.w, self.h):

                # Using a 'walk-along-vectors' method, create roi here
                roi = self.create_roi_from_bounds(perpendicular)
                rois.append(roi)
                n_rois_created += 1
            else:
                break

            perpendicular = new_perpendicular

        return rois


class LaminarDistance:
    """ Find the distance from stim to center of each ROI along laminar axis """

    def __init__(self, laminar_axis, laminar_rois, stim_pt):
        self.laminar_axis = laminar_axis
        self.laminar_rois = laminar_rois
        self.stim_pt = stim_pt

    def get_laminar_dist(self, roi):
        center = roi.get_center()
        proj_dist = self.laminar_axis.get_projection_of_segment(self.stim_pt, center)
        return proj_dist

    def compute_laminar_distances(self):
        dists = []
        for roi in self.laminar_rois:
            dists.append(self.get_laminar_dist(roi))
        return dists


class LayerAxes:
    """ Given four corners, construct a layer axis and a column axis """

    def __init__(self, corners, img_width=80, img_height=80):
        self.corners = corners
        self.w = img_width
        self.h = img_height
        if type(self.corners[0]) == int:
            self.convert_corners_to_px()
        self.layer_axis = None
        self.layer_axis_2 = None
        self.construct_axes()

    def get_layer_axes(self):
        return [self.layer_axis, self.layer_axis_2]

    def get_corners(self):
        return self.corners.get_points()

    def convert_corners_to_px(self):
        self.corners = LaminarROI(self.corners,
                                  img_width=self.w,
                                  img_height=self.h)

    def is_point_at_edge(self, x, y):
        return self.corners.is_point_at_edge(x, y)

    def construct_axes(self):
        """ 2 of the corners will be at the edge(s)
            The segment between these 2 corners should be excluded
            the segment across from segment should be excluded
            The other two are the axes of interest, and we will set them to
            self.layer_axis and self.layer_axis_2 arbitrarily """

        edge_pts = []
        axis_pts = []

        # Which points are on edge(s)?
        for pt in self.get_corners():
            x, y = pt
            if self.is_point_at_edge(x, y) and len(edge_pts) < 2:
                edge_pts.append(pt)
            else:
                axis_pts.append(pt)

        print("edge_pts", edge_pts, "axis_pts", axis_pts)

        # Which points should go together? There are 2 possible arrangements
        # each correct pairing should minimize total segment length
        # let's just look at axis pt 0
        dx0 = axis_pts[0][0] - edge_pts[0][0]
        dy0 = axis_pts[0][1] - edge_pts[0][1]
        dist0 = dx0 * dx0 + dy0 * dy0

        dx1 = axis_pts[0][0] - edge_pts[1][0]
        dy1 = axis_pts[0][1] - edge_pts[1][1]
        dist1 = dx1 * dx1 + dy1 * dy1

        # Important: guarantees that axes are vectors that point
        # from axis start point -> edge point.
        if dist0 < dist1:
            self.layer_axis = Line(axis_pts[0], edge_pts[0])
            self.layer_axis_2 = Line(axis_pts[1], edge_pts[1])
        else:
            self.layer_axis = Line(axis_pts[1], edge_pts[0])
            self.layer_axis_2 = Line(axis_pts[0], edge_pts[1])


class LaminarVisualization:
    """ produce a plot of SNR with the results plotted """

    def __init__(self, snr, stim_point, roi_centers, corners, lines, line_colors, linewidths):
        self.plot_point(stim_point)
        for roi in roi_centers:
            self.plot_point(roi, color='white', marker='v')
        for i in range(len(lines)):
            ln = lines[i]
            self.plot_line(ln[0][0], ln[0][1], ln[1][0], ln[1][1],
                           color=line_colors[i],
                           linewidth=linewidths[i])
        for c in corners:
            self.plot_point(c, color='yellow')
        plt.imshow(snr)
        plt.show()

    def plot_point(self, p, color='red', marker='*'):
        plt.plot(p[0], p[1], color=color, marker=marker)

    def plot_line(self, x1, y1, x2, y2, color, linewidth=3):
        plt.plot([x2, x1], [y2, y1], color=color, linewidth=linewidth)
