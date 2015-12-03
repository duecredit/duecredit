# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from duecredit.collector import DueCreditCollector
from duecredit.stub import InactiveDueCreditCollector
from duecredit.entries import BibTeX, Doi

from nose.tools import assert_equal
from nose.tools import assert_in
from nose import SkipTest

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
    yield _test_api, DueCreditCollector()
    yield _test_api, InactiveDueCreditCollector()

import os
import sys
from os.path import dirname, join as pathjoin, pardir, normpath
from mock import patch
from subprocess import Popen, PIPE

# Since duecredit and possibly lxml already loaded, let's just test
# ability to import in absence of lxml via external call to python
def test_noincorrect_import_if_no_lxml():
    badlxml_path = pathjoin(dirname(__file__), 'envs', 'nolxml')
    def run_python_command(cmd):
        """Just a tiny helper which runs command and returns exit code, stdout, stderr"""
        python = Popen([sys.executable, '-c', cmd], stdout=PIPE, stderr=PIPE)
        ret = python.wait()
        return ret, python.stdout.read().decode(), python.stderr.read().decode()

    mock_env = {'PYTHONPATH': "%s:%s" % (badlxml_path, os.environ.get('PYTHONPATH', ''))}
    with patch.dict(os.environ, mock_env):
        # make sure out mocking works here
        ret, out, err = run_python_command('import lxml')
        assert_equal(ret, 1)
        assert_in('ImportError', err)
        #
        # make sure out mocking works here
        ret, out, err = run_python_command('import duecredit')
        assert_equal(err, '')
        assert_equal(out, '')
        assert_equal(ret, 0)

    # Now make sure that we would not crash entire process at the end when unable to
    # produce sensible output when we have something to cite
    # we do inject for numpy
    try:
        import numpy
    except ImportError:
        raise SkipTest("We need to have numpy to test correct operation")
    for run in (0, 1):
        with patch.dict(os.environ, mock_env):
            # make sure out mocking works here
            ret, out, err = run_python_command('import duecredit; import numpy as np; print("done123")')
            assert_equal(err, '')
            if run == 1:  # we enabled duecredit
                assert_in('For formatted output we need citeproc', out)
                assert_in('done123', out)
            else:
                assert_equal('done123\n', out)
            assert_equal(ret, 0)  # but we must not fail overall regardless

        mock_env.update({'DUECREDIT_ENABLE': '1'})



if __name__ == '__main__':
    from duecredit import due
    _test_api(due)