# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import os
import sys
import pytest
from os.path import dirname, join as pathjoin, pardir, normpath
from subprocess import Popen, PIPE

from duecredit.collector import DueCreditCollector
from duecredit.stub import InactiveDueCreditCollector
from duecredit.entries import BibTeX, Doi

from ..utils import on_windows

badlxml_path = pathjoin(dirname(__file__), 'envs', 'nolxml')
stubbed_script = pathjoin(dirname(__file__), 'envs', 'stubbed', 'script.py')


def _test_api(due):
    # add references
    due.add(BibTeX('@article{XXX00, ...}'))
    # could even be by DOI -- we need to fetch and cache those
    due.add(Doi("xxx.yyy/zzz.1", key="XXX01"))

    # and/or load multiple from a file
    due.load('/home/siiioul/deep/good_intentions.bib')

    # Cite entire module
    due.cite('XXX00', description="Answers to existential questions", path="module")
    # Cita some method within some submodule
    due.cite('XXX01', description="More answers to existential questions",
             path="module.submodule:class1.whoknowswhat2.func1")

    # dcite  for decorator cite
    # cite specific functionality if/when it gets called up
    @due.dcite('XXX00', description="Provides an answer for meaningless existence")
    def purpose_of_life():
        return None

    class Child(object):
        # Conception process is usually way too easy to be referenced
        def __init__(self):
            pass

        # including functionality within/by the methods
        @due.dcite('XXX00')
        def birth(self, gender):
            return "Rachel was born"

    kid = Child()
    kid.birth("female")


def test_api():
    _test_api(DueCreditCollector())
    _test_api(InactiveDueCreditCollector())


def run_python_command(cmd=None, script=None):
    """Just a tiny helper which runs command and returns exit code, stdout, stderr"""
    assert bool(cmd) != bool(script)  # one or another, not both
    args = ['-c', cmd] if cmd else [script]
    python = Popen([sys.executable] + args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = python.communicate()  # wait()
    ret = python.poll()
    # TODO stdout cannot decode on Windows special character /x introduced
    return ret, stdout.decode(errors='ignore'), stderr.decode()


# Since duecredit and possibly lxml already loaded, let's just test
# ability to import in absence of lxml via external call to python
def test_noincorrect_import_if_no_lxml(monkeypatch):
    if on_windows:
        pytest.xfail("Fails for some reason on Windows")

    monkeypatch.setitem(os.environ, 'PYTHONPATH', "%s:%s" % (badlxml_path, os.environ.get('PYTHONPATH', '')))
    ret, out, err = run_python_command('import lxml')
    assert ret == 1
    assert 'ImportError' in err

    ret, out, err = run_python_command('import duecredit')
    assert err == ''
    assert out == ''
    assert ret == 0


def check_noincorrect_import_if_no_lxml_numpy(monkeypatch, kwargs, env):
    # Now make sure that we would not crash entire process at the end when unable to
    # produce sensible output when we have something to cite
    # we do inject for numpy
    try:
        import numpy
    except ImportError:
        pytest.skip("We need to have numpy to test correct operation")

    if on_windows:
        pytest.xfail("Fails for some reason on Windows")

    fake_env_nolxml_ = {'PYTHONPATH': "%s:%s" % (badlxml_path, os.environ.get('PYTHONPATH', ''))}.copy()
    fake_env_nolxml_.update(env)

    for key in fake_env_nolxml_:
        monkeypatch.setitem(os.environ, key, fake_env_nolxml_[key])

    ret, out, err = run_python_command(**kwargs)
    assert err == ''
    if os.environ.get('DUECREDIT_ENABLE', False) and on_windows:  # TODO this test fails on windows
        pytest.xfail("Fails for some reason on Windows")
    elif os.environ.get('DUECREDIT_ENABLE', False):  # we enabled duecredit
        assert 'For formatted output we need citeproc' in out
        assert 'done123' in out
    elif os.environ.get('DUECREDIT_TEST_EARLY_IMPORT_ERROR'):
        assert 'ImportError' in out
        assert 'DUECREDIT_TEST_EARLY_IMPORT_ERROR' in out
        assert 'done123' in out
    else:
        assert 'done123\n' or 'done123\r\n' == out
    assert ret == 0  # but we must not fail overall regardless


@pytest.mark.parametrize("env", [{}, {'DUECREDIT_ENABLE': 'yes'},
                                 {'DUECREDIT_TEST_EARLY_IMPORT_ERROR': 'yes'}])
def test_noincorrect_import_if_no_lxml_numpy(monkeypatch, env):
    for kwargs in (
        # direct command to evaluate
        {'cmd': 'import duecredit; import numpy as np; print("done123")'},
        # script with decorated funcs etc -- should be importable
        {'script': stubbed_script}
    ):
        check_noincorrect_import_if_no_lxml_numpy(monkeypatch, kwargs, env)


if __name__ == '__main__':
    from duecredit import due
    _test_api(due)
