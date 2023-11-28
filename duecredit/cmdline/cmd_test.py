# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Run internal DueCredit (unit)tests to verify correct operation on the system"""
from __future__ import annotations

__docformat__ = "restructuredtext"

import argparse

# magic line for manpage summary
# man: -*- % run unit-tests


def setup_parser(parser: argparse.ArgumentParser) -> None:
    # TODO -- pass options such as verbosity etc
    pass


def run(_args: argparse.Namespace) -> None:
    import duecredit  # noqa: F401

    raise NotImplementedError("Just use pytest duecredit for now")
    # duecredit.test()
