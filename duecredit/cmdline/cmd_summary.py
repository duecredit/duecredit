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
from .. import DUECREDIT_FILE, lgr

__docformat__ = 'restructuredtext'

# magic line for manpage summary
# man: -*- % summary of collected citations

def setup_parser(parser):

    parser.add_argument(
        "-f", "--filename", default=DUECREDIT_FILE,
        help="Filename containing collected citations. Default: %(default)s")

    parser.add_argument(
        "--style", default="apa",
        help="Style to be used for listing citations")

def run(args):
    from ..io import PickleOutput
    if not os.path.exists(args.filename):
        lgr.debug("File %s doesn't exist.  No summary available")
        return 1

    due = PickleOutput.load(DUECREDIT_FILE)

    print "TODO"


