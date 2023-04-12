import numpy as np
import matplotlib.pyplot as plt
from lib.analysis.laminar_dist import LaminarVisualization, GridVisualization


# Code to build a directed graph analysis of spatial
# area and latency, to measurement shape of signal flow

class Node:
    """A node representing an ROI located in a grid"""
    def __init__(self, center, latency, snr, i=None):
        self.center = center
        self.latency = latency
        self.snr = snr
        self.i = i
        self.flow_vector = [0, 0]  # a vector representing current flow, magnitude prop to latency difference (x snr?)

        # for calculation
        self.running_fv_average = [0, 0]  # running average
        self.running_neighbor_count = 0

    def calculate_fv_from_running_numbers(self, weight_by_snr=True):
        if self.running_neighbor_count > 0:
            v = self.running_fv_average
            if weight_by_snr:
                v[0] *= self.snr
                v[1] *= self.snr
            v[0] /= self.running_neighbor_count
            v[1] /= self.running_neighbor_count
            self.set_current_flow_vector(v)

            self.running_fv_average = [0, 0]  # running average
            self.running_neighbor_count = 0

    def accumulate_running_fv(self, v, latency):
        self.running_neighbor_count += 1
        self.running_fv_average[0] = v[0] * latency
        self.running_fv_average[1] = v[1] * latency

    def get_center(self):
        return self.center

    def get_current_flow_vector(self):
        return self.flow_vector

    def set_current_flow_vector(self, v):
        self.flow_vector = v

    def get_latency(self):
        return self.latency

    def get_snr(self):
        return self.snr

    def set_node_index(self, i):
        self.i = i

    def get_node_index(self):
        return self.i

    def is_neighbor(self, nd2, node_edge_length, tol=0.1):
        """ True if nd and nd2 centers are < (1+tol) x dist between diagonal nodes """
        x, y = self.get_center()
        x2, y2 = nd2.get_center()
        dist = np.sqrt((x-x2)**2 + (y-y2)**2)
        return dist <= node_edge_length * np.sqrt(2) * (1 + tol)

    def get_unit_vector_between_centers(self, nd2):
        """ Get the unit vector pointing from center to center of nd2 """
        c2 = nd2.get_center()
        c = self.get_center()
        uv = [c[0] - c2[0],
              c[1] - c2[1]]
        length = np.sqrt(uv[0] * uv[0] + uv[1] * uv[1])
        uv[0] /= length
        uv[1] /= length
        return uv


class Grid:
    """ A graph representing a collection of nodes and their adjacencies
            1) builds directed graph of significant latency differences
            2) generates latency maps
            3) generates spatial flow visualization
    """
    def __init__(self, node_list, node_side_edge_length, latency_tolerance=0.2):
        self.node_list = node_list
        self.n = len(self.node_list)
        self.node_side_edge_length = node_side_edge_length
        self.adjacency_matrix = np.zeros((self.n, self.n), dtype=np.int8)
        self.dir_latency_matrix = np.zeros((self.n, self.n), dtype=np.int8)  # i -> j if latency(i) < latency(j)
        self.latency_tolerance = latency_tolerance  # ms to count as non-simultaneous difference between latencies
        self.connect_neighbors()  # populate adjacency matrix

    def create_latency_map(self, ):
        """ Create a map of ROI latencies in original frame space """
        raise NotImplementedError

    def mark_neighbors(self, i , j):
        self.adjacency_matrix[i, j] = 1
        self.adjacency_matrix[j, i] = 1

    def mark_i_comes_before_j(self, i, j):
        """ i -> j if latency(i) < latency(j) """
        self.dir_latency_matrix[i, j] = 1
        self.dir_latency_matrix[j, i] = 0

    def is_i_before_j(self, i, j):
        return self.dir_latency_matrix[i, j] == 1

    def are_neighbors(self, i, j):
        return self.adjacency_matrix[i, j] == 1

    def determine_prior_node(self, nd, nd2):
        """ If either node is before the other, return them in latency increasing order. Else returns None """
        lat = nd.get_latency()
        lat2 = nd2.get_latency()
        if 0 < lat2 - lat > self.latency_tolerance:
            return nd, nd2
        elif 0 < lat - lat2 > self.latency_tolerance:
            return nd2, nd
        return None, None

    def connect_neighbors(self):
        """ populate adjacency matrix """
        for i in range(len(self.node_list)):
            nd = self.node_list[i]
            nd.set_node_index(i)
            for j in range(i+1, len(self.node_list)):
                nd2 = self.node_list[j]
                if nd.is_neighbor(nd2, self.node_side_edge_length):
                    self.mark_neighbors(i, j)

    def populate_latency_matrix(self):
        """ populate directed latency matrix """
        for i in range(len(self.node_list)):
            nd = self.node_list[i]
            for j in range(i+1, len(self.node_list)):
                nd2 = self.node_list[j]
                if self.are_neighbors(i, j):
                    pn, ln = self.determine_prior_node(nd, nd2)
                    if pn is not None:
                        pi = pn.get_node_index()
                        li = ln.get_node_index()
                        self.mark_i_comes_before_j(pi, li)

    def visualize_spatial_flow(self, snr_map, save_dir="."):
        """ genearte visualization of latency matrix """
        gv = GridVisualization(snr_map, None, [], [], [],
                 [], [], [], [], save_dir=save_dir, produce_plot=False)
        # draw directed arrows over SNR map
        for i in range(len(self.node_list)):
            nd = self.node_list[i]
            for j in range(i + 1, len(self.node_list)):
                nd2 = self.node_list[j]
                if self.is_i_before_j(i, j):
                    gv.draw_directed_arrow(nd, nd2)
                elif self.is_i_before_j(j, i):
                    gv.draw_directed_arrow(nd2, nd)
        gv.produce_plot(save_dir)

    def calculate_current_field(self):
        """ Calculate current flow vectors of all nodes in the network
                For each neighbor,
                    Get the unit vector from center to neighbor's center
                    Weight the vector by latency difference
                Weighted average over all such neighbors
        """
        for i in range(len(self.node_list)):
            nd = self.node_list[i]
            for j in range(i + 1, len(self.node_list)):
                nd2 = self.node_list[j]
                if self.are_neighbors(i, j):
                    uv = nd.get_unit_vector_between_centers(nd2)
                    lat = nd.get_latency() - nd2.get_latency()
                    nd.accumulate_running_fv(uv, lat)
                    # do reverse
                    uv[0] *= -1
                    uv[1] *= -1
                    nd2.accumulate_running_fv(uv, -1 * lat)
        for i in range(len(self.node_list)):
            nd = self.node_list[i]
            nd.calculate_fv_from_running_numbers()

    def visualize_current_field(self, snr_map, save_dir=".", min_lat=0.1, max_lat=3.0):
        """ Visualize current flow vectors of all nodes in the network """
        gv = GridVisualization(snr_map, None, [], [], [],
                               [], [], [], [], save_dir=save_dir, produce_plot=False)
        # draw current field over SNR map
        for i in range(len(self.node_list)):
            nd = self.node_list[i]
            gv.draw_current_flow_arrow(nd,
                                       min_lat=min_lat,
                                       max_lat=max_lat,
                                       norm_max=max_lat / 3.0)
        gv.produce_plot(save_dir)
