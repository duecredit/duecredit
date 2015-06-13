from ..collector import DueCreditCollector, InactiveDueCreditCollector
from ..entries import BibTeX, Doi

from nose.tools import assert_equal

def _test_entry(due, entry):
    due.add(entry)

_sample_bibtex = "@article{XXX0, ...}"
_sample_doi = "a.b.c/1.2.3"

def test_entry():
    entry = BibTeX(_sample_bibtex)
    yield _test_entry, DueCreditCollector(), entry

    entries = [BibTeX(_sample_bibtex), BibTeX(_sample_bibtex), Doi(_sample_doi)]
    yield _test_entry, DueCreditCollector(), entries


def _test_dcite_basic(due, callable):

    assert_equal(callable("magical", 1), "load")
    # verify that @wraps correctly passes all the docstrings etc
    assert_equal(callable.__name__, "method")
    assert_equal(callable.__doc__, "docstring")



def test_dcite_method():

    # Test basic wrapping that we don't mask out the arguments
    for due in [DueCreditCollector(), InactiveDueCreditCollector()]:
        active = isinstance(due, DueCreditCollector)
        due.add(BibTeX(_sample_bibtex))

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
        if active:
            assert_equal(due.citations, {})
            assert_equal(len(due._entries), 1)

        yield _test_dcite_basic, due, method

        if active:
            assert_equal(len(due.citations), 1)
            assert_equal(len(due._entries), 1)
            assert_equal(due.citations["XXX0"].count, 1)

        instance = SomeClass()
        yield _test_dcite_basic, due, instance.method

        if active:
            assert_equal(len(due.citations), 1)
            assert_equal(len(due._entries), 1)
            assert_equal(due.citations["XXX0"].count, 2)

