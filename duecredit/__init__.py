# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Module/app to automate collection of relevant to analysis publications.

Please see README.md shipped along with duecredit to get a better idea about
its functionality
"""

from ._version import __version__
from .dueswitch import due
from .entries import BibTeX, Doi, Text, Url

__all__ = ["Doi", "BibTeX", "Url", "Text", "due", "__version__"]
