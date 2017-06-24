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

import sys
import os

from ..log import lgr
from ..config import DUECREDIT_FILE
from ..collector import CollectorSummary
from ..io import TextOutput, BibTeXOutput

__docformat__ = 'restructuredtext'

# magic line for manpage summary
# man: -*- % collect DueCredit citations defined in a module

def setup_parser(parser):

    parser.add_argument(
        "-f", "--filename", default=DUECREDIT_FILE,
        help="Filename to store collected citations into. Default: %(default)s")

    parser.add_argument(
        "-m", "--module",
        help="Module to collect all DueCredit citations from")


def run(args):
    from ..io import PickleOutput

    if args.filename and os.path.exists(args.filename):
        lgr.info("Reloading %s for initial collection", args.filename)
        due = PickleOutput.load(args.filename)
    else:
        from duecredit import due
        due.activate()
    # TODO: add a new mode where dcite would immediately collect

    # walk all the modules
    import pkgutil
    package = __import__(args.module, fromlist='dummy')
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__,
            prefix=package.__name__ + '.',
            onerror=lambda x: None):
        lgr.info("Importing module %s" % modname)
        try:
            module = __import__(modname, fromlist="dummy")
        except Exception as exc:
            lgr.info("Failed to import %s: %s", modname, exc)

    CollectorSummary(due).dump()
    if True:
        out = TextOutput(sys.stdout, due, args.style)
    out.dump()


