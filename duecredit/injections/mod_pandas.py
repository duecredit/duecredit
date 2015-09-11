# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Automatic injection of bibliography entries for pandas module
"""

from ..entries import Doi, BibTeX, Url

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('pandas', None, BibTeX("""
        @InProceedings{ mckinney-proc-scipy-2010,
          author    = { Wes McKinney },
          title     = { Data Structures for Statistical Computing in Python },
          booktitle = { Proceedings of the 9th Python in Science Conference },
          pages     = { 51 - 56 },
          year      = { 2010 },
          editor    = { St\'efan van der Walt and Jarrod Millman }
        }
    """), description="Data analysis library for tabular data")