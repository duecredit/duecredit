from ..collector import DueCreditCollector
from ..entries import BibTeX, DueCreditEntry
from ..io import PickleOutput, import_doi
from nose.tools import assert_equal, assert_is_instance, assert_raises
from six import PY2

import sys
import pickle
import tempfile
import vcr

@vcr.use_cassette()
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
    #entry = BibTeX('@article{XXX0, ...}')
    entry = BibTeX("@article{Atkins_2002,\n"
                   "title=title,\n"
                   "volume=1, \n"
                   "url=http://dx.doi.org/10.1038/nrd842, \n"
                   "DOI=10.1038/nrd842, \n"
                   "number=7, \n"
                   "journal={Nat. Rev. Drug Disc.}, \n"
                   "publisher={Nature Publishing Group}, \n"
                   "author={Atkins, Joshua H. and Gershell, Leland J.}, \n"
                   "year={2002}, \n"
                   "month={Jul}, \n"
                   "pages={491-492}\n}")
    collector_ = DueCreditCollector()
    collector_.add(entry)
    collector_.cite(entry)

    # test it doesn't puke with an empty collector
    collectors = [collector_, DueCreditCollector()]

    for collector in collectors:
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

