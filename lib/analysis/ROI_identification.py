from sklearn.mixture import GaussianMixture
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import numpy as np
import random


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
        plt.xlabel('n_components');

    def gaussian_mixture_model(self, X, k, show=True):
        gmm = GaussianMixture(n_components=k)
        gmm.fit(X)
        labels = gmm.predict(X)
        if show:
            plt.gca().invert_yaxis()
            plt.scatter(X[:, 0], X[:, 1],
                        s=10,
                        c=labels,
                        cmap='rainbow');
        return labels

    def draw_gmm_enclosures(self, X, labels, a=0.1, s=10):
        w, h = X.shape
        heatmap, xedges, yedges = np.histogram2d(X[:, 0], X[:, 1],
                                                 bins=(w, h))
        extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]

        plt.clf()
        plt.imshow(heatmap.T, extent=extent, origin='upper')
        plt.scatter(X[:, 0], X[:, 1],
                    s=s,
                    c=labels,
                    cmap='rainbow',
                    alpha=a);
        plt.show()
