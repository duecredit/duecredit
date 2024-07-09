# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Run internal DueCredit (unit)tests to verify correct operation on the system"""


__docformat__ = 'restructuredtext'

# magic line for manpage summary
# man: -*- % run unit-tests

from .helpers import parser_add_common_args

import nose

def setup_parser(parser):
    # TODO -- pass options such as verbosity etc
    pass
    
def run(args):
    import duecredit
    raise NotImplementedError("Just use nosetests duecredit for now")
    #duecredit.test()
