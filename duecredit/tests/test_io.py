from ..collector import DueCreditCollector
from ..entries import BibTeX, DueCreditEntry
from ..io import PickleOutput
from nose.tools import assert_equal

import pickle
import tempfile

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
