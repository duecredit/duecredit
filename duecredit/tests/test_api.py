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
import warnings

import pytest
import shutil

from os.path import dirname, join as pathjoin, pardir, normpath
from subprocess import Popen, PIPE

from duecredit.collector import DueCreditCollector
from duecredit.stub import InactiveDueCreditCollector
from duecredit.entries import BibTeX, Doi

from ..utils import on_windows
import tempfile
# temporary location where stuff would be copied
badlxml_path = pathjoin(dirname(__file__), 'envs', 'nolxml')
stubbed_dir = tempfile.mktemp()
stubbed_script = pathjoin(pathjoin(stubbed_dir, 'script.py'))


@pytest.fixture(scope="module")
def stubbed_env():
    """Create stubbed module with a sample script"""
    os.makedirs(stubbed_dir)
    with open(stubbed_script, 'wb') as f:
        f.write("""
from due import due, Doi

kwargs = dict(
    entry=Doi("10.1007/s12021-008-9041-y"),
    description="Multivariate pattern analysis of neural data",
    tags=["use"]
)

due.cite(path="test", **kwargs)


@due.dcite(**kwargs)
def method(arg):
    return arg+1

assert method(1) == 2
print("done123")
""".encode())
    # copy stub.py under stubbed
    shutil.copy(
        pathjoin(dirname(__file__), os.pardir, 'stub.py'),
        pathjoin(stubbed_dir, 'due.py')
    )
    yield stubbed_script
    # cleanup
    shutil.rmtree(stubbed_dir)


@pytest.fixture
def duplicate_script(tmp_path):
    package_dir = tmp_path / "mypackage"
    package_dir.mkdir()
    with open(str(package_dir / "__init__.py"), "w") as f:
        f.write("""
from .due import BibTeX, due

bib_str = '''
@misc{ Nobody06,
       author = "Nobody Jr",
       title = "My Article",
       year = "2006" }
'''.strip()

due.cite(BibTeX(bib_str), path="mypackage")


@due.dcite(BibTeX(bib_str))
def hello():
    print("hello there!")
""".lstrip())

    shutil.copy(
        pathjoin(dirname(__file__), os.pardir, 'stub.py'),
        pathjoin(str(package_dir), 'due.py')
    )

    script_path = tmp_path / "myscript.py"
    with open(str(script_path), "w") as f:
        f.write("""
from mypackage import hello

hello()
""".lstrip())

    yield script_path


def test_no_duplicate(duplicate_script, monkeypatch):
    monkeypatch.setenv("DUECREDIT_ENABLE", "yes")
    cwd = str(duplicate_script.parent)
    ret, out, err = run_python_command(
        script=str(duplicate_script), cwd=cwd
    )
    if ret:
        warnings.warn(err)
    assert ret == 0
    assert "[2]" not in out
    assert "1 package" in out and "1 function" in out

    ret2, out2, err2 = run_command(
        ["duecredit", "summary", "--format", "bibtex"], cwd=cwd
    )

    if ret:
        warnings.warn(err2)
    warnings.warn(out2)
    assert ret2 == 0
    assert out2.count("@") == 1
    stripped = out2.strip()
    assert stripped.startswith('@')
    assert stripped.endswith('}')


@pytest.mark.parametrize(
    'collector_class', [DueCreditCollector, InactiveDueCreditCollector]
)
def test_api(collector_class):
    due = collector_class()
    # add references
    due.add(BibTeX('@article{XXX00, ...}'))
    # could even be by DOI -- we need to fetch and cache those
    due.add(Doi("xxx.yyy/zzz.1", key="XXX01"))

    # and/or load multiple from a file
    due.load('/home/siiioul/deep/good_intentions.bib')

    # Cite entire module
    due.cite('XXX00', description="Answers to existential questions", path="module")
    # Cite some method within some submodule
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


def run_command(args, cwd=None):
    try:
        # run script from some temporary directory so we do not breed .duecredit.p
        # in current directory
        if cwd is None:
            rm = True
            cwd = tempfile.mkdtemp()
        else:
            rm = False
        python = Popen(args, stdout=PIPE, stderr=PIPE, cwd=cwd)
        stdout, stderr = python.communicate()  # wait()
        ret = python.poll()
    finally:
        if rm:
            shutil.rmtree(cwd)
    # TODO stdout cannot decode on Windows special character /x introduced
    return ret, stdout.decode(errors='ignore'), stderr.decode()


def run_python_command(cmd=None, script=None, cwd=None):
    """Just a tiny helper which runs command and returns exit code, stdout, stderr"""
    assert bool(cmd) != bool(script)  # one or another, not both
    args = ['-c', cmd] if cmd else [script]

    return run_command([sys.executable] + args, cwd)


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


@pytest.mark.parametrize(
    "env", [{},
            {'DUECREDIT_ENABLE': 'yes'},
            {'DUECREDIT_ENABLE': 'yes', 'DUECREDIT_REPORT_TAGS' :'*'},
            {'DUECREDIT_TEST_EARLY_IMPORT_ERROR': 'yes'}
            ])
@pytest.mark.parametrize(
    "kwargs", [
        # direct command to evaluate
        {'cmd': 'import duecredit; import numpy as np; print("done123")'},
        # script with decorated funcs etc -- should be importable
        {'script': stubbed_script}
    ])
def test_noincorrect_import_if_no_lxml_numpy(monkeypatch, kwargs, env, stubbed_env):
    # Now make sure that we would not crash entire process at the end when unable to
    # produce sensible output when we have something to cite
    # we do inject for numpy
    try:
        import numpy
    except ImportError:
        pytest.skip("We need to have numpy to test correct operation")

    fake_env_nolxml_ = {'PYTHONPATH': "%s:%s" % (badlxml_path, os.environ.get('PYTHONPATH', ''))}.copy()
    fake_env_nolxml_.update(env)

    for key in fake_env_nolxml_:
        monkeypatch.setitem(os.environ, key, fake_env_nolxml_[key])

    ret, out, err = run_python_command(**kwargs)
    direct_duecredit_import = 'import duecredit' in kwargs.get('cmd', '')
    if direct_duecredit_import and env.get('DUECREDIT_TEST_EARLY_IMPORT_ERROR', ''):
        # We do fail then upon regular import but stubbed script should be ok
        # since should use the stub
        assert 'Both inactive and active collectors should be provided' in err
        assert ret == 1
    else:
        assert err == ''
        assert ret == 0  # but we must not fail overall regardless

    if os.environ.get('DUECREDIT_ENABLE', False) and on_windows:  # TODO this test fails on windows
        pytest.xfail("Fails for some reason on Windows")
    elif os.environ.get('DUECREDIT_ENABLE', False):  # we enabled duecredit
        if (os.environ.get('DUECREDIT_REPORT_TAGS', None) == '*' and kwargs.get('script')) \
            or 'numpy' in kwargs.get('cmd', ''):
            # we requested to have all tags output, and used bibtex in our entry
            assert 'For formatted output we need citeproc' in out
        else:
            # there was nothing to format so we did not fail for no reason
            assert 'For formatted output we need citeproc' not in out
            assert '0 packages cited' in out
        assert 'done123' in out
    elif os.environ.get('DUECREDIT_TEST_EARLY_IMPORT_ERROR'):
        assert 'ImportError' in out
        assert 'DUECREDIT_TEST_EARLY_IMPORT_ERROR' in out
        if direct_duecredit_import:
            assert 'Please report' in out
        else:
            assert 'done123' in out
    else:
        assert 'done123\n' or 'done123\r\n' == out


if __name__ == '__main__':
    from duecredit import due
    test_api(due)
