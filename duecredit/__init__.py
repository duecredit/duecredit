# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""TODO"""

import logging
import os

from .entries import *
from .version import __version__, __release_date__

lgr = logging.get('duecredit')
lgr.setLevel(logging.DEBUG)


def is_active():
    env_enable = os.environ.get('DUECREDIT_ENABLE')
    if env_enable and env_enable.lower() in ('1', 'yes'):
        return True
    return False

# Rebind the collector's methods to the module here
if is_active():
    from .collector import DueCreditCollector
    due = DueCreditCollector()
else:
    # provide stubs which would do nothing
    raise NotImplementedError()
    pass
