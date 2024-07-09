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
from __future__ import annotations

from typing import TYPE_CHECKING

from ..entries import BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None

if TYPE_CHECKING:
    from .injector import DueCreditInjector


def inject(injector: DueCreditInjector) -> None:
    injector.add(
        "pandas",
        None,
        BibTeX(
            """
        @InProceedings{ mckinney-proc-scipy-2010,
          author    = { McKinney, Wes },
          title     = { Data Structures for Statistical Computing in Python },
          booktitle = { Proceedings of the 9th Python in Science Conference },
          pages     = { 51 -- 56 },
          year      = { 2010 },
          editor    = { van der Walt, St\'efan and Millman, Jarrod }
        }
    """
        ),
        description="Data analysis library for tabular data",
    )
