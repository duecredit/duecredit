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
from mock import patch

from ..utils import is_interactive
from nose.tools import assert_false, assert_true

def test_is_interactive_crippled_stdout():
    class mocked_out(object):
        """the one which has no isatty
        """
        def write(self, *args, **kwargs):
            pass

    class mocked_isatty(mocked_out):
        def isatty(self):
            return True

    for inout in ('in', 'out', 'err'):
        with patch('sys.std%s' % inout, mocked_out()):
            assert_false(is_interactive())

    # just for paranoids
    with patch('sys.stdin', mocked_isatty()), \
            patch('sys.stdout', mocked_isatty()), \
            patch('sys.stderr', mocked_isatty()):
        assert_true(is_interactive())