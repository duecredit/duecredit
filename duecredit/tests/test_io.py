from ..collector import DueCreditCollector
from ..entries import BibTeX, DueCreditEntry
from ..io import TextOutput, PickleOutput, import_doi
from nose.tools import assert_equal, assert_is_instance, assert_raises, \
    assert_true
from six import PY2

import sys
import pickle
import tempfile
from .test_collector import _sample_bibtex, _sample_bibtex2
import vcr

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO

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

def test_text_output():
    entry = BibTeX(_sample_bibtex)
    collector = DueCreditCollector()
    collector.cite(entry)

    strio = StringIO()
    TextOutput(strio, collector).dump()
    value = strio.getvalue()
    assert_true("Halchenko, Y.O." in value, msg="value was %s" % value)
    assert_true(value.strip().endswith("Frontiers in Neuroinformatics, 6(22)."))


def test_text_output_dump_formatting():
    due = DueCreditCollector()

    # XXX: atm just to see if it spits out stuff
    @due.dcite(BibTeX(_sample_bibtex), use='solution to life',
               path='mymodule', version='0.0.16')
    def mymodule(arg1, kwarg2="blah"):
        """docstring"""
        assert_equal(arg1, "magical")
        assert_equal(kwarg2, 1)

        @due.dcite(BibTeX(_sample_bibtex2), use='solution to life',
                   path='mymodule:myfunction')
        def myfunction(arg42):
            pass

        myfunction('argh')
        return "load"

    # check we don't have anything output
    strio = StringIO()
    TextOutput(strio, due).dump()
    value = strio.getvalue()
    assert_true('0 modules cited' in value, msg='value was {0}'.format(value))
    assert_true('0 functions cited' in value,
                msg='value was {0}'.format(value))

    # now we call it -- check it prints stuff
    mymodule('magical', kwarg2=1)
    TextOutput(strio, due).dump()
    value = strio.getvalue()
    assert_true('1 modules cited' in value, msg='value was {0}'.format(value))
    assert_true('1 functions cited' in value,
                msg='value was {0}'.format(value))
    assert_true('(v 0.0.16)' in value,
                msg='value was {0}'.format(value))
    assert_equal(len(value.split('\n')), 17, msg='value was {0}'.format(value))

    # verify that we have returned to previous state of filters
    import warnings
    assert_true(('ignore', None, UserWarning, None, 0) not in warnings.filters)
