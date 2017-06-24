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

import os
import pkgutil
import warnings

from ..log import lgr
from ..config import DUECREDIT_FILE

__docformat__ = 'restructuredtext'

# magic line for manpage summary
# man: -*- % collect DueCredit citations defined in a module

def setup_parser(parser):

    parser.add_argument(
        "-f", "--filename", default=DUECREDIT_FILE,
        help="Filename to store collected citations into. Default: %(default)s")

    parser.add_argument(
        "-m", "--module",
        nargs='*',
        help="Module(s) to collect all DueCredit citations from")


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
    with warnings.catch_warnings():
        for module in args.module:
            lgr.info("Walking the %s module", module)
            # Warnings aren't related to our "task" at hands, so we ignore
            # them but we need to do it before each __import__ because
            package = safe_import(module)
            for importer, modname, ispkg in pkgutil.walk_packages(
                    path=package.__path__,
                    prefix=package.__name__ + '.',
                    onerror=lambda x: None):
                lgr.debug("Importing module %s" % modname)
                safe_import(modname)

    ## CollectorSummary(due).dump()
    # if True:
    #     out = TextOutput(sys.stdout, due) #, args.style)
    # out.dump()


def safe_import(modname):
    try:
        warnings.filterwarnings("ignore")
        return __import__(modname)
    except Exception as exc:
        lgr.debug("Failed to import %s: %s, skipped", modname, exc)


