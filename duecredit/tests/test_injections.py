# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import gc
import sys

from six import viewvalues, PY2

if PY2:
    import __builtin__
else:
    import builtins as __builtin__
_orig__import__ = __builtin__.__import__

from duecredit.collector import DueCreditCollector, InactiveDueCreditCollector
from duecredit.entries import BibTeX, Doi

from ..injections.injector import DueCreditInjector, find_object, get_modules_for_injection
from .. import __version__

from nose import SkipTest
from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_true

try:
    import mvpa2
    _have_mvpa2 = True
except ImportError:
    _have_mvpa2 = False

class TestActiveInjector(object):
    def setup(self):
        self._cleanup_modules()
        self.due = DueCreditCollector()
        self.injector = DueCreditInjector(collector=self.due)
        self.injector.activate(retrospect=False)  # numpy might be already loaded...

    def teardown(self):
        # gc might not pick up inj after some tests complete
        # so we will always deactivate explicitly
        self.injector.deactivate()
        assert_true(__builtin__.__import__ is _orig__import__)
        self._cleanup_modules()

    def _cleanup_modules(self):
        if 'duecredit.tests.mod' in sys.modules:
            sys.modules.pop('duecredit.tests.mod')

    def _test_simple_injection(self, func, import_stmt, func_call=None):
        assert_false('duecredit.tests.mod' in sys.modules)
        self.injector.add('duecredit.tests.mod', func,
                          Doi('1.2.3.4'),
                          description="Testing %s" % func,
                          min_version='0.1', max_version='1.0',
                          tags=["implementation", "very custom"])
        assert_false('duecredit.tests.mod' in sys.modules) # no import happening
        assert_equal(len(self.due._entries), 0)
        assert_equal(len(self.due.citations), 0)

        exec(import_stmt)

        assert_equal(len(self.due._entries), 1)   # we should get an entry now
        assert_equal(len(self.due.citations), 0)  # but not yet a citation

        import duecredit.tests.mod as mod
        _, _, obj = find_object(mod, func)
        assert_true(obj.__duecredited__)              # we wrapped
        assert_false(obj.__duecredited__ is obj)      # and it is not pointing to the same func
        assert_equal(obj.__doc__, "custom docstring") # we preserved docstring

        # TODO: test decoration features -- preserver __doc__ etc
        exec('ret = %s(None, "somevalue")' % (func_call or func))
        # XXX: awkwardly 'ret' is not found in the scope while running nosetests
        # under python3.4, although present in locals()... WTF?
        assert_equal(locals()['ret'], "%s: None, somevalue" % func)
        assert_equal(len(self.due._entries), 1)
        assert_equal(len(self.due.citations), 1)

        # TODO: there must be a cleaner way to get first value
        citation = list(viewvalues(self.due.citations))[0]
        # TODO: ATM we don't allow versioning of the submodules -- we should
        # assert_equal(citation.version, '0.5')
        # ATM it will be the duecredit's version
        assert_equal(citation.version, __version__)

        assert(citation.tags == ['implementation', 'very custom'])

    def test_simple_injection(self):
        yield self._test_simple_injection, "testfunc1", 'from duecredit.tests.mod import testfunc1'
        yield self._test_simple_injection, "TestClass1.testmeth1", \
              'from duecredit.tests.mod import TestClass1; c = TestClass1()', 'c.testmeth1'
        yield self._test_simple_injection, "TestClass12.Embed.testmeth1", \
              'from duecredit.tests.mod import TestClass12; c = TestClass12.Embed()', 'c.testmeth1'

    def test_delayed_entries(self):
        # verify that addition of delayed injections happened
        modules_for_injection = get_modules_for_injection()
        assert_equal(len(self.injector._delayed_injections), len(modules_for_injection))
        assert_equal(self.injector._entry_records, {})    # but no entries were added
        assert('scipy' in self.injector._delayed_injections)  # We must have it ATM

        try:
            # We do have injections for scipy
            import scipy
        except ImportError as e:
            raise SkipTest("scipy was not found: %s" % (e,))

    def test_import_mvpa2_suite(self):
        if not _have_mvpa2:
            raise SkipTest("no mvpa2 found")
        # just a smoke test for now
        import mvpa2.suite as mv

    def _test_incorrect_path(self, mod, obj):
        ref = Doi('1.2.3.4')
        # none of them should lead to a failure
        self.injector.add(mod, obj, ref)
        # now cause the import handling -- it must not fail
        # TODO: catch/analyze warnings
        exec('from duecredit.tests.mod import testfunc1')

    def test_incorrect_path(self):
        yield self._test_incorrect_path, "nonexistingmodule", None
        yield self._test_incorrect_path, "duecredit.tests.mod.nonexistingmodule", None
        yield self._test_incorrect_path, "duecredit.tests.mod", "nonexisting"
        yield self._test_incorrect_path, "duecredit.tests.mod", "nonexisting.whocares"



def _test_find_object(mod, path, parent, obj_name, obj):
    assert_equal(find_object(mod, path), (parent, obj_name, obj))

def test_find_object():
    import duecredit.tests.mod as mod
    yield _test_find_object, mod, 'testfunc1', mod, 'testfunc1', mod.testfunc1
    yield _test_find_object, mod, 'TestClass1', mod, 'TestClass1', mod.TestClass1
    yield _test_find_object, mod, 'TestClass1.testmeth1', mod.TestClass1, 'testmeth1', mod.TestClass1.testmeth1
    yield _test_find_object, mod, 'TestClass12.Embed.testmeth1', \
          mod.TestClass12.Embed, 'testmeth1', mod.TestClass12.Embed.testmeth1

def test_no_double_activation():
    orig__import__ = __builtin__.__import__
    try:
        due = DueCreditCollector()
        injector = DueCreditInjector(collector=due)
        injector.activate()
        assert_false(__builtin__.__import__ is orig__import__)
        duecredited__import__ = __builtin__.__import__
        # TODO: catch/analyze/swallow warning
        injector.activate()
        assert_true(__builtin__.__import__ is duecredited__import__) # we didn't decorate again
    finally:
        injector.deactivate()
        __builtin__.__import__ = orig__import__

def test_get_modules_for_injection():
    assert_equal(get_modules_for_injection(), [
        'mod_biosig',
        'mod_dipy',
        'mod_mdp',
        'mod_mne',
        'mod_nibabel',
        'mod_nipy',
        'mod_nipype',
        'mod_numpy',
        'mod_pandas',
        'mod_psychopy',
        'mod_scipy',
        'mod_skimage',
        'mod_sklearn'])

def test_cover_our_injections():
    # this one tests only import/syntax/api for the injections
    due = DueCreditCollector()
    inj = DueCreditInjector(collector=due)
    for modname in get_modules_for_injection():
        mod = __import__('duecredit.injections.' + modname, fromlist=["duecredit.injections"])
        mod.inject(inj)

def test_no_harm_from_deactivate():
    # if we have not activated one -- shouldn't blow if we deactivate it
    # TODO: catch warning being spitted out
    DueCreditInjector().deactivate()

def test_injector_del():
    orig__import__ = __builtin__.__import__
    try:
        due = DueCreditCollector()
        inj = DueCreditInjector(collector=due)
        del inj   # delete inactive
        assert_true(__builtin__.__import__ is orig__import__)
        inj = DueCreditInjector(collector=due)
        inj.activate(retrospect=False)
        assert_false(__builtin__.__import__ is orig__import__)
        assert_false(inj._orig_import is None)
        del inj   # delete active but not used
        inj = None
        __builtin__.__import__ = None # We need to do that since otherwise gc will not pick up inj
        gc.collect()  # To cause __del__
        assert_true(__builtin__.__import__ is orig__import__)
        import abc   # and new imports work just fine
    finally:
        __builtin__.__import__ = orig__import__
