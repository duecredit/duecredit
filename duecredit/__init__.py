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

from .entries import Doi, BibTeX, Url
from .version import __version__, __release_date__

from .log import lgr
from .utils import never_fail

def _get_duecredit_enable():
    env_enable = os.environ.get('DUECREDIT_ENABLE', 'no')
    if not env_enable.lower() in ('0', '1', 'yes', 'no', 'true', 'false'):
        lgr.warning("Misunderstood value %s for DUECREDIT_ENABLE. "
                    "Use 'yes' or 'no', or '0' or '1'")
    return env_enable.lower() in ('1', 'yes', 'true')

@never_fail
def _get_inactive_due():
    # keeping duplicate but separate so later we could even place it into a separate
    # submodule to possibly minimize startup time impact even more
    from .collector import InactiveDueCreditCollector
    return InactiveDueCreditCollector()

@never_fail
def _get_active_due():
    from .config import CACHE_DIR, DUECREDIT_FILE
    from duecredit.collector import CollectorSummary, DueCreditCollector
    from .io import load_due
    import atexit
    # where to cache bibtex entries
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # TODO:  this needs to move to atexit handling, that we load previous
    # one and them merge with new ones.  Informative bits could be -- how
    # many new citations we got
    if os.path.exists(DUECREDIT_FILE):
        try:
            due_ = load_due(DUECREDIT_FILE)
        except Exception as e:
            lgr.warning("Failed to load previously collected %s. "
                        "DueCredit will not be active for this session."
                        % DUECREDIT_FILE)
            return _get_inactive_due()
    else:
        due_ = DueCreditCollector()

    # Wrapper to create and dump summary... passing method doesn't work:
    #  probably removes instance too early
    @never_fail
    def crap():
        _due_summary = CollectorSummary(due_)
        _due_summary.dump()

    atexit.register(crap)

    # Deal with injector
    from .injections import DueCreditInjector
    injector = DueCreditInjector(collector=due_)
    injector.activate()
    return due_

def _get_due(active=False):
    """Returns "due" Collector (real or a stub) and sets up dumping atexit for active one
    """

    # Rebind the collector's methods to the module here
    due_ = None
    if active or _get_duecredit_enable():
        due_ = _get_active_due()

    # if not active or failed to activate
    if due_ is None:
        due_ = _get_inactive_due()
    return due_

due = _get_due()

# TODO: REDO without numpy so we don't pollute the modules space and interfer with injections/citations

# be friendly on systems with ancient numpy -- no tests, but at least
# importable
# try:
#     from numpy.testing import Tester as _Tester
#     test = _Tester().test
#     _bench = _Tester().bench
#     del _Tester
# except ImportError:
#     def test(*args, **kwargs):
#         raise RuntimeError('Need numpy >= 1.2 for duecredit.tests()')
#    test.__test__ = False

# Minimize default imports
__all__ = ['Doi', 'BibTeX', 'Url', 'due']