# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Automatic injection of bibliography entries for scipy module
"""

from ..entries import Doi, BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('scipy', None, BibTeX("""
    @Misc{JOP+01,
      author =    {Eric Jones and Travis Oliphant and Pearu Peterson and others},
      title =     {{SciPy}: Open source scientific tools for {Python}},
      year =      {2001--},
      url = "http://www.scipy.org/",
      note = {[Online; accessed 2015-07-13]}
    }"""), description="Scientific tools library")

    injector.add('scipy.cluster.hierarchy', 'ward', BibTeX("""
    @article{ward1963hierarchical,
        title={Hierarchical grouping to optimize an objective function},
        author={Ward Jr, Joe H},
        journal={Journal of the American statistical association},
        volume={58},
        number={301},
        pages={236--244},
        year={1963},
        publisher={Taylor \& Francis}
    }"""), description="Ward hierarchical clustering", min_version='v0.4.3')

    injector.add('scipy.cluster.hierarchy', 'single', BibTeX("""
    @article{gower1969minimum,
        title={Minimum spanning trees and single linkage cluster analysis},
        author={Gower, John C and Ross, GJS},
        journal={Applied statistics},
        pages={54--64},
        year={1969},
        publisher={JSTOR}
    }"""), description="Single linkage hierarchical clustering")

    injector.add('scipy.cluster.hierarchy', 'single', BibTeX("""
    @article{sibson1973slink,
        title={SLINK: an optimally efficient algorithm for the single-link
        cluster method},
        author={Sibson, Robin},
        journal={The Computer Journal},
        volume={16},
        number={1},
        pages={30--34},
        year={1973},
        publisher={Br Computer Soc}
    }"""), description="Single linkage hierarchical clustering")
