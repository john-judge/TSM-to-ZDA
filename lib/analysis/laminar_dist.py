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
        """ True if line is within w x h"""
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

    def __init__(self, points, img_width=80, img_height=80, input_diode_numbers=True):
        self.w = img_width
        self.h = img_height
        self.points = points
        if input_diode_numbers:
            self.points = self.diode_num_to_points(points)
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

    def is_point_at_edge(self, x, y, tolerance=2):
        return x <= tolerance or y <= tolerance or \
               x >= self.w - 1 - tolerance or y >= self.h - 1 - tolerance


class ROICreator:
    """ Given two laminar axes and an ROI width,
        create as many ROIs as possible from start until edge
        The Laminar axes input should be guaranteed
        to be in form [start, edge] vectors. This property
        is guarantteed in LayerAxes.construct_axes method """
    def __init__(self, layer_axes, width=80, height=80, roi_width=3):
        self.w, self.h = width, height
        self.roi_width = roi_width
        self.axis1, self.axis2 = layer_axes.get_layer_axes()
        self.n_rois_created = 0
        self.rois = []

    def round_bound_w(self, v):
        """ Round v and keep in width bounds """
        v = round(v)
        v = max(0, v)
        v = min(v, self.w-1)
        return v

    def round_bound_h(self, v):
        """ Round v and keep in height bounds """
        v = round(v)
        v = max(0, v)
        v = min(v, self.h-1)
        return v

    def create_roi_from_bounds(self, perpend):
        roi = []

        distance = round(perpend.get_length())

        # start point is where perpend1 starts
        x, y = perpend.get_start_point()

        laminar_walk_direction = self.axis1.get_unit_vector()
        columnar_walk_direction = perpend.get_unit_vector()
        for j in range(distance):
            for i in range(self.roi_width):
                x += laminar_walk_direction[0]
                y += laminar_walk_direction[1]
                roi.append([self.round_bound_w(x), self.round_bound_h(y)])
            # increment down column now
            x += columnar_walk_direction[0]
            y += columnar_walk_direction[1]
        return roi

    def get_rois(self):
        self.rois = self.create_rois()  # list of list of points

        # convert to list of LaminarROI objects
        self.rois = [LaminarROI(r,
                                img_width=self.w,
                                input_diode_numbers=False) for r in self.rois]
        return self.rois

    def create_rois(self):
        """ Returns a list of lists of points """
        rois = []

        perpendicular = Line(self.axis1.get_start_point(),
                             self.axis2.get_start_point())

        self.n_rois_created = 0
        while perpendicular.is_line_in_bounds(self.w, self.h):

            # increment perpendicular
            s = perpendicular.get_start_point()
            uv = self.axis1.get_unit_vector()
            new_start_pt = [s[0] + uv[0] * self.roi_width,
                            s[1] + uv[1] * self.roi_width]
            e = perpendicular.get_end_point()
            new_end_pt = [e[0] + uv[0] * self.roi_width,
                          e[1] + uv[1] * self.roi_width]
            new_perpendicular = Line(new_start_pt, new_end_pt)

            if new_perpendicular.is_line_in_bounds(self.w, self.h):

                # Using a 'walk-along-vectors' method, create roi here
                roi = self.create_roi_from_bounds(perpendicular)
                rois.append(roi)
                self.n_rois_created += 1
            else:
                break
            perpendicular = new_perpendicular
        return rois

    def convert_point_to_diode_number(self, pt):
        x, y = pt
        dn = y * self.w + x + 1
        return dn

    def write_roi_file(self, subdir, rois_file_prefix):
        pad_n = str(self.n_rois_created)
        while len(pad_n) < 2:
            pad_n = '0' + pad_n
        roi_filename = subdir + rois_file_prefix + "_01_to_" + pad_n + ".dat"
        with open(roi_filename, 'w') as f:
            f.write(str(len(roi_filename)) + "\n")
            for i in range(len(self.rois)):
                roi = self.rois[i].get_points()
                f.write(str(i) + "\n")
                f.write(str(len(roi) + 1) + "\n")  # +1 for PhotoZ reason
                f.write(str(i) + "\n")  # needed for unknown reason
                for pt in roi:
                    dn = self.convert_point_to_diode_number(pt)
                    f.write(str(dn) + "\n")  # PhotoZ actually 0-indexed internally i think?
        print("Created file:", roi_filename)


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

    def is_point_at_edge(self, x, y, tolerance=2):
        return self.corners.is_point_at_edge(x, y, tolerance=tolerance)

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
        dx0 = axis_pts[0][0] - edge_pts[0][0]
        dy0 = axis_pts[0][1] - edge_pts[0][1]
        dist0 = dx0 * dx0 + dy0 * dy0
        dx0 = axis_pts[1][0] - edge_pts[1][0]
        dy0 = axis_pts[1][1] - edge_pts[1][1]
        dist0 += dx0 * dx0 + dy0 * dy0

        dx1 = axis_pts[0][0] - edge_pts[1][0]
        dy1 = axis_pts[0][1] - edge_pts[1][1]
        dist1 = dx1 * dx1 + dy1 * dy1
        dx1 = axis_pts[1][0] - edge_pts[0][0]
        dy1 = axis_pts[1][1] - edge_pts[0][1]
        dist1 += dx1 * dx1 + dy1 * dy1

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

    def __init__(self, snr, stim_point, roi_centers, corners, lines, line_colors, linewidths, save_dir="."):
        self.plot_point(stim_point)
        self.save_dir = save_dir
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
        plt.savefig(save_dir)

    def plot_point(self, p, color='red', marker='*'):
        plt.plot(p[0], p[1], color=color, marker=marker)

    def plot_line(self, x1, y1, x2, y2, color, linewidth=3):
        plt.plot([x2, x1], [y2, y1], color=color, linewidth=linewidth)
