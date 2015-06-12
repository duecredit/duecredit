from ..collector import DueCreditCollector

from nose.tools import assert_equal

def _test_entry(due, entry):
    due.add(entry)


def test_entry():
    entry = ('thisismykey', 'thisismyreference')
    yield _test_entry, DueCreditCollector(), entry

    entries = [('thisismykey', 'thisismyreference'),
               ('thisisanothermykey', 'thisismyreference'),
               ('thisismykey', 'thisismyreference')]
    yield _test_entry, DueCreditCollector(), entries


def test_dcite_function():
    # Test basic wrapping that we don't mask out the arguments
    # TODO: create a decorator to sweep both active and inactive one
    due = DueCreditCollector()

    @due.dcite("XXX0")
    def method(arg1, kwarg2="blah"):
        assert_equal(arg1, "magical")
        assert_equal(kwarg2, 1)

    method("magical", 1)


def test_dcite_method():
    # Test basic wrapping that we don't mask out the arguments
    # TODO: create a decorator to sweep both active and inactive one
    due = DueCreditCollector()

    class SomeClass(object):
        @due.dcite("XXX0")
        def method(self, arg1, kwarg2="blah"):
            assert_equal(arg1, "magical")
            assert_equal(kwarg2, 1)

    instance = SomeClass()
    instance.method("magical", 1)