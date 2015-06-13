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
import pickle
import sys

from .entries import *
from .version import __version__, __release_date__

lgr = logging.getLogger('duecredit')
lgr.setLevel(logging.DEBUG)

lgr.addHandler(logging.StreamHandler(sys.stdout))

def is_active():
    env_enable = os.environ.get('DUECREDIT_ENABLE')
    if env_enable and env_enable.lower() in ('1', 'yes'):
        return True
    return False

# Rebind the collector's methods to the module here
if is_active():
    from .collector import DueCreditCollector, CollectorGrave
    # where to cache bibtex entries
    cache_dir = '~/.cache/duecredit/bibtex'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if os.path.exists('.duecredit.p'):
        with open('.duecredit.p') as f:
            due = pickle.load(f)
    else:
        due = DueCreditCollector()
    _export_upon_del = CollectorGrave(due)

else:
    # keeping duplicate but separate so later we could even place it into a separate
    # submodule to possibly minimize startup time impact even more
    #
    # provide stubs which would do nothing
    from .collector import InactiveDueCreditCollector
    due = InactiveDueCreditCollector

