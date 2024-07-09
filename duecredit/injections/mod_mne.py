# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
Automatic injection of bibliography entries for mne module
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
    # http://martinos.org/mne/stable/cite.html
    injector.add(
        "mne",
        None,
        Doi("10.1016/j.neuroimage.2013.10.027"),
        description="MNE software for processing MEG and EEG data.",
        tags=["implementation"],
    )
    injector.add(
        "mne",
        None,
        Doi("10.3389/fnins.2013.00267"),
        description="MEG and EEG data analysis with MNE-Python.",
        tags=["implementation"],
    )
