# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Spit out the summary of the citations which were collected.

"""
from __future__ import annotations

import argparse
import os
import sys

from ..config import DUECREDIT_FILE
from ..io import BibTeXOutput, TextOutput
from ..log import lgr

__docformat__ = "restructuredtext"

# magic line for manpage summary
# man: -*- % summary of collected citations


def setup_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--filename",
        default=DUECREDIT_FILE,
        help="Filename containing collected citations. Default: %(default)s",
    )

    parser.add_argument(
        "--style",
        choices=("apa", "harvard1"),
        default="harvard1",
        help="Style to be used for listing citations",
    )

    parser.add_argument(
        "--format",
        choices=("text", "bibtex"),
        default="text",
        help="Way to present the summary",
    )


def run(args: argparse.Namespace) -> int:
    from ..io import PickleOutput

    if not os.path.exists(args.filename):
        lgr.debug("File {} doesn't exist.  No summary available".format(args.filename))
        return 1

    due = PickleOutput.load(args.filename)
    # CollectorSummary(due).dump()

    out: TextOutput | BibTeXOutput
    if args.format == "text":
        out = TextOutput(sys.stdout, due, args.style)
    elif args.format == "bibtex":
        out = BibTeXOutput(sys.stdout, due)
    else:
        raise ValueError("unknown to treat %s" % args.format)
    out.dump()
    return 0
