# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import sys

from mock import patch
from six.moves import StringIO
from nose.tools import assert_raises, assert_equal

from .. import __version__
from ..cmdline import main

def test_import():
    import duecredit.cmdline
    import duecredit.cmdline.main

@patch('sys.stdout', new_callable=StringIO)
def test_main_help(stdout):
    assert_raises(SystemExit, main.main, ['--help'])
    assert(stdout.getvalue().lstrip().startswith("Usage: "))

# differs among Python versions -- catch both
@patch('sys.std' + ('err' if sys.version_info < (3, 4) else 'out'), new_callable=StringIO)
def test_main_version(out):
    assert_raises(SystemExit, main.main, ['--version'])
    assert_equal((out.getvalue()).split('\n')[0], "duecredit %s" % __version__)

# smoke test the cmd_summary
# TODO: carry sample .duecredit.p, point to that file, mock TextOutput and BibTeXOutput .dumps
def test_smoke_cmd_summary():
    main.main(['summary'])

# test the not implemented cmd_test
def test_cmd_test():
    assert_raises(SystemExit, main.main, ['test'])