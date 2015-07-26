# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from ..utils import ExternalVersions
from ..version import __version__

from nose.tools import assert_equal, assert_greater_equal, assert_greater
from nose.tools import assert_raises
from six import PY3

if PY3:
    # just to ease testing
    def cmp(a, b):
        return (a > b) - (a < b)

def test_external_versions_basic():
    ev = ExternalVersions()
    assert_equal(ev._versions, {})
    assert_equal(ev['duecredit'], __version__)
    # and it could be compared
    assert_greater_equal(ev['duecredit'], __version__)
    assert_greater(ev['duecredit'], '0.1')

    # For non-existing one we get None
    assert_equal(ev['duecreditnonexisting'], None)
    # and nothing gets added to _versions for nonexisting
    assert_equal(set(ev._versions.keys()), {'duecredit'})

    # but if it is a module without version, we get it set to UNKNOWN
    assert_equal(ev['os'], ev.UNKNOWN)
    # And get a record on that inside
    assert_equal(ev._versions.get('os'), ev.UNKNOWN)
    # And that thing is "True", i.e. present
    assert(ev['os'])
    # but not comparable with anything besides itself (was above)
    assert_raises(TypeError, cmp, ev['os'], '0')
    assert_raises(TypeError, assert_greater, ev['os'], '0')

    # And we can get versions based on modules themselves
    from duecredit.tests import mod
    assert_equal(ev[mod], mod.__version__)
