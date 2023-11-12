# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.   Originates from datalad package distributed
#   under MIT license
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import sys

from ..utils import is_interactive


def test_is_interactive_crippled_stdout(monkeypatch):
    class MockedOut:
        """the one which has no isatty
        """
        def write(self, *args, **kwargs):
            pass

    class MockedIsaTTY(MockedOut):
        def isatty(self):
            return True

    for inout in ('in', 'out', 'err'):
        monkeypatch.setattr(sys, 'std%s' % inout, MockedOut())
        assert not is_interactive()

    # just for paranoids
    for inout in ('in', 'out', 'err'):
        monkeypatch.setattr(sys, 'std%s' % inout, MockedIsaTTY())
    assert is_interactive()
