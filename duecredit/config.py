# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Configuration handling for duecredit"""

import os
# For now just hardcoded variables

CACHE_DIR = os.path.expanduser(os.path.join('~', '.cache', 'duecredit', 'bibtex'))
DUECREDIT_FILE = '.duecredit.p'

