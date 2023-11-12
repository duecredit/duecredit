# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import sys
from io import StringIO

import pytest

from .. import __version__
from ..cmdline import main


def test_import():
    import duecredit.cmdline
    import duecredit.cmdline.main


def test_main_help(monkeypatch):
    # Patch stdout
    fakestdout = StringIO()
    monkeypatch.setattr(sys, "stdout", fakestdout)

    pytest.raises(SystemExit, main.main, ['--help'])
    assert fakestdout.getvalue().lstrip().startswith("Usage: ")


def test_main_version(monkeypatch):
    # Patch stdout or stderr for different Python versions -- catching both
    fakestdout = StringIO()
    fakeout = 'stdout'
    monkeypatch.setattr(sys, fakeout, fakestdout)

    pytest.raises(SystemExit, main.main, ['--version'])
    assert (fakestdout.getvalue()).split('\n')[0] == "duecredit %s" % __version__


# smoke test the cmd_summary
# TODO: carry sample .duecredit.p, point to that file, monkeypatch TextOutput and BibTeXOutput .dumps
def test_smoke_cmd_summary():
    main.main(['summary'])


def test_cmd_test():  # test the not implemented cmd_test
    pytest.raises(SystemExit, main.main, ['test'])
