# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from mock import patch
import atexit

from nose import SkipTest

from ..injections.injector import DueCreditInjector
from ..dueswitch import due

@patch.object(DueCreditInjector, 'activate')
@patch.object(atexit, 'register')
def test_dueswitch_activate(mock_register, mock_activate):
    was_active = due.active
    # atexit.register(crap)
    # injector.activate()
    due.activate()
    if was_active:
        # we can only test that mocked methods do not invoked second time
        mock_activate.assert_not_called()
        mock_register.assert_not_called()
        raise SkipTest("due is already active, can't test more at this point")
    # was not active, so should have called activate of the injector class
    mock_activate.assert_called_once_with()
    mock_register.assert_called_once_with(due._dump_collector_summary)
