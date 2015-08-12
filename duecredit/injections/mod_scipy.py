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
    }"""),
                 description="Scientific tools library",
                 tags=['implementation'])

    # scipy.cluster.hierarchy general references
    # TODO: we should allow to pass a list of entries
    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @article{johnson1967hierarchical,
        title={Hierarchical clustering schemes},
        author={Johnson, Stephen C},
        journal={Psychometrika},
        volume={32},
        number={3},
        pages={241--254},
        year={1967},
        publisher={Springer}
    }"""),
                 min_version='0.4.3',
                 description="Hierarchical clustering",
                 tags=['edu'])

    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @article{sneath1962numerical,
        title={Numerical taxonomy},
        author={Sneath, Peter HA and Sokal, Robert R},
        journal={Nature},
        volume={193},
        number={4818},
        pages={855--860},
        year={1962},
        publisher={Nature Publishing Group}
    }"""),
                 description="Hierarchical clustering",
                 min_version='0.4.3',
                 tags=['edu'])

    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @article{batagelj1995comparing,
        title={Comparing resemblance measures},
        author={Batagelj, Vladimir and Bren, Matevz},
        journal={Journal of classification},
        volume={12},
        number={1},
        pages={73--90},
        year={1995},
        publisher={Springer}
    }"""),
                 description="Hierarchical clustering",
                 min_version='0.4.3',
                 tags=['edu'])

    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @book{sokal1958statistical,
        author = {Sokal, R R and Michener, C D and {University of Kansas}},
        title = {{A Statistical Method for Evaluating Systematic Relationships}},
        publisher = {University of Kansas},
        year = {1958},
        series = {University of Kansas science bulletin}
    }"""),
                 description="Hierarchical clustering",
                 min_version='0.4.3',
                 tags=['edu'])

    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @article{edelbrock1979mixture,
        title={Mixture model tests of hierarchical clustering algorithms:
            the problem of classifying everybody},
        author={Edelbrock, Craig},
        journal={Multivariate Behavioral Research},
        volume={14},
        number={3},
        pages={367--384},
        year={1979},
        publisher={Taylor \& Francis}
    }"""),
                 description="Hierarchical clustering",
                 min_version='0.4.3',
                 tags=['edu'])

    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @book{jain1988algorithms,
        title={Algorithms for clustering data},
        author={Jain, Anil K and Dubes, Richard C},
        year={1988},
        publisher={Prentice-Hall, Inc.}
    }"""),
                 description="Hierarchical clustering",
                 min_version='0.4.3',
                 tags=['edu'])

    injector.add('scipy.cluster.hierarchy', None, BibTeX("""
    @article{fisher1936use,
        title={The use of multiple measurements in taxonomic problems},
        author={Fisher, Ronald A},
        journal={Annals of eugenics},
        volume={7},
        number={2},
        pages={179--188},
        year={1936},
        publisher={Wiley Online Library}
    }"""),
                 description="Hierarchical clustering",
                 min_version='0.4.3',
                 tags=['edu'])

    # Here options for linkage
    injector.add('scipy.cluster.hierarchy', 'linkage', BibTeX("""
    @article{ward1963hierarchical,
        title={Hierarchical grouping to optimize an objective function},
        author={Ward Jr, Joe H},
        journal={Journal of the American statistical association},
        volume={58},
        number={301},
        pages={236--244},
        year={1963},
        publisher={Taylor \& Francis}
    }"""),
                 conditions={(1, 'method'): {'ward'}},
                 description="Ward hierarchical clustering",
                 min_version='0.4.3',
                 tags=['reference'])

    injector.add('scipy.cluster.hierarchy', 'linkage', BibTeX("""
    @article{gower1969minimum,
        title={Minimum spanning trees and single linkage cluster analysis},
        author={Gower, John C and Ross, GJS},
        journal={Applied statistics},
        pages={54--64},
        year={1969},
        publisher={JSTOR}
    }"""),
                 conditions={(1, 'method'): {'single', 'DC_DEFAULT'}},
                 description="Single linkage hierarchical clustering",
                 min_version='0.4.3',
                 tags=['reference'])

    injector.add('scipy.cluster.hierarchy', 'linkage', BibTeX("""
    @article{sibson1973slink,
        title={SLINK: an optimally efficient algorithm for the single-link cluster method},
        author={Sibson, Robin},
        journal={The Computer Journal},
        volume={16},
        number={1},
        pages={30--34},
        year={1973},
        publisher={Br Computer Soc}
    }"""),
                 conditions={(1, 'method'): {'single', 'DC_DEFAULT'}},
                 description="Single linkage hierarchical clustering",
                 min_version='0.4.3',
                 tags=['implementation'])
