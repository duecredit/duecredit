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
        publisher={JMLR.org}
        }
    """), description="Machine Learning library")

    # sklearn.cluster.affinity_propagation_
    injector.add('sklearn.cluster.affinity_propagation_', None, Doi('10.1126/science.1136800'),
                 description="Affinity propagation clustering algorithm", tags=['implementation'])

    # sklearn.cluster.bicluster
    injector.add('sklearn.cluster.bicluster', 'SpectralCoclustering._fit', Doi('10.1101/gr.648603'),
                 description="Spectral Coclustering algorithm", tags=['implementation'])
    injector.add('sklearn.cluster.bicluster', 'SpectralBiclustering._fit', Doi('10.1101/gr.648603'),
                 description="Spectral Biclustering algorithm", tags=['implementation'])

    # sklearn.cluster.birch
    injector.add('sklearn.cluster.birch', 'Birch._fit', Doi('10.1145/233269.233324'),
                 description="BIRCH clustering algorithm", tags=['implementation'])
    injector.add('sklearn.cluster.birch', 'Birch._fit', Url('https://code.google.com/p/jbirch/'),
                 description="Java implementation of BIRCH clustering algorithm", tags=['another-implementation'])

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
}"""), description="dbscan clustering algorithm", tags=['implementation'])

    # sklearn.cluster.mean_shift_
    injector.add('sklearn.cluster.mean_shift_', 'mean_shift', Doi('10.1109/34.1000236'),
                 description="Mean shift clustering algorithm", tags=['implementation'])

    # sklearn.cluster.spectral
    injector.add('sklearn.cluster.spectral', 'discretize', Doi('10.1109/ICCV.2003.1238361'),
                 description="Multiclass spectral clustering", tags=['reference'])
    injector.add('sklearn.cluster.spectral', 'spectral_clustering', Doi('10.1109/34.868688'),
                 description="Spectral clustering", tags=['implementation'])
    injector.add('sklearn.cluster.spectral', 'spectral_clustering', Doi('10.1007/s11222-007-9033-z'),
                 description="Spectral clustering", tags=['implementation'])

    # sklearn.ensemble.forest and tree
    Breiman_2001 = Doi("10.1023/A:1010933404324")
    Breiman_1984 = BibTeX("""@BOOK{breiman-friedman-olshen-stone-1984,
  author        = {L. Breiman and J. Friedman and R. Olshen and C. Stone},
  title         = {{Classification and Regression Trees}},
  publisher     = {Wadsworth and Brooks},
  address       = {Monterey, CA},
  year          = {1984},
}""")
    # Not clear here though if those are the original publication on the topic
    # or just an educational references (books), most probably both ;)
    injector.add('sklearn.ensemble.forest', 'RandomForestClassifier.predict_proba', Breiman_2001,
                 description="Random forest classifiers",
                 tags=['implementation', 'edu'])
    injector.add('sklearn.ensemble.forest', 'RandomForestRegressor.predict', Breiman_2001,
                 description="Random forest regressions",
                 tags=['implementation', 'edu'])
    injector.add('sklearn.tree.tree', 'DecisionTreeClassifier.predict_proba', Breiman_1984,
                 description="Classification and regression trees",
                 tags=['implementation', 'edu'])

