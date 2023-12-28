import numpy as np
import heapq
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

    def get_line_formula(self):
        """ formula for this line in Ax + By + C = 0 """
        dy = (self.y2 - self.y1)
        dx = (self.x2 - self.x1)
        b_dx = self.y2 * dx - dy * self.x2
        B, A, C = dx, -dy, -b_dx
        return A, B, C

    def get_distance_to_point(self, pt):
        """ FInd length of perpendicular distance to pt """
        x, y = pt
        A, B, C = self.get_line_formula()
        d = np.abs(A * x + B * y + C) / np.sqrt(A * A + B * B)
        return d

    def is_point_left_of_line(self, pt):
        """ Returns true if point is on one side of line, else False """
        A, B, C = self.get_line_formula()
        x, y = pt
        return A * x + B * y + C < 0

    def get_angle_theta(self, radians=True):
        """ return angle from x-axis """
        theta = np.arctan((self.y2 - self.y1) / (self.x2 - self.x1))
        if not radians:
            theta = np.degrees(theta)
        return theta

    def get_split_px_map(self, left_value=1, grid_dim=(80, 80)):
        """ Produce a px map where grid is split by line and assigned value accordingly """
        px_map = np.zeros(grid_dim)
        for i in range(grid_dim[0]):
            for j in range(grid_dim[1]):
                if self.is_point_left_of_line([i, j]):
                    px_map[i, j] += left_value
        return px_map

    @staticmethod
    def has_one_connected_domain(px_map):
        """ return whether number of connected domains of split px map PX_MAP is exactly one"""
        w, h = px_map.shape
        def increment_point(i, j):
            if i < w - 1:
                i += 1
            elif j < h - 1:
                j += 1
            else:
                return None
            return [i, j]
        total_populated = np.sum(px_map)

        if total_populated < 1:
            return False
        i, j = 0, 0
        while px_map[i, j] < 1:
            i, j = increment_point(i, j)

        plt.imshow(px_map)
        plt.show()

        traversed_count = 0
        traversed_map = np.zeros((w, h))
        q = [[i,j]]
        while len(q) > 0:
            i, j = q.pop()
            if traversed_map[i, j] == 0:
                traversed_count += px_map[i, j]
                traversed_map[i, j] = 1
            for i_c in [i-1, i, i+1]:
                for j_c in [j-1, j, j+1]:
                    if 0 <= i_c < w and 0 <= j_c < h and traversed_map[i_c, j_c] == 0 and px_map[i_c, j_c] > 0:
                        q.append([i_c, j_c])
        print(traversed_count, total_populated)
        return (traversed_count == total_populated)


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

    def get_dimensions(self):
        return self.w, self.h


class ROICreator:
    """ Given two laminar axes and an ROI width,
        create as many ROIs as possible from start until edge
        The Laminar axes input should be guaranteed
        to be in form [start, edge] vectors. This property
        is guarantteed in LayerAxes.construct_axes method """

    def __init__(self, layer_axes, width=80, height=80, roi_width=3, stim_point_spacer=True):
        self.w, self.h = width, height
        self.axis1, self.axis2 = None, None
        if layer_axes is not None:
            self.axis1, self.axis2 = layer_axes.get_layer_axes()

        self.stim_point_spacer = stim_point_spacer  # whether to leave 1 ROI buffer next to stim pt

        self.roi_width = roi_width
        # if None, bounded only by axes
        if self.roi_width is None:
            self.roi_width = int((self.axis1.get_length() + self.axis2.get_length()) / 2)

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
            if ((not self.stim_point_spacer) or self.n_rois_created > 0) \
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

    def convert_roi_to_diode_numbers(self, roi):
        return [self.convert_point_to_diode_number(pt) for pt in roi]

    def convert_rois_to_diode_numbers(self, rois):
        return [self.convert_roi_to_diode_numbers(r) for r in rois]

    def write_roi_file(self, subdir, rois_file_prefix):
        pad_n = str(self.n_rois_created)
        while len(pad_n) < 2:
            pad_n = '0' + pad_n
        # roi_filename = subdir + rois_file_prefix + "_01_to_" + pad_n + ".dat"
        roi_filename = subdir + rois_file_prefix
        if not roi_filename.endswith(".dat"):
            roi_filename += ".dat"
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
        return roi_filename

    def get_roi_centers(self, rounded=False):
        roi_centers = [r.get_center() for r in self.rois]
        if rounded:
            roi_centers = [[round(r[0], 2), round(r[1], 2)] for r in roi_centers]
        return roi_centers

    def write_roi_centers_to_file(self, filename):
        roi_centers = self.get_roi_centers(rounded=True)
        with open(filename, 'w') as f:
            for rc in roi_centers:
                f.write(str(rc[0]) + "\t" + str(rc[1]) + '\n')
        print("File created: ", filename)


class SquareROICreator(ROICreator):

    def __init__(self, layer_axes, width=80, height=80, roi_width=3, max_num_rois=None, snr=None):
        self.n_sq = roi_width
        self.snr = snr
        self.max_num_rois = max_num_rois
        if self.snr is None and self.max_num_rois is not None:
            raise Exception("max_num_rois argument is given but snr argument is not")
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

    def get_roi_avg_snr(self, roi):
        avg_snr = 0
        for px in roi:
            x, y = px
            avg_snr += self.snr[x, y]
        return avg_snr / len(roi)

    def create_rois(self):
        """ Returns a list of lists of points """
        rois = []
        perpendicular = Line(self.axis1.get_start_point(),
                             self.axis2.get_start_point())
        for col_direction in [-1, 1]:
            continue_to_create_rois = True
            while continue_to_create_rois:  # perpendicular.is_line_partly_in_bounds(self.w, self.h):

                # increment perpendicular
                new_perpendicular = self.increment_perpendicular(perpendicular, col_direction=col_direction)

                # Using a 'walk-along-vectors' method, create roi here
                rois += self.create_row_of_rois(perpendicular)

                perpendicular = new_perpendicular

                # criteria to create additional rois
                continue_to_create_rois = perpendicular.is_line_partly_in_bounds(self.w, self.h)
        rois = self.limit_num_rois(rois)
        self.n_rois_created = len(rois)
        return rois

    def limit_num_rois(self, rois):
        if self.max_num_rois is None or len(rois) <= self.max_num_rois:
            return rois

        snrs = [self.get_roi_avg_snr(r) for r in rois]
        top_n_snr_indices = [snrs.index(i) for i in heapq.nlargest(self.max_num_rois, snrs)]
        top_rois = [rois[i] for i in top_n_snr_indices]
        return top_rois

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
                x_r = float(x) + (j_offset * columnar_walk_direction[0])
                y_r = float(y) + (j_offset * columnar_walk_direction[1])
                for j in range(self.n_sq):
                    x_r2 = float(x_r)
                    y_r2 = float(y_r)
                    for i in range(self.n_sq):
                        jiggle = [-1, 0, 1]
                        if i == 0:
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
                if len(roi) > 0:
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

    def __init__(self, corners, img_width=80, img_height=80, verbose=True, obey_initial_order=False):
        """ obey_initial_order: if False, prioritize edges and minimize total segment length.
                                if True, pair points into lines in the order they come.
        """
        self.verbose = verbose
        self.corners = corners
        self.w = img_width
        self.h = img_height
        if type(self.corners[0]) == int:
            self.convert_corners_to_px()
        self.layer_axis = None  # Line object
        self.layer_axis_2 = None  # Line object
        self.construct_axes(obey_initial_order=obey_initial_order)

    def get_layer_axes(self):
        """ Returns list of two Line objects"""
        return [self.layer_axis, self.layer_axis_2]

    def get_corners(self):
        return self.corners.get_points()

    def convert_corners_to_px(self):
        self.corners = LaminarROI(self.corners,
                                  img_width=self.w,
                                  img_height=self.h)

    def is_point_at_edge(self, x, y, tolerance=0):
        return self.corners.is_point_at_edge(x, y, tolerance=tolerance)

    def construct_axes(self, obey_initial_order=False):
        """ Half of the corners will be at the edge(s)
            The segment between these 2 corners should be excluded
            the segment across from segment should be excluded
            The other two are the axes of interest, and we will set them to
            self.layer_axis and self.layer_axis_2 arbitrarily """

        if obey_initial_order:
            c = self.get_corners()
            self.layer_axis = Line(c[0], c[1])
            self.layer_axis_2 = Line(c[2], c[3])
            return

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

        if self.verbose:
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
                 line_colors, linewidths, rois, roi_colors, save_dir=".",
                 produce_plot=True):
        if stim_point is not None:
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
        if produce_plot:
            self.produce_plot(save_dir)

    @staticmethod
    def produce_plot(save_dir):
        plt.savefig(save_dir)
        plt.show()

    @staticmethod
    def plot_point(p, color='red', marker='*'):
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
                 line_colors, linewidths, rois, roi_colors, save_dir=".",
                 produce_plot=True):
        super().__init__(snr, stim_point, roi_centers, corners, lines[:2], line_colors[:2], linewidths[:2],
                         rois, roi_colors, save_dir=save_dir, produce_plot=produce_plot)

    def draw_directed_arrow(self, nd, nd2):
        """ Draw arrow nd -> nd2 connecting centers """
        shorten = 0.84
        x, y = nd.get_center()
        x2, y2 = nd2.get_center()
        dx = (x2 - x) * shorten
        dy = (y2 - y) * shorten
        plt.arrow(x, y, dx, dy, length_includes_head=True, head_width=1, color='white')

    def draw_current_flow_arrow(self, nd, min_lat=0.2, max_lat=3.0, norm_max=3.0):
        """ Draw arrow over this node representing currnt flow """
        v = nd.get_current_flow_vector()
        dx, dy = v
        length = np.sqrt(dx*dx + dy*dy)
        if min_lat <= length <= max_lat:
            dx /= length
            dy /= length
            length /= norm_max
            c = nd.get_center()

            dx = length
            plt.arrow(c[0], c[1], dx * length, dy * length,
                      length_includes_head=True,
                      head_width=1,
                      color='black')
        elif length > max_lat:
            print("Big average latency:", length)

