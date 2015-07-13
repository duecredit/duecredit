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

import logging
import os
import pickle
import sys

from .entries import *
from .version import __version__, __release_date__

lgr = logging.getLogger('duecredit')
lgr.setLevel(logging.DEBUG)

lgr.addHandler(logging.StreamHandler(sys.stdout))

CACHE_DIR = os.path.expanduser(os.path.join('~', '.cache', 'duecredit', 'bibtex'))
DUECREDIT_FILE = '.duecredit.p'

def is_active():
    env_enable = os.environ.get('DUECREDIT_ENABLE')
    if env_enable and env_enable.lower() in ('1', 'yes'):
        return True
    return False

def get_due():
    from .io import PickleOutput
    from .collector import DueCreditCollector
    if os.path.exists(DUECREDIT_FILE):
        return PickleOutput.load(DUECREDIT_FILE)
    else:
        return DueCreditCollector()

# Rebind the collector's methods to the module here
if is_active():
    from .collector import CollectorSummary
    import atexit
    # where to cache bibtex entries
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    due = get_due()  # hidden in a function to avoid circular import of .io
    # Wrapper to create and dump summary... passing method doesn't work:
    #  probably removes instance too early
    def crap():
        _due_summary = CollectorSummary(due)
        _due_summary.dump()
    atexit.register(crap)
else:
    # keeping duplicate but separate so later we could even place it into a separate
    # submodule to possibly minimize startup time impact even more
    #
    # provide stubs which would do nothing
    from .collector import InactiveDueCreditCollector
    due = InactiveDueCreditCollector()


# be friendly on systems with ancient numpy -- no tests, but at least
# importable
try:
    from numpy.testing import Tester
    test = Tester().test
    bench = Tester().bench
    del Tester
except ImportError:
    def test(*args, **kwargs):
        raise RuntimeError('Need numpy >= 1.2 for duecredit.tests()')

from . import log

# Deal with injector
from .injections import injector

injector.activate()
#import mvpa2.suite
#injector.deactivate()
