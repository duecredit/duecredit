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
import pytest

import builtins as __builtin__
_orig__import__ = __builtin__.__import__

from duecredit.collector import DueCreditCollector
from duecredit.entries import Doi
import duecredit.tests.mod as mod

from ..injections.injector import DueCreditInjector, find_object, get_modules_for_injection
from .. import __version__

try:
    import mvpa2
    _have_mvpa2 = True
except ImportError:
    _have_mvpa2 = False

from logging import getLogger
lgr = getLogger('duecredit.tests.injector')


class TestActiveInjector:
    def setup_method(self):
        lgr.log(5, "Setting up for a TestActiveInjector test")
        self._cleanup_modules()
        self.due = DueCreditCollector()
        self.injector = DueCreditInjector(collector=self.due)
        self.injector.activate(retrospect=False)  # numpy might be already loaded...

    def teardown_method(self):
        lgr.log(5, "Tearing down after a TestActiveInjector test")
        # gc might not pick up inj after some tests complete
        # so we will always deactivate explicitly
        self.injector.deactivate()
        assert __builtin__.__import__ is _orig__import__
        self._cleanup_modules()

    def _cleanup_modules(self):
        if 'duecredit.tests.mod' in sys.modules:
            sys.modules.pop('duecredit.tests.mod')

    def _test_simple_injection(self, func, import_stmt, func_call=None):
        assert 'duecredit.tests.mod' not in sys.modules
        self.injector.add('duecredit.tests.mod', func,
                          Doi('1.2.3.4'),
                          description="Testing %s" % func,
                          min_version='0.1', max_version='1.0',
                          tags=["implementation", "very custom"])
        assert 'duecredit.tests.mod' not in sys.modules  # no import happening
        assert len(self.due._entries) == 0
        assert len(self.due.citations) == 0

        globals_, locals_ = {}, {}
        exec(import_stmt, globals_, locals_)

        assert len(self.due._entries) == 1   # we should get an entry now
        assert len(self.due.citations) == 0  # but not yet a citation

        import duecredit.tests.mod as mod
        _, _, obj = find_object(mod, func)
        assert obj.__duecredited__                # we wrapped
        assert obj.__duecredited__ is not obj     # and it is not pointing to the same func
        assert obj.__doc__ == "custom docstring"  # we preserved docstring

        # TODO: test decoration features -- preserver __doc__ etc
        exec('ret = %s(None, "somevalue")' % (func_call or func), globals_, locals_)
        # TODO: awkwardly 'ret' is not found in the scope while running pytest
        # under python3.4, although present in locals()... WTF?
        assert locals_['ret'] == "%s: None, somevalue" % func
        assert len(self.due._entries) == 1
        assert len(self.due.citations) == 1

        # TODO: there must be a cleaner way to get first value
        citation = list(self.due.citations.values())[0]
        # TODO: ATM we don't allow versioning of the submodules -- we should
        # assert_equal(citation.version, '0.5')
        # ATM it will be the duecredit's version
        assert citation.version == __version__

        assert(citation.tags == ['implementation', 'very custom'])

    def _test_double_injection(self, func, import_stmt, func_call=None):
        assert 'duecredit.tests.mod' not in sys.modules
        # add one injection
        self.injector.add('duecredit.tests.mod', func,
                          Doi('1.2.3.4'),
                          description="Testing %s" % func,
                          min_version='0.1', max_version='1.0',
                          tags=["implementation", "very custom"])
        # add another one
        self.injector.add('duecredit.tests.mod', func,
                          Doi('1.2.3.5'),
                          description="Testing %s" % func,
                          min_version='0.1', max_version='1.0',
                          tags=["implementation", "very custom"])
        assert 'duecredit.tests.mod' not in sys.modules  # no import happening
        assert len(self.due._entries) == 0
        assert len(self.due.citations) == 0

        globals_, locals_ = {}, {}
        exec(import_stmt, globals_, locals_)

        assert len(self.due._entries) == 2  # we should get two entries now
        assert len(self.due.citations) == 0  # but not yet a citation

        import duecredit.tests.mod as mod
        _, _, obj = find_object(mod, func)
        assert obj.__duecredited__  # we wrapped
        assert obj.__duecredited__ is not obj  # and it is not pointing to the same func
        assert obj.__doc__ == "custom docstring"  # we preserved docstring

        # TODO: test decoration features -- preserver __doc__ etc
        exec('ret = %s(None, "somevalue")' % (func_call or func), globals_, locals_)
        # TODO: awkwardly 'ret' is not found in the scope while running pytest
        # under python3.4, although present in locals()... WTF?
        assert locals_['ret'] == "%s: None, somevalue" % func
        assert len(self.due._entries) == 2
        assert len(self.due.citations) == 2

        # TODO: there must be a cleaner way to get first value
        citation = list(self.due.citations.values())[0]
        # TODO: ATM we don't allow versioning of the submodules -- we should
        # assert_equal(citation.version, '0.5')
        # ATM it will be the duecredit's version
        assert citation.version, __version__

        assert (citation.tags == ['implementation', 'very custom'])

    test1 = ('testfunc1', 'from duecredit.tests.mod import testfunc1', None)
    test2 = ("TestClass1.testmeth1", 'from duecredit.tests.mod import TestClass1; c = TestClass1()', 'c.testmeth1')
    test3 = ("TestClass12.Embed.testmeth1", 'from duecredit.tests.mod import TestClass12; c = TestClass12.Embed()',
             'c.testmeth1')

    @pytest.mark.parametrize("func, import_stmt, func_call", [test1, test2, test3])
    def test_simple_injection(self, func, import_stmt, func_call):
        self._test_simple_injection(func, import_stmt, func_call)

    @pytest.mark.parametrize("func, import_stmt, func_call", [test1, test2, test3])
    def test_double_injection(self, func, import_stmt, func_call):
        self._test_double_injection(func, import_stmt, func_call)

    def test_delayed_entries(self):
        # verify that addition of delayed injections happened
        modules_for_injection = get_modules_for_injection()
        assert len(self.injector._delayed_injections) == len(modules_for_injection)
        assert self.injector._entry_records == {}  # but no entries were added
        assert 'scipy' in self.injector._delayed_injections  # We must have it ATM

        try:
            # We do have injections for scipy
            import scipy
        except ImportError as e:
            pytest.skip("scipy was not found: %s" % (e,))

    def test_import_mvpa2_suite(self):
        if not _have_mvpa2:
            pytest.skip("no mvpa2 found")
        # just a smoke test for now
        import mvpa2.suite as mv

    def _test_incorrect_path(self, mod, obj):
        ref = Doi('1.2.3.4')
        # none of them should lead to a failure
        self.injector.add(mod, obj, ref)
        # now cause the import handling -- it must not fail
        # TODO: catch/analyze warnings
        exec('from duecredit.tests.mod import testfunc1', {}, {})

    @pytest.mark.parametrize("mod, obj", [("nonexistingmodule", None),
                                          ("duecredit.tests.mod.nonexistingmodule", None),
                                          ("duecredit.tests.mod", "nonexisting"),
                                          ("duecredit.tests.mod", "nonexisting.whocares")])
    def test_incorrect_path(self, mod, obj):
        self._test_incorrect_path(mod, obj)


def test_find_iobject():
    assert find_object(mod, 'testfunc1') == (mod, 'testfunc1', mod.testfunc1)
    assert find_object(mod, 'TestClass1') == (mod, 'TestClass1', mod.TestClass1)
    assert find_object(mod, 'TestClass1.testmeth1') == (mod.TestClass1, 'testmeth1', mod.TestClass1.testmeth1)
    assert find_object(mod, 'TestClass12.Embed.testmeth1') == (mod.TestClass12.Embed,
                                                               'testmeth1', mod.TestClass12.Embed.testmeth1)


def test_no_double_activation():
    orig__import__ = __builtin__.__import__
    try:
        due = DueCreditCollector()
        injector = DueCreditInjector(collector=due)
        injector.activate()
        assert __builtin__.__import__ is not orig__import__
        duecredited__import__ = __builtin__.__import__
        # TODO: catch/analyze/swallow warning
        injector.activate()
        assert __builtin__.__import__ is duecredited__import__  # we didn't decorate again
    finally:
        injector.deactivate()
        __builtin__.__import__ = orig__import__


def test_get_modules_for_injection():
    # output order is sorted by name (not that it matters for functionality)
    assert get_modules_for_injection() == ['mod_biosig',
                                           'mod_dipy',
                                           'mod_matplotlib',
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
                                           'mod_sklearn',
                                           ]


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
        assert __builtin__.__import__ is orig__import__
        inj = DueCreditInjector(collector=due)
        inj.activate(retrospect=False)
        assert __builtin__.__import__ is not orig__import__
        assert inj._orig_import is not None
        del inj   # delete active but not used
        inj = None
        __builtin__.__import__ = None # We need to do that since otherwise gc will not pick up inj
        gc.collect()  # To cause __del__
        assert __builtin__.__import__ is orig__import__
        import abc   # and new imports work just fine
    finally:
        __builtin__.__import__ = orig__import__


def test_injector_delayed_del():
    # interesting case -- if we still have an instance of injector hanging around
    # and then create a new one, activate it but then finally delete/gc old one
    # it would (currently) reset import back (because atm defined as class var)
    # which would ruin operation of the new injector
    orig__import__ = __builtin__.__import__
    try:
        due = DueCreditCollector()

        inj = DueCreditInjector(collector=due)
        inj.activate(retrospect=False)
        assert __builtin__.__import__ is not orig__import__
        assert inj._orig_import is not None
        inj.deactivate()
        assert __builtin__.__import__ is orig__import__
        assert inj._orig_import is None

        # create 2nd one
        inj2 = DueCreditInjector(collector=due)
        inj2.activate(retrospect=False)
        assert __builtin__.__import__ is not orig__import__
        assert inj2._orig_import is not None
        del inj
        inj = None
        gc.collect()  # To cause __del__
        assert __builtin__.__import__ is not orig__import__  # would fail if del had side-effect
        assert inj2._orig_import is not None
        inj2.deactivate()
        assert __builtin__.__import__ is orig__import__
        import abc   # and new imports work just fine
    finally:
        __builtin__.__import__ = orig__import__
