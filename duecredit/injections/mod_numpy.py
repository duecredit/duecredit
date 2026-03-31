# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Automatic injection of bibliography entries for numpy module"""

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
        "numpy",
        None,
        BibTeX(
            r"""
    @article{harris2020array,
        title={Array programming with {NumPy}},
        author={Harris, Charles R. and Millman, K. Jarrod and
            van der Walt, St{\'e}fan J and Gommers, Ralf and
            Virtanen, Pauli and Cournapeau, David and
            Wieser, Eric and Taylor, Julian and Berg, Sebastian and
            Smith, Nathaniel J. and Kern, Robert and Picus, Matti and
            Hoyer, Stephan and van Kerkwijk, Marten H. and
            Brett, Matthew and Haldane, Allan and
            Fern{\'a}ndez del R{\'i}o, Jaime and Wiebe, Mark and
            Peterson, Pearu and G{\'e}rard-Marchant, Pierre and
            Sheppard, Kevin and Reddy, Tyler and Weckesser, Warren and
            Abbasi, Hameer and Gohlke, Christoph and
            Oliphant, Travis E.},
        journal={Nature},
        volume={585},
        pages={357--362},
        year={2020},
        doi={10.1038/s41586-020-2649-2}
        }
    """
        ),
        tags=["implementation"],
        cite_module=True,
        description="Scientific tools library",
    )
