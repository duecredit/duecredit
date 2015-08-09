# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Automatic injection of bibliography entries for numpy module
"""

from ..entries import Doi, BibTeX, Url

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('sklearn', None, BibTeX("""
    @article{pedregosa2011scikit,
        title={Scikit-learn: Machine learning in Python},
        author={Pedregosa, Fabian and Varoquaux, Ga{\"e}l and Gramfort,
        Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel,
        Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss,
        Ron and Dubourg, Vincent and others},
        journal={The Journal of Machine Learning Research},
        volume={12},
        pages={2825--2830},
        year={2011},
        publisher={JMLR. org}
        }
    """), description="Machine Learning library")

    # sklearn.cluster.affinity_propagation_
    injector.add('sklearn.cluster.affinity_propagation_', None, Doi('10.1126/science.1136800'),
                 description="Affinity propagation clustering algorithm", tags=['reference'])

    # sklearn.cluster.bicluster
    injector.add('sklearn.cluster.bicluster', 'SpectralCoclustering', Doi('10.1.1.140.301'),
                 description="Spectral Coclustering algorithm", tags=['reference'])
    injector.add('sklearn.cluster.bicluster', 'SpectralBiclustering', Doi('10.1.1.135.1608'),
                 description="Spectral Biclustering algorithm", tags=['reference'])

    # sklearn.cluster.birch
    injector.add('sklearn.cluster.birch', 'Birch', Doi('10.1145/233269.233324'),
                 description="BIRCH clustering algorithm", tags=['reference'])
    injector.add('sklearn.cluster.birch', 'Birch', Url('https://code.google.com/p/jbirch/'),
                 description="Java implementation of BIRCH clustering algorithm", tags=['implementation'])

    # sklearn.cluster.dbscan_
    injector.add('sklearn.cluster.dbscan_', 'dbscan',
                 BibTeX("""@inproceedings{ester1996density,
  title={A density-based algorithm for discovering clusters in large spatial databases with noise.},
  author={Ester, Martin and Kriegel, Hans-Peter and Sander, J{\"o}rg and Xu, Xiaowei},
  booktitle={Kdd},
  volume={96},
  number={34},
  pages={226--231},
  year={1996}
}"""), description="dbscan clustering algorithm", tags=['reference'])

    # sklearn.cluster.mean_shift_
    injector.add('sklearn.cluster.mean_shift_', 'MeanShift', Doi('10.1109/34.1000236'),
                 description="Mean shift clustering algorithm", tags=['reference'])

    # sklearn.cluster.spectral
    injector.add('sklearn.cluster.spectral', 'discretize', Doi('10.1109/ICCV.2003.1238361'),
                 description="Multiclass spectral clustering", tags=['reference'])
    injector.add('sklearn.cluster.spectral', 'spectral_clustering', Doi('10.1.1.160.2324'),
                 description="Spectral clustering", tags=['reference'])
    injector.add('sklearn.cluster.spectral', 'spectral_clustering', Doi('10.1.1.165.9323'),
                 description="Spectral clustering", tags=['reference'])


