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

from ..entries import Doi, BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('numpy', None, BibTeX(r"""
    @article{van2011numpy,
        title={The NumPy array: a structure for efficient numerical computation},
        author={Van Der Walt, Stefan and Colbert, S Chris and Varoquaux, Gael},
        journal={Computing in Science \& Engineering},
        volume={13},
        number={2},
        pages={22--30},
        year={2011},
        publisher={AIP Publishing},
        doi={10.1109/MCSE.2011.37}
        }
    """),
    tags=['implementation'],
    cite_module=True,
    description="Scientific tools library")
