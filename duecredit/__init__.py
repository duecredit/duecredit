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

import os

from .entries import Doi, BibTeX, Donate
from .version import __version__, __release_date__

from .log import lgr
from .utils import never_fail

def is_active():
    env_enable = os.environ.get('DUECREDIT_ENABLE')
    if env_enable and env_enable.lower() in ('1', 'yes'):
        return True
    return False

@never_fail
def _get_active_due():
    from .config import CACHE_DIR, DUECREDIT_FILE
    from duecredit.collector import CollectorSummary, DueCreditCollector
    from .io import load_due
    import atexit
    # where to cache bibtex entries
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    if os.path.exists(DUECREDIT_FILE):
        due = load_due(DUECREDIT_FILE)
    else:
        due = DueCreditCollector()

    # Wrapper to create and dump summary... passing method doesn't work:
    #  probably removes instance too early
    def crap():
        _due_summary = CollectorSummary(due)
        _due_summary.dump()

    atexit.register(crap)

    # Deal with injector
    from .injections import DueCreditInjector
    injector = DueCreditInjector()
    injector.activate()
    #injector.deactivate()
    return due

def _get_due(active=False):
    """Returns "due" Collector (real or a stub) and sets up dumping atexit for active one
    """

    # Rebind the collector's methods to the module here
    if active or is_active():
        due = _get_active_due()
    else:
        due = None

    # if not active or failed to activate
    if due is None:
        # keeping duplicate but separate so later we could even place it into a separate
        # submodule to possibly minimize startup time impact even more
        #
        # provide stubs which would do nothing
        from .collector import InactiveDueCreditCollector
        due = InactiveDueCreditCollector()
    return due


due = _get_due()

# be friendly on systems with ancient numpy -- no tests, but at least
# importable
try:
    from numpy.testing import Tester as _Tester
    test = _Tester().test
    _bench = _Tester().bench
    del _Tester
except ImportError:
    def test(*args, **kwargs):
        raise RuntimeError('Need numpy >= 1.2 for duecredit.tests()')
test.__test__ = False

# Minimize default imports
__all__ = [ 'Doi', 'BibTeX', 'Donate', 'due' ]