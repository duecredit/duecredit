from ..collector import DueCreditCollector, InactiveDueCreditCollector, \
    CollectorGrave
from ..entries import BibTeX, Doi
from ..export import TextOutput, PickleOutput

from mock import patch
from nose.tools import assert_equal, assert_is_instance, assert_raises
import os
import tempfile

def _test_entry(due, entry):
    due.add(entry)

_sample_bibtex = "@article{XXX0, ...}"
_sample_doi = "a.b.c/1.2.3"

def test_entry():
    entry = BibTeX(_sample_bibtex)
    yield _test_entry, DueCreditCollector(), entry

    entries = [BibTeX(_sample_bibtex), BibTeX(_sample_bibtex),
               Doi(_sample_doi)]
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
            citation = due.citations["XXX0"]
            assert_equal(citation.count, 1)
            assert_equal(citation.level, "func duecredit.tests."
                                         "test_collector.method")

        instance = SomeClass()
        yield _test_dcite_basic, due, instance.method

        if active:
            assert_equal(len(due.citations), 1)
            assert_equal(len(due._entries), 1)
            assert_equal(citation.count, 2)
            # TODO: we should actually get level/counts pairs so here
            # it is already a different level


def test_get_output_handler_method():
    with patch.dict(os.environ, {'DUECREDIT_OUTPUTS': 'stdout, pickle'}):
        entry = BibTeX('@article{XXX0, ...}')
        collector = DueCreditCollector()
        collector.add(entry)
        collector.cite(entry)

        with tempfile.NamedTemporaryFile() as f:
            grave = CollectorGrave(collector, fn=f.name)
            handlers = [grave._get_output_handler(type_, collector)
                        for type_ in ['stdout', 'pickle']]

            assert_is_instance(handlers[0], TextOutput)
            assert_is_instance(handlers[1], PickleOutput)

            assert_raises(NotImplementedError, grave._get_output_handler,
                          'nothing', collector)


def test_collectors_uniform_API():
    get_api = lambda obj: [x for x in sorted(dir(obj))
                           if not x.startswith('_')
                              or x in ('__call__')]
    assert_equal(get_api(DueCreditCollector), get_api(InactiveDueCreditCollector))