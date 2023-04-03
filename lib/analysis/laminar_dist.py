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
        dx, dy = self.get_disp_vector()
        return np.sqrt(dx * dx + dy * dy)

    def get_disp_vector(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        return [x, y]

    def is_line_partly_in_bounds(self, w, h):
        """ True if at least one of the rois is in bounds w x h"""
        return ((0 <= self.x1 < w
                 and 0 <= self.y1 < h) or
                (0 <= self.x2 < w
                 and 0 <= self.y2 < h))

    def is_line_entirely_in_bounds(self, w, h):
        """ True if both ends of line are within w x h """
        return (0 <= self.x1 < w
                and 0 <= self.y1 < h
                and 0 <= self.x2 < w
                and 0 <= self.y2 < h)

    def get_unit_vector(self):
        x, y = self.get_disp_vector()
        length = self.get_length()
        return [x / length, y / length]

    def get_projection_of_segment(self, p1, p2):
        """ get the length of the projection of the segment p1-p2 onto this line """
        uv = self.get_unit_vector()
        input_v = [p2[0] - p1[0], p2[1] - p1[1]]
        return np.abs(uv[0] * input_v[0] + uv[1] * input_v[1])


class LaminarROI:
    """ A layer-like (as opposed to single-cell) ROI spanning the width of a cortex layer or column"""

    def __init__(self, points, img_width=80, img_height=80, input_diode_numbers=True, center_offset=None):
        self.w = img_width
        self.h = img_height
        self.points = points
        if input_diode_numbers:
            self.points = self.diode_num_to_points(points)
        self.center = self.calculate_center_of_mass(center_offset)

    def get_center(self):
        return self.center

    def get_points(self):
        return self.points

    def calculate_center_of_mass(self, center_offset):
        avg_pt = [0, 0]
        if len(self.points) < 1:
            return [None, None]

        for pt in self.points:
            avg_pt[0] += pt[0]
            avg_pt[1] += pt[1]

        if center_offset is not None:
            offset = center_offset['offset']
            total_points = center_offset['total_points']
            avg_pt[0] += offset[0]
            avg_pt[1] += offset[1]
            avg_pt[0] /= total_points
            avg_pt[1] /= total_points
        else:
            avg_pt[0] /= len(self.points)
            avg_pt[1] /= len(self.points)
        return avg_pt

    def diode_num_to_points(self, diode_numbers):
        pts = []
        for dn in diode_numbers:
            x_px = dn % self.w
            y_px = int(dn / self.w)
            pts.append([x_px, y_px])
        return pts

    def is_point_at_edge(self, x, y, tolerance=2):
        if tolerance == 0:
            return x == 0 or y == 0 or \
                   x == self.w - 1 or y == self.h - 1
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
        self.roi_center_offsets = []  # a list of out-of-bounds points (dicts)
        self.added_point_map = {}  # guarantee that NO rois overlap
        self.roi_min_size = 27  # less than this # of px will not be used as roi

    def round_bound_w(self, v):
        """ Round v and keep in width bounds """
        v = round(v)
        v = max(0, v)
        v = min(v, self.w - 1)
        return v

    def round_bound_h(self, v):
        """ Round v and keep in height bounds """
        v = round(v)
        v = max(0, v)
        v = min(v, self.h - 1)
        return v

    def create_roi_from_bounds(self, perpend, limit_roi_length=None):
        roi = []
        center_offset = [0, 0]
        distance = round(perpend.get_length())
        if limit_roi_length is not None:
            distance = min(limit_roi_length, distance)
        # start point is where perpend1 starts
        x, y = perpend.get_start_point()
        total_points = 0  # includes out-of-bounds points for center offset

        laminar_walk_direction = self.axis1.get_unit_vector()
        columnar_walk_direction = perpend.get_unit_vector()

        for j in range(distance):
            x_r = float(x)
            y_r = float(y)
            for i in range(self.roi_width):
                jiggle = [-1, 0, 1]
                if i == 0 or i == self.roi_width - 1:
                    jiggle = [0]
                if i > 0:
                    x_r += laminar_walk_direction[0]
                    y_r += laminar_walk_direction[1]
                x_round = round(x_r)
                y_round = round(y_r)
                for dy in jiggle:
                    for dx in jiggle:
                        x_round_jig = x_round + dx
                        y_round_jig = y_round + dy
                        if 0 <= x_round_jig < self.w and \
                                0 <= y_round_jig < self.h:

                            if not (x_round_jig in self.added_point_map
                                    and y_round_jig in self.added_point_map[x_round_jig]):
                                roi.append([x_round_jig, y_round_jig])
                                if x_round_jig not in self.added_point_map:
                                    self.added_point_map[x_round_jig] = {}
                                if y_round_jig not in self.added_point_map[x_round_jig]:
                                    self.added_point_map[x_round_jig][y_round_jig] = True
                        else:  # out of bounds, add to center-offset
                            center_offset[0] += x_round
                            center_offset[1] += y_round
                        total_points += 1
            # increment down column now
            x += columnar_walk_direction[0]
            y += columnar_walk_direction[1]

        # 'ghost' out-of-bounds points to take into account when determining
        # roi center-of-mass
        offset = None
        if center_offset[0] != 0 and center_offset[1] != 0:
            offset = {'offset': center_offset,
                      'total_points': total_points}
        return roi, offset

    def get_rois(self):
        self.rois = self.create_rois()  # list of list of points

        # convert to list of LaminarROI objects
        self.rois = [LaminarROI(self.rois[i],
                                img_width=self.w,
                                input_diode_numbers=False,
                                #  center_offset=self.roi_center_offsets[i]
                                )
                     for i in range(len(self.rois))]
        return self.rois

    def increment_perpendicular(self, perpendicular, col_direction=1):
        s = perpendicular.get_start_point()
        uv1 = self.axis1.get_unit_vector()  # for incrementing start point of perpend
        uv2 = self.axis2.get_unit_vector()  # for incrementing end point of perpend
        rw = float(self.roi_width) * col_direction
        new_start_pt = [s[0] + uv1[0] * rw,
                        s[1] + uv1[1] * rw]
        e = perpendicular.get_end_point()
        new_end_pt = [e[0] + uv2[0] * rw,
                      e[1] + uv2[1] * rw]
        new_perpendicular = Line(new_start_pt, new_end_pt)
        return new_perpendicular

    def create_rois(self):
        """ Returns a list of lists of points """
        rois = []
        perpendicular = Line(self.axis1.get_start_point(),
                             self.axis2.get_start_point())
        self.n_rois_created = 0
        continue_to_create_rois = True
        while continue_to_create_rois:  # perpendicular.is_line_partly_in_bounds(self.w, self.h):

            # increment perpendicular
            new_perpendicular = self.increment_perpendicular(perpendicular)

            # Using a 'walk-along-vectors' method, create roi here
            roi, center_offset = self.create_roi_from_bounds(perpendicular)

            # leave a buffer near stim point
            if self.n_rois_created > 0 \
                    and len(roi) > self.roi_min_size:  # hard-coded
                rois.append(roi)
                self.roi_center_offsets.append(center_offset)
            self.n_rois_created += 1

            perpendicular = new_perpendicular

            # criteria to create additional rois
            continue_to_create_rois = (len(roi) > self.roi_min_size) \
                                      or perpendicular.is_line_partly_in_bounds(self.w, self.h)

        self.n_rois_created -= 1  # we discarded the first roi
        return rois

    def convert_point_to_diode_number(self, pt):
        x, y = pt
        dn = y * self.w + x
        return dn

    def write_roi_file(self, subdir, rois_file_prefix):
        pad_n = str(self.n_rois_created)
        while len(pad_n) < 2:
            pad_n = '0' + pad_n
        # roi_filename = subdir + rois_file_prefix + "_01_to_" + pad_n + ".dat"
        roi_filename = subdir + rois_file_prefix + ".dat"
        with open(roi_filename, 'w') as f:
            f.write(str(len(self.rois)) + "\n")
            for i in range(len(self.rois)):
                roi = self.rois[i].get_points()
                f.write(str(i) + "\n")
                f.write(str(len(roi) + 1) + "\n")  # +1 for PhotoZ reason
                f.write(str(i) + "\n")  # needed for unknown reason
                for pt in roi:
                    dn = self.convert_point_to_diode_number(pt)
                    f.write(str(dn) + "\n")  # PhotoZ actually 0-indexed internally i think?
        print("Created file:", roi_filename)


class SquareROICreator(ROICreator):

    def __init__(self, layer_axes, width=80, height=80, roi_width=3):
        self.n_sq = roi_width
        super().__init__(layer_axes, width=width, height=height, roi_width=roi_width)

    def get_rois(self):
        self.rois = self.create_rois()  # list of list of points

        # convert to list of LaminarROI objects
        self.rois = [LaminarROI(self.rois[i],
                                img_width=self.w,
                                input_diode_numbers=False,
                                #  center_offset=self.roi_center_offsets[i]
                                )
                     for i in range(len(self.rois))]
        return self.rois

    def create_rois(self):
        """ Returns a list of lists of points """
        rois = []
        perpendicular = Line(self.axis1.get_start_point(),
                             self.axis2.get_start_point())
        self.n_rois_created = 0
        for col_direction in [-1, 1]:
            continue_to_create_rois = True
            while continue_to_create_rois:  # perpendicular.is_line_partly_in_bounds(self.w, self.h):

                # increment perpendicular
                new_perpendicular = self.increment_perpendicular(perpendicular, col_direction=col_direction)

                # Using a 'walk-along-vectors' method, create roi here
                rois += self.create_row_of_rois(perpendicular)

                self.n_rois_created += 1

                perpendicular = new_perpendicular

                # criteria to create additional rois
                continue_to_create_rois = perpendicular.is_line_partly_in_bounds(self.w, self.h)

        return rois

    def create_row_of_rois(self, perpend):
        rois = []
        roi = []
        laminar_walk_direction = self.axis1.get_unit_vector()
        columnar_walk_direction = perpend.get_unit_vector()

        # go in positive direction as far as possible, go in negative direction as far as possible
        for row_direction in [-1, 1]:
            # start point is where perpend1 starts
            x, y = perpend.get_start_point()
            continue_to_create = True
            j_offset = 0
            while continue_to_create:
                x_r = float(x) + j_offset
                y_r = float(y) + j_offset
                for j in range(self.n_sq):
                    x_r2 = float(x_r)
                    y_r2 = float(y_r)
                    for i in range(self.n_sq):
                        jiggle = [-1, 0, 1]
                        if i == 0 or i == self.n_sq - 1:
                            jiggle = [0]
                        if i > 0:
                            x_r2 += laminar_walk_direction[0] * row_direction
                            y_r2 += laminar_walk_direction[1] * row_direction
                        x_round = round(x_r2)
                        y_round = round(y_r2)
                        for dy in jiggle:
                            for dx in jiggle:
                                x_round_jig = x_round + dx
                                y_round_jig = y_round + dy
                                if 0 <= x_round_jig < self.w and \
                                        0 <= y_round_jig < self.h:

                                    if not (x_round_jig in self.added_point_map
                                            and y_round_jig in self.added_point_map[x_round_jig]):
                                        roi.append([x_round_jig, y_round_jig])
                                        if x_round_jig not in self.added_point_map:
                                            self.added_point_map[x_round_jig] = {}
                                        if y_round_jig not in self.added_point_map[x_round_jig]:
                                            self.added_point_map[x_round_jig][y_round_jig] = True
                    # increment down column now
                    x_r += columnar_walk_direction[0]
                    y_r += columnar_walk_direction[1]
                if len(roi) > 0.25 * self.n_sq * self.n_sq:
                    rois.append(roi)
                continue_to_create = (np.abs(j_offset) < self.w)
                roi = []
                j_offset += self.n_sq * row_direction

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

    def write_laminar_distance_file(self, dir, input_laminar_distances):
        with open(dir + "laminar_distances.txt", 'w') as f:
            for ld in input_laminar_distances:
                f.write(str(ld) + '\n')
        print("File created: ", dir + "laminar_distances.txt")


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

    def is_point_at_edge(self, x, y, tolerance=0):
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

        # if no edge points, treat the last two points as edge points
        if len(edge_pts) < 1:
            edge_pts = axis_pts[2:]
            axis_pts = axis_pts[:2]

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

    def __init__(self, snr, stim_point, roi_centers, corners, lines,
                 line_colors, linewidths, rois, roi_colors, save_dir="."):
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
        for i in range(len(rois)):
            self.plot_roi(rois[i].get_points(), roi_colors[i])
        plt.imshow(snr)
        plt.savefig(save_dir)
        plt.show()

    def plot_point(self, p, color='red', marker='*'):
        plt.plot(p[0], p[1], color=color, marker=marker)

    def plot_line(self, x1, y1, x2, y2, color, linewidth=3):
        plt.plot([x2, x1], [y2, y1], color=color, linewidth=linewidth)

    def plot_roi(self, roi_pts, roi_color):
        x, y = [], []
        for pt in roi_pts:
            x.append(pt[0])
            y.append(pt[1])
        plt.scatter(x, y, c=roi_color, s=1)


class GridVisualization(LaminarVisualization):
    """ produce a plot of SNR with the results plotted """

    def __init__(self, snr, stim_point, roi_centers, corners, lines,
                 line_colors, linewidths, rois, roi_colors, save_dir="."):
        super().__init__(snr, stim_point, roi_centers, corners, lines[:2], line_colors[:2], linewidths[:2],
                         rois, roi_colors, save_dir=save_dir)

