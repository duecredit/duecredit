from ..collector import DueCreditCollector, InactiveDueCreditCollector
from ..entries import BibTeX, Doi

from nose.tools import assert_equal

def _test_entry(due, entry):
    due.add(entry)


def test_entry():
    entry = BibTeX("myentry")
    yield _test_entry, DueCreditCollector(), entry

    entries = [BibTeX("myentry"), BibTeX("myentry"), Doi("myentry")]
    yield _test_entry, DueCreditCollector(), entries


def _test_dcite_basic(due, callable):

    assert_equal(callable("magical", 1), "load")
    # verify that @wraps correctly passes all the docstrings etc
    assert_equal(callable.__name__, "method")
    assert_equal(callable.__doc__, "docstring")



def test_dcite_method():
    # Test basic wrapping that we don't mask out the arguments
    for due in [DueCreditCollector(), InactiveDueCreditCollector()]:

        @due.dcite("XXX0")
        def method(arg1, kwarg2="blah"):
            """docstring"""
            assert_equal(arg1, "magical")
            assert_equal(kwarg2, 1)
            return "load"

        class SomeClass(object):
            @due.dcite("XXX0")
            def method(self, arg1, kwarg2="blah"):
                """docstring"""
                assert_equal(arg1, "magical")
                assert_equal(kwarg2, 1)
                return "load"

        yield _test_dcite_basic, due, method

        instance = SomeClass()
        yield _test_dcite_basic, due, instance.method

