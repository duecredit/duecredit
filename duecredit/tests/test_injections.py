# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import sys

from duecredit.collector import DueCreditCollector, InactiveDueCreditCollector
from duecredit.entries import BibTeX, Doi

from six import viewvalues
from ..injections import DueCreditInjector, find_object

from nose.tools import assert_equal
from nose.tools import assert_false

class TestActiveInjector(object):
    def setup(self):
        self._cleanup_modules()
        self.due = DueCreditCollector()
        self.injector = DueCreditInjector(collector=self.due)
        self.injector.activate()

    def teardown(self):
        self.injector.deactivate()
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

        # TODO: test decoration features -- preserver __doc__ etc
        exec('ret = %s(None, "somevalue")' % (func_call or func))
        # XXX: awkwardly 'ret' is not found in the scope while running nosetests
        # under python3.4, although present in locals()... WTF?
        assert_equal(locals()['ret'], "%s: None, somevalue" % func)
        assert_equal(len(self.due._entries), 1)
        assert_equal(len(self.due.citations), 1)

        # TODO: there must be a cleaner way to get first value
        citation = list(viewvalues(self.due.citations))[0]
        assert(citation.tags == ['implementation', 'very custom'])

    def test_simple_injection(self):
        yield self._test_simple_injection, "testfunc1", 'from duecredit.tests.mod import testfunc1'
        yield self._test_simple_injection, "TestClass1.testmeth1", \
              'from duecredit.tests.mod import TestClass1; c = TestClass1()', 'c.testmeth1'
        yield self._test_simple_injection, "TestClass12.Embed.testmeth1", \
              'from duecredit.tests.mod import TestClass12; c = TestClass12.Embed()', 'c.testmeth1'


def _test_find_object(mod, path, parent, obj_name, obj):
    assert_equal(find_object(mod, path), (parent, obj_name, obj))


def test_find_object():
    import duecredit.tests.mod as mod
    yield _test_find_object, mod, 'testfunc1', mod, 'testfunc1', mod.testfunc1
    yield _test_find_object, mod, 'TestClass1', mod, 'TestClass1', mod.TestClass1
    yield _test_find_object, mod, 'TestClass1.testmeth1', mod.TestClass1, 'testmeth1', mod.TestClass1.testmeth1
    yield _test_find_object, mod, 'TestClass12.Embed.testmeth1', \
          mod.TestClass12.Embed, 'testmeth1', mod.TestClass12.Embed.testmeth1
