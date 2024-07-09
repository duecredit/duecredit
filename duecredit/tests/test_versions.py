# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from os import linesep
import pytest

from ..version import __version__
from ..versions import ExternalVersions, StrictVersion

from six import PY3

if PY3:
    # just to ease testing
    def cmp(a, b):
        return (a > b) - (a < b)


def test_external_versions_basic():
    ev = ExternalVersions()
    assert ev._versions == {}
    assert ev['duecredit'] == __version__
    # and it could be compared
    assert ev['duecredit'] >= __version__
    assert ev['duecredit'] > '0.1'
    assert list(ev.keys()) == ['duecredit']
    assert 'duecredit' in ev
    assert 'unknown' not in ev

    # StrictVersion might remove training .0
    version_str = str(ev['duecredit']) \
        if isinstance(ev['duecredit'], StrictVersion) \
        else __version__
    assert ev.dumps() == "Versions: duecredit=%s" % version_str

    # For non-existing one we get None
    assert ev['duecreditnonexisting'] is None

    # and nothing gets added to _versions for nonexisting
    assert set(ev._versions.keys()) == {'duecredit'}

    # but if it is a module without version, we get it set to UNKNOWN
    assert ev['os'] == ev.UNKNOWN
    # And get a record on that inside
    assert ev._versions.get('os') == ev.UNKNOWN
    # And that thing is "True", i.e. present
    assert(ev['os'])
    # but not comparable with anything besides itself (was above)
    with pytest.raises(TypeError):
        cmp(ev['os'], '0')

    # assert_raises(TypeError, assert_greater, ev['os'], '0')

    # And we can get versions based on modules themselves
    from duecredit.tests import mod
    assert ev[mod] == mod.__version__

    # Check that we can get a copy of the versions
    versions_dict = ev.versions
    versions_dict['duecredit'] = "0.0.1"
    assert versions_dict['duecredit'] == "0.0.1"
    assert ev['duecredit'] == __version__


def test_external_versions_unknown():
    assert str(ExternalVersions.UNKNOWN) == 'UNKNOWN'


def _test_external(ev, modname):
    try:
        exec("import %s" % modname, globals(), locals())
    except ImportError:
        modname = pytest.importorskip(modname)
    except Exception as e:
        pytest.skip("External %s fails to import: %s" % (modname, e))
    assert ev[modname] is not ev.UNKNOWN
    assert ev[modname] > '0.0.1'
    assert '1000000.0' > ev[modname]  # unlikely in our lifetimes


@pytest.mark.parametrize("modname", ['scipy', 'numpy', 'mvpa2', 'sklearn', 'statsmodels',
                                     'pandas', 'matplotlib', 'psychopy'])
def test_external_versions_popular_packages(modname):
    ev = ExternalVersions()

    _test_external(ev, modname)

    # more of a smoke test
    assert linesep not in ev.dumps()
    assert ev.dumps(indent=True).endswith(linesep)
