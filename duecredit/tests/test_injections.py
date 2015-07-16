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

from ..injections import DueCreditInjector

from nose.tools import assert_equal

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

    def test_simple_injection(self):
        self.injector.add('duecredit.tests.mod', 'testfunc1',
                          Doi('1.2.3.4'),
                          description="Testing testfunc1",
                          min_version='0.1', max_version='1.0',
                          tags=["implementation", "very custom"])
        assert_equal(len(self.due._entries), 0)
        assert_equal(len(self.due.citations), 0)

        from duecredit.tests.mod import testfunc1

        assert_equal(len(self.due._entries), 1)   # we should get an entry now
        assert_equal(len(self.due.citations), 0)  # but not yet a citation

        # TODO: test decoration features -- preserver __doc__ etc
        testfunc1(None, "somevalue")
        assert_equal(len(self.due._entries), 1)
        assert_equal(len(self.due.citations), 1)




