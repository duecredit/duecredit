from ..collector import DueCreditCollector
from ..entries import BibTeX, DueCreditEntry
from ..io import PickleOutput, import_doi
from nose.tools import assert_equal, assert_is_instance, assert_raises
from six import PY2

import sys
import pickle
import tempfile


def test_import_doi():
    doi_good = '10.1038/nrd842'
    if PY2:
        target_type = unicode
    else:
        target_type = str
    assert_is_instance(import_doi(doi_good), target_type)

    doi_bad = 'fasljfdldaksj'
    assert_raises(ValueError, import_doi, doi_bad)


def test_pickleoutput():
    entry = BibTeX('@article{XXX0, ...}')
    collector = DueCreditCollector()
    collector.add(entry)
    collector.cite(entry)

    with tempfile.NamedTemporaryFile() as fn:
        pickler = PickleOutput(collector, fn=fn.name)
        assert_equal(pickler.fn, fn.name)
        assert_equal(pickler.dump(), None)
        collector_loaded = pickle.load(fn)

        assert_equal(collector.citations.keys(),
                     collector_loaded.citations.keys())
        # TODO: implement comparison of citations
        assert_equal(collector._entries.keys(),
                     collector_loaded._entries.keys())
