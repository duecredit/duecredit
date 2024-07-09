# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
from __future__ import annotations

from io import StringIO
import sys

import pytest
from pytest import MonkeyPatch

from .. import __version__
from ..cmdline import main


def test_import() -> None:
    import duecredit.cmdline  # noqa: F401
    import duecredit.cmdline.main  # noqa: F401


def test_main_help(monkeypatch: MonkeyPatch) -> None:
    # Patch stdout
    fakestdout = StringIO()
    monkeypatch.setattr(sys, "stdout", fakestdout)

    pytest.raises(SystemExit, main.main, ["--help"])
    assert fakestdout.getvalue().lstrip().startswith("Usage: ")


def test_main_version(monkeypatch: MonkeyPatch) -> None:
    # Patch stdout or stderr for different Python versions -- catching both
    fakestdout = StringIO()
    fakeout = "stdout"
    monkeypatch.setattr(sys, fakeout, fakestdout)

    pytest.raises(SystemExit, main.main, ["--version"])
    assert (fakestdout.getvalue()).split("\n")[0] == "duecredit %s" % __version__


# smoke test the cmd_summary
# TODO: carry sample .duecredit.p, point to that file, monkeypatch TextOutput and BibTeXOutput .dumps
def test_smoke_cmd_summary() -> None:
    main.main(["summary"])


def test_cmd_test() -> None:  # test the not implemented cmd_test
    pytest.raises(SystemExit, main.main, ["test"])
