#coding=utf-8

import numpy as np
import warnings
from sklearn.cluster import k_means_
from sklearn.utils import check_array
from sklearn.utils import check_random_state
from sklearn.utils import as_float_array
from sklearn.utils import gen_batches
from sklearn.utils.validation import check_is_fitted
from sklearn.utils.validation import FLOAT_DTYPES
from .StringMatch import StringMatch

class StringCluster(k_means_.MiniBatchKMeans):
    def __init__(self, n_clusters=8, init='k-means++', max_iter=100,
                 batch_size=100, verbose=0, compute_labels=True,
                 random_state=None, tol=0.0, max_no_improvement=10,
                 init_size=None, n_init=3, reassignment_ratio=0.01):
        super().__init__(n_clusters, init, max_iter, batch_size, verbose, compute_labels,random_state,
                         tol, max_no_improvement,init_size, n_init, reassignment_ratio)

    def fit(self, X, y=None):
        """Compute the centroids on X by chunking it into mini-batches.

        Parameters
        ----------
        X : array-like or sparse matrix, shape=(n_samples, n_features)
            Training instances to cluster.

        y : Ignored

        """
        random_state = check_random_state(self.random_state)
        X = check_array(X, accept_sparse="csr", order='C',
                        dtype=[np.float64, np.float32])
        n_samples, n_features = X.shape
        if n_samples < self.n_clusters:
            raise ValueError("Number of samples smaller than number "
                             "of clusters.")

        n_init = self.n_init
        if hasattr(self.init, '__array__'):
            self.init = np.ascontiguousarray(self.init, dtype=X.dtype)
            if n_init != 1:
                warnings.warn(
                    'Explicit initial center position passed: '
                    'performing only one init in MiniBatchKMeans instead of '
                    'n_init=%d'
                    % self.n_init, RuntimeWarning, stacklevel=2)
                n_init = 1

        x_squared_norms = k_means_.row_norms(X, squared=True)

        if self.tol > 0.0:
            tol = k_means_._tolerance(X, self.tol)

            # using tol-based early stopping needs the allocation of a
            # dedicated before which can be expensive for high dim data:
            # hence we allocate it outside of the main loop
            old_center_buffer = np.zeros(n_features, dtype=X.dtype)
        else:
            tol = 0.0
            # no need for the center buffer if tol-based early stopping is
            # disabled
            old_center_buffer = np.zeros(0, dtype=X.dtype)

        distances = np.zeros(self.batch_size, dtype=X.dtype)
        n_batches = int(np.ceil(float(n_samples) / self.batch_size))
        n_iter = int(self.max_iter * n_batches)

        init_size = self.init_size
        if init_size is None:
            init_size = 3 * self.batch_size
        if init_size > n_samples:
            init_size = n_samples
        self.init_size_ = init_size

        validation_indices = random_state.randint(0, n_samples, init_size)
        X_valid = X[validation_indices]
        x_squared_norms_valid = x_squared_norms[validation_indices]

        # perform several inits with random sub-sets
        best_inertia = None
        for init_idx in range(n_init):
            if self.verbose:
                print("Init %d/%d with method: %s"
                      % (init_idx + 1, n_init, self.init))
            counts = np.zeros(self.n_clusters, dtype=np.int32)

            # TODO: once the `k_means` function works with sparse input we
            # should refactor the following init to use it instead.

            # Initialize the centers using only a fraction of the data as we
            # expect n_samples to be very large when using MiniBatchKMeans
            cluster_centers = k_means_._init_centroids(
                X, self.n_clusters, self.init,
                random_state=random_state,
                x_squared_norms=x_squared_norms,
                init_size=init_size)

            # Compute the label assignment on the init dataset
            batch_inertia, centers_squared_diff = k_means_._mini_batch_step(
                X_valid, x_squared_norms[validation_indices],
                cluster_centers, counts, old_center_buffer, False,
                distances=None, verbose=self.verbose)

            # Keep only the best cluster centers across independent inits on
            # the common validation set
            _, inertia = k_means_._labels_inertia(X_valid, x_squared_norms_valid,
                                         cluster_centers)
            if self.verbose:
                print("Inertia for init %d/%d: %f"
                      % (init_idx + 1, n_init, inertia))
            if best_inertia is None or inertia < best_inertia:
                self.cluster_centers_ = cluster_centers
                self.counts_ = counts
                best_inertia = inertia

        # Empty context to be used inplace by the convergence check routine
        convergence_context = {}

        # Perform the iterative optimization until the final convergence
        # criterion
        for iteration_idx in range(n_iter):
            # Sample a minibatch from the full dataset
            minibatch_indices = random_state.randint(
                0, n_samples, self.batch_size)

            # Perform the actual update step on the minibatch data
            batch_inertia, centers_squared_diff = k_means_._mini_batch_step(
                X[minibatch_indices], x_squared_norms[minibatch_indices],
                self.cluster_centers_, self.counts_,
                old_center_buffer, tol > 0.0, distances=distances,
                # Here we randomly choose whether to perform
                # random reassignment: the choice is done as a function
                # of the iteration index, and the minimum number of
                # counts, in order to force this reassignment to happen
                # every once in a while
                random_reassign=((iteration_idx + 1)
                                 % (10 + self.counts_.min()) == 0),
                random_state=random_state,
                reassignment_ratio=self.reassignment_ratio,
                verbose=self.verbose)

            # Monitor convergence and do early stopping if necessary
            if k_means_._mini_batch_convergence(
                    self, iteration_idx, n_iter, tol, n_samples,
                    centers_squared_diff, batch_inertia, convergence_context,
                    verbose=self.verbose):
                break

        self.n_iter_ = iteration_idx + 1

        if self.compute_labels:
            self.labels_, self.inertia_ = self._labels_inertia_minibatch(X)

        return self

def main():
    K0 = StringCluster()

if __name__ == '__main__':
    main()