from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import numpy as np
import random


class Cluster:
    """ Object representing a region of interest / cluster """
    def __init__(self, pixels, width):
        self.width = width
        self.pixels = pixels

    def get_pixels(self):
        return self.pixels

    def get_border_pixels(self, px=None, adj_map=None):
        """ Return a list of pixels bordering the region. Intersection with cluster is null set. """
        if len(self.pixels) < 1:
            return []
        border = []
        if adj_map is None:
            adj_map = self.build_adjacency_map()
        if px is None:
            px = self.pixels[0]
        y, x = px
        border += self.get_adj_px_not_in_cluster(x, y, adj_map)
        neighbors = self.get_px_unvisited_neighbors_from_adj_list(x, y, adj_map)
        for pt2 in neighbors:
            y2, x2 = pt2
            border += self.get_border_pixels(pt2, adj_map)

        adj_map[y][x] = True
        return border

    def get_adj_px_not_in_cluster(self, x, y, adj_map):
        """ Return a list of the pixels that are adjacent to x, y but not in the adj_map """
        border = []
        for x2 in range(max(0, x-1), min(self.width-1, x+1)):
            for y2 in range(max(0, y - 1), min(self.width - 1, y + 1)):
                if y2 not in adj_map or x2 not in adj_map[y2]:
                    border.append([y2, x2])
        return border

    def get_px_unvisited_neighbors_from_adj_list(self, x, y, adj_map):
        """ Return a list of points neighboring x, y """
        neighbors = []
        for y2 in [y - 1, y, y + 1]:
            if y2 in adj_map:
                for x2 in [x - 1, x, x + 1]:
                    if x2 in adj_map[y2]:
                        if not adj_map[y2][x2] and abs(x - x2) + abs(y - y2) < 2:
                            neighbors.append([y2, x2])
        return neighbors

    def point_to_diode_number(self, pt):
        # in photoZ diode #s
        return pt[1] * self.width + pt[0]

    def diode_number_to_pt(self, diode):
        return [diode % self.width, int(diode / self.width)]

    def is_adjacent_to(self, cluster2):
        """ Returns True if this cluster is adjacent to cluster2 object """
        for px in self.pixels:
            y1, x1 = px
            for px2 in cluster2.get_pixels():
                y2, x2 = px2
                if np.abs(x1 - x2) < 2 or np.abs(y1 - y2) < 2:
                    return True
        return False

    def get_cluster_size(self):
        return len(self.pixels)

    def get_cluster_snr(self, snr_map):
        avg_snr = 0
        for px in self.pixels:
            y, x = px
            avg_snr += snr_map[x, y]
        return avg_snr / max(1, self.get_cluster_size())

    def find_contiguous(self, pt, adj_map):
        contig_list = [pt]
        y, x = pt
        adj_map[y][x] = True
        neighbors = self.get_px_unvisited_neighbors_from_adj_list(x, y, adj_map)
        for pt2 in neighbors:
            y2, x2 = pt2
            contig_list.append(pt2)
            adj_map[y2][x2] = True
            contig_list += self.find_contiguous(pt2, adj_map)  # recursive depth first search
        return contig_list

    def find_unvisited(self, adj_list):
        """ Return next unvisited pixel, or None """
        for y in adj_list:
            for x in adj_list[y]:
                if not adj_list[y][x]:
                    return [y, x]
        return None

    def build_adjacency_map(self):
        adj_map = {}
        for px in self.pixels:
            y, x = px
            if y not in adj_map:
                adj_map[y] = {}
            adj_map[y][x] = False  # whether point has been visited
        return adj_map

    def create_new_cluster(self, new_pixels):
        return Cluster(new_pixels, self.width)

    def remove_pixels(self, pixels):
        hash_map = {}
        for px in pixels:
            y, x = px
            if y not in hash_map:
                hash_map[y] = {}
            hash_map[y][x] = True
        for i in range(len(self.pixels)-1, -1, -1):
            y, x = self.pixels[i]
            if y in hash_map and x in hash_map[y]:
                del self.pixels[i]

    def attempt_split(self):
        """ If possible, remove non-contiguous points and return as list of new cluster(s) """
        if len(self.pixels) < 2:
            return []
        new_clusters = []
        adj_map = self.build_adjacency_map()
        n_visited = 0
        pt = self.pixels[0]
        while n_visited < len(self.pixels):
            new_island = self.find_contiguous(pt, adj_map)
            n_visited += len(new_island)

            new_clusters.append(self.create_new_cluster(new_island))
            self.remove_pixels(new_island)

            if n_visited < len(self.pixels):
                pt = self.find_unvisited(adj_map)

        return new_clusters

    def get_df_f(self, max_amps, rli):
        """ Computer df/f, where df is the peak fluorescence change from
            RLI, and f = RLI (base fluorescence) """
        avg_dff = 0
        for px in self.pixels:
            y, x = px
            avg_dff += max_amps[x, y] / rli[x, y]
        return avg_dff / max(1, self.get_cluster_size())


class ROI_Identifier:

    def __init__(self):
        pass

    def generate_points(self, snr_map, n_points=100000, percentile_cutoff=85, upper_cutoff=100):
        """ Use MC method to generate points, interpreting
            the intensity map as a probability distribution """
        z_max = np.max(snr_map)
        cutoff = np.percentile(snr_map, percentile_cutoff)
        if upper_cutoff == 100:
            upper_cutoff = None
        else:
            upper_cutoff = np.percentile(snr_map, upper_cutoff)

        samples = []
        while len(samples) < n_points:
            # sample a random point uniformly
            w, h = snr_map.shape
            x_sample = random.randint(0, w - 1)
            y_sample = random.randint(0, h - 1)

            # reject outright if SNR is below cutoff
            if snr_map[x_sample][y_sample] < cutoff or \
                    (upper_cutoff is not None and snr_map[x_sample][y_sample] > upper_cutoff):
                continue
            else:  # sample from SNR map as probability
                z_sample = random.uniform(0, z_max)

                if snr_map[x_sample][y_sample] >= z_sample:
                    samples.append([y_sample, x_sample])

        return np.array(samples)

    def heatmap_of_scatter(self, samples, w, h):
        heatmap, xedges, yedges = np.histogram2d(samples[:, 0],
                                                 samples[:, 1],
                                                 bins=(w, h))
        extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]

        plt.clf()
        plt.imshow(heatmap.T, extent=extent, origin='upper')
        plt.show()

    def find_gmm_cluster_number(self, X, k_start=1, k_search=40, k_step=4, aic_only=True):
        n_components = np.arange(k_start, k_search, k_step)
        models = [GaussianMixture(n, covariance_type='full', random_state=0).fit(X)
                  for n in n_components]
        if not aic_only:
            plt.plot(n_components, [m.bic(X) for m in models], label='BIC')
        plt.plot(n_components, [m.aic(X) for m in models], label='AIC')
        plt.legend(loc='best')
        plt.xlabel('n_components')

    def gaussian_mixture_model(self, X, k, show=True):
        gmm = GaussianMixture(n_components=k)
        gmm.fit(X)
        labels = gmm.predict(X)
        if show:
            plt.gca().invert_yaxis()
            plt.scatter(X[:, 0], X[:, 1],
                        s=10,
                        c=labels,
                        cmap='rainbow')
        return labels

    def draw_gmm_enclosures(self, X, labels, a=0.1, s=10, show=True, plot_sample_heatmap=True, overlay_image=None):
        w, h = X.shape
        heatmap, xedges, yedges = np.histogram2d(X[:, 0], X[:, 1],
                                                 bins=(w, h))
        extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]

        if plot_sample_heatmap:
            plt.imshow(heatmap.T, extent=extent, origin='upper')
        elif overlay_image is not None:
            plt.imshow(overlay_image, cmap='gray')
        else:
            plt.imshow(np.zeros(heatmap.shape), extent=extent, origin='upper')
        plt.scatter(X[:, 0], X[:, 1],
                    s=s,
                    c=labels,
                    cmap='rainbow',
                    alpha=a)
        if show:
            plt.show()
