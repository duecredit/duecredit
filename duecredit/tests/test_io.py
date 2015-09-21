# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from ..collector import DueCreditCollector, Citation
from .test_collector import _sample_bibtex, _sample_doi
from ..entries import BibTeX, DueCreditEntry, Doi
from ..io import TextOutput, PickleOutput, import_doi, EnumeratedEntries, get_text_rendering
from nose.tools import assert_equal, assert_is_instance, assert_raises, \
    assert_true, assert_false
from six.moves import StringIO
from six import text_type

from mock import patch

import random
import re
import sys
import pickle
import tempfile
from .test_collector import _sample_bibtex, _sample_bibtex2

try:
    import vcr

    @vcr.use_cassette()
    def test_import_doi():
        doi_good = '10.1038/nrd842'
        assert_is_instance(import_doi(doi_good), text_type)

        doi_bad = 'fasljfdldaksj'
        assert_raises(ValueError, import_doi, doi_bad)

except ImportError:
    # no vcr, and that is in 2015!
    pass


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
    collector_.cite(entry, path='module')

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
    collector.cite(entry, path='module')

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_true("Halchenko, Y.O." in value, msg="value was %s" % value)
    assert_true(value.strip().endswith("Frontiers in Neuroinformatics, 6(22)."))


def test_text_output_dump_formatting():
    due = DueCreditCollector()

    # XXX: atm just to see if it spits out stuff
    @due.dcite(BibTeX(_sample_bibtex), description='solution to life',
               path='mymodule', version='0.0.16')
    def mymodule(arg1, kwarg2="blah"):
        """docstring"""
        assert_equal(arg1, "magical")
        assert_equal(kwarg2, 1)

        @due.dcite(BibTeX(_sample_bibtex2), description='solution to life',
                   path='mymodule:myfunction')
        def myfunction(arg42):
            pass

        myfunction('argh')
        return "load"

    # check we don't have anything output
    strio = StringIO()
    TextOutput(strio, due).dump(tags=['*'])
    value = strio.getvalue()
    assert_true('0 modules cited' in value, msg='value was {0}'.format(value))
    assert_true('0 functions cited' in value,
                msg='value was {0}'.format(value))

    # now we call it -- check it prints stuff
    mymodule('magical', kwarg2=1)
    TextOutput(strio, due).dump(tags=['*'])
    value = strio.getvalue()
    assert_true('1 packages cited' in value, msg='value was {0}'.format(value))
    assert_true('1 functions cited' in value, msg='value was {0}'.format(value))
    assert_true('(v 0.0.16)' in value,
                msg='value was {0}'.format(value))
    assert_equal(len(value.split('\n')), 21, msg='value was {0}'.format(value))

    # test we get the reference numbering right
    samples_bibtex = [_generate_sample_bibtex() for x in range(5)]
    # this sucks but at the moment it's the only way to have multiple
    # references for a function

    @due.dcite(BibTeX(samples_bibtex[0]), description='another solution',
               path='myothermodule', version='0.0.666')
    def myothermodule(arg1, kwarg2="blah"):
        """docstring"""
        assert_equal(arg1, "magical")
        assert_equal(kwarg2, 1)

        @due.dcite(BibTeX(samples_bibtex[1]), description='solution to life',
                   path='myothermodule:myotherfunction')
        @due.dcite(BibTeX(samples_bibtex[2]), description='solution to life',
                   path='myothermodule:myotherfunction')
        @due.dcite(BibTeX(samples_bibtex[3]), description='solution to life',
                   path='myothermodule:myotherfunction')
        @due.dcite(BibTeX(samples_bibtex[4]), description='solution to life',
                   path='myothermodule:myotherfunction')
        @due.dcite(BibTeX(_sample_bibtex2), description='solution to life',
                   path='myothermodule:myotherfunction')
        def myotherfunction(arg42):
            pass

        myotherfunction('argh')
        return "load"

    myothermodule('magical', kwarg2=1)
    strio = StringIO()
    TextOutput(strio, due).dump(tags=['*'])
    value = strio.getvalue()
    lines = value.split('\n')

    citation_numbers = []
    reference_numbers = []
    references = []
    for line in lines:
        match_citation = re.search('\[([0-9, ]+)\]$', line)
        match_reference = re.search('^\[([0-9])\]', line)
        if match_citation:
            citation_numbers.extend(match_citation.group(1).split(', '))
        elif match_reference:
            reference_numbers.append(match_reference.group(1))
            references.append(line.replace(match_reference.group(), ""))

    assert_equal(set(citation_numbers), set(reference_numbers))
    assert_equal(len(set(references)), len(set(citation_numbers)))
    assert_equal(len(citation_numbers), 8)
    # verify that we have returned to previous state of filters
    import warnings
    assert_true(('ignore', None, UserWarning, None, 0) not in warnings.filters)

def _generate_sample_bibtex():
    """
    Generate a random sample bibtex to test multiple references
    """
    letters = 'abcdefghilmnopqrstuvxz'
    numbers = '0123456789'
    letters_numbers = letters + letters.upper() + numbers
    letters_numbers_spaces = letters_numbers + ' '

    key = "".join(random.sample(letters_numbers, 7))
    title = "".join(random.sample(letters_numbers_spaces, 20))
    journal = "".join(random.sample(letters_numbers_spaces, 20))
    publisher = "".join(random.sample(letters_numbers_spaces, 10))
    author = "".join(random.sample(letters, 6)) + ', ' + \
             "".join(random.sample(letters, 4))
    year = "".join(random.sample(numbers, 4))

    elements = [('title', title), ('journal', journal),
                ('publisher', publisher), ('author', author),
                ('year', year)]

    sample_bibtex = "@ARTICLE{%s,\n" % key
    for string, value in elements:
        sample_bibtex += "%s={%s},\n" % (string, value)
    sample_bibtex += "}"
    return sample_bibtex

def test_enumeratedentries():
    enumentries = EnumeratedEntries()
    assert_false(enumentries)

    # add some entries
    entries = [('ciao', 1), ('miao', 2), ('bau', 3)]
    for entry, _ in entries:
        enumentries.add(entry)

    assert_equal(len(enumentries), 3)

    for entry, nr in entries:
        assert_equal(nr, enumentries[entry])
        assert_equal(entry, enumentries.fromrefnr(nr))

    assert_raises(KeyError, enumentries.__getitem__, 'boh')
    assert_raises(KeyError, enumentries.fromrefnr, 666)

    assert_equal(entries, sorted(enumentries, key=lambda x: x[1]))

@patch('duecredit.io.get_bibtex_rendering')
@patch('duecredit.io.format_bibtex')
def test_get_text_rendering(mock_format_bibtex, mock_get_bibtex_rendering):
    # mock get_bibtex_rendering to return the same bibtex entry
    sample_bibtex = BibTeX(_sample_bibtex)
    mock_get_bibtex_rendering.return_value = sample_bibtex

    # test if bibtex type is passed
    citation_bibtex = Citation(sample_bibtex, path='mypath')
    bibtex_output = get_text_rendering(citation_bibtex)
    mock_format_bibtex.assert_called_with(citation_bibtex.entry, style='harvard1')
    mock_format_bibtex.reset_mock()

    # test if doi type is passed
    citation_doi = Citation(Doi(_sample_doi), path='mypath')
    doi_output = get_text_rendering(citation_doi)
    mock_format_bibtex.assert_called_with(citation_bibtex.entry, style='harvard1')

    assert_equal(bibtex_output, doi_output)
