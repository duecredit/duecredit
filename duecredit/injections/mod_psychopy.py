# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
Automatic injection of bibliography entries for psychopy module
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..entries import Doi

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None

if TYPE_CHECKING:
    from .injector import DueCreditInjector


def inject(injector: DueCreditInjector) -> None:
    injector.add(
        "psychopy",
        None,
        Doi("doi:10.1016/j.jneumeth.2006.11.017"),
        description="PsychoPy -- Psychophysics software in Python.",
        tags=["implementation"],
    )

    injector.add(
        "psychopy",
        None,
        Doi("10.3389/neuro.11.010.2008"),
        description="Generating stimuli for neuroscience using PsychoPy.",
        tags=["implementation"],
    )
