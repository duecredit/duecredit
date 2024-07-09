# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import random
import re
import pickle
import os

from .test_collector import _sample_bibtex, _sample_bibtex2
from six.moves import StringIO
from six import text_type

from mock import patch

from ..collector import DueCreditCollector, Citation
from .test_collector import _sample_bibtex, _sample_doi
from ..entries import BibTeX, DueCreditEntry, Doi
from ..io import TextOutput, PickleOutput, import_doi, \
    get_text_rendering, format_bibtex, _is_contained, Output, BibTeXOutput
from ..utils import with_tempfile

from nose.tools import assert_equal, assert_is_instance, assert_raises, \
    assert_true, assert_false

try:
    import vcr

    @vcr.use_cassette()
    def test_import_doi():
        doi_good = '10.1038/nrd842'
        kw = dict(sleep=0.00001, retries=2)
        assert_is_instance(import_doi(doi_good, **kw), text_type)

        doi_bad = 'fasljfdldaksj'
        assert_raises(ValueError, import_doi, doi_bad, **kw)

        doi_zenodo = '10.5281/zenodo.50186'
        assert_is_instance(import_doi(doi_zenodo, **kw), text_type)

except ImportError:
    # no vcr, and that is in 2015!
    pass


@with_tempfile
def test_pickleoutput(fn):
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
                   "pages={491--492}\n}")
    collector_ = DueCreditCollector()
    collector_.add(entry)
    collector_.cite(entry, path='module')

    # test it doesn't puke with an empty collector
    collectors = [collector_, DueCreditCollector()]

    for collector in collectors:
        pickler = PickleOutput(collector, fn=fn)
        assert_equal(pickler.fn, fn)
        assert_equal(pickler.dump(), None)

        with open(fn, 'rb') as f:
            collector_loaded = pickle.load(f)

        assert_equal(collector.citations.keys(),
                     collector_loaded.citations.keys())
        # TODO: implement comparison of citations
        assert_equal(collector._entries.keys(),
                     collector_loaded._entries.keys())
        os.unlink(fn)


def test_output():
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # normal use
    collector = DueCreditCollector()
    collector.cite(entry, path='package')
    collector.cite(entry, path='package.module')

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['*'])

    assert_equal(len(packages), 1)
    assert_equal(len(modules), 1)
    assert_equal(len(objects), 0)

    assert_equal(packages['package'][0],
                 collector.citations[('package', entry.get_key())])
    assert_equal(modules['package.module'][0],
                 collector.citations[('package.module', entry.get_key())])

    # no toppackage
    collector = DueCreditCollector()
    collector.cite(entry, path='package')
    collector.cite(entry, path='package2.module')

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['*'])

    assert_equal(len(packages), 0)
    assert_equal(len(modules), 1)
    assert_equal(len(objects), 0)

    assert_equal(modules['package2.module'][0],
                 collector.citations[('package2.module', entry.get_key())])


    # toppackage because required
    collector = DueCreditCollector()
    collector.cite(entry, path='package', cite_module=True)
    collector.cite(entry, path='package2.module')

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['*'])

    assert_equal(len(packages), 1)
    assert_equal(len(modules), 1)
    assert_equal(len(objects), 0)

    assert_equal(packages['package'][0],
                 collector.citations[('package', entry.get_key())])
    assert_equal(modules['package2.module'][0],
                 collector.citations[('package2.module', entry.get_key())])


    # check it returns multiple entries
    collector = DueCreditCollector()
    collector.cite(entry, path='package')
    collector.cite(entry2, path='package')
    collector.cite(entry, path='package.module')

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['*'])

    assert_equal(len(packages), 1)
    assert_equal(len(packages['package']), 2)
    assert_equal(len(modules), 1)
    assert_equal(len(objects), 0)

    # sort them in order so we know who is who
    # entry2 key is Atk...
    # entry key is XX..
    packs = sorted(packages['package'], key=lambda x: x.entry.key)

    assert_equal(packs[0],
                 collector.citations[('package', entry2.get_key())])
    assert_equal(packs[1],
                 collector.citations[('package', entry.get_key())])
    assert_equal(modules['package.module'][0],
                 collector.citations[('package.module', entry.get_key())])


    # check that filtering works
    collector = DueCreditCollector()
    collector.cite(entry, path='package', tags=['edu'])
    collector.cite(entry2, path='package')
    collector.cite(entry, path='package.module', tags=['edu'])

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['edu'])

    assert_equal(len(packages), 1)
    assert_equal(len(packages['package']), 1)
    assert_equal(len(modules), 1)
    assert_equal(len(objects), 0)

    assert_equal(packages['package'][0],
                 collector.citations[('package', entry.get_key())])
    assert_equal(modules['package.module'][0],
                 collector.citations[('package.module', entry.get_key())])


def test_output_return_all():
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # normal use
    collector = DueCreditCollector()
    collector.cite(entry, path='package')
    collector.cite(entry2, path='package2')

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['*'])
    assert_false(packages)
    assert_false(modules)
    assert_false(objects)

    for flag in ['1', 'True', 'TRUE', 'true', 'on', 'yes']:
        with patch.dict(os.environ, {'DUECREDIT_REPORT_ALL': flag}):
            # if _all is None then get the environment
            packages, modules, objects = output._get_collated_citations(tags=['*'])
            assert_equal(len(packages), 2)
            assert_false(modules)
            assert_false(objects)
            # however if _all is set it shouldn't work
            packages, modules, objects = output._get_collated_citations(tags=['*'], all_=False)
            assert_false(packages)
            assert_false(modules)
            assert_false(objects)


def test_output_tags():
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # normal use
    collector = DueCreditCollector()
    collector.cite(entry, path='package', cite_module=True, tags=['edu'])
    collector.cite(entry2, path='package.module', tags=['wip'])

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=['*'])
    assert_true(len(packages) == 1)
    assert_true(len(modules) == 1)
    assert_false(objects)

    packages, modules, objects = output._get_collated_citations()
    assert_false(packages)
    assert_false(modules)
    assert_false(objects)

    for tags in ['edu', 'wip', 'edu,wip']:
        with patch.dict(os.environ, {'DUECREDIT_REPORT_TAGS': tags}):
            # if tags is None then get the environment
            packages, modules, objects = output._get_collated_citations()
            assert_true(len(packages) == (1 if 'edu' in tags else 0))
            assert_true(len(modules) == (1 if 'wip' in tags else 0))
            assert_false(objects)
            # however if tags is set it shouldn't work
            packages, modules, objects = output._get_collated_citations(tags=['implementation'])
            assert_false(packages)
            assert_false(modules)
            assert_false(objects)


def test_text_output():
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # in this case, since we're not citing any module or method, we shouldn't
    # output anything
    collector = DueCreditCollector()
    collector.cite(entry, path='package')

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_true("0 packages cited" in value, msg="value was %s" % value)
    assert_true("0 modules cited" in value, msg="value was %s" % value)
    assert_true("0 functions cited" in value, msg="value was %s" % value)

    # but it should be cited if cite_module=True
    collector = DueCreditCollector()
    collector.cite(entry, path='package', cite_module=True)

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_true("1 package cited" in value, msg="value was %s" % value)
    assert_true("0 modules cited" in value, msg="value was %s" % value)
    assert_true("0 functions cited" in value, msg="value was %s" % value)

    # in this case, we should be citing the package since we are also citing a
    # submodule
    collector = DueCreditCollector()
    collector.cite(entry, path='package')
    collector.cite(entry, path='package.module')

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_true("1 package cited" in value, msg="value was %s" % value)
    assert_true("1 module cited" in value, msg="value was %s" % value)
    assert_true("0 functions cited" in value, msg="value was %s" % value)
    assert_true("Halchenko, Y.O." in value, msg="value was %s" % value)
    assert_true(value.strip().endswith("Frontiers in Neuroinformatics, 6(22)."))


    # in this case, we should be citing the package since we are also citing a
    # submodule
    collector = DueCreditCollector()
    collector.cite(entry, path='package')
    collector.cite(entry2, path='package')
    collector.cite(entry, path='package.module')

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_true("1 package cited" in value, msg="value was %s" % value)
    assert_true("1 module cited" in value, msg="value was %s" % value)
    assert_true("0 functions cited" in value, msg="value was %s" % value)
    assert_true("Halchenko, Y.O." in value, msg="value was %s" % value)
    assert_true('[1, 2]' in value, msg="value was %s" %value)
    assert_false('[3]' in value, msg="value was %s" %value)


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
    strio = StringIO()
    mymodule('magical', kwarg2=1)
    TextOutput(strio, due).dump(tags=['*'])
    value = strio.getvalue()
    assert_true('1 package cited' in value, msg='value was {0}'.format(value))
    assert_true('1 function cited' in value, msg='value was {0}'.format(value))
    assert_true('(v 0.0.16)' in value,
                msg='value was {0}'.format(value))
    assert_equal(len(value.split('\n')), 16, msg='value was {0}'.format(len(value.split('\n'))))

    # test we get the reference numbering right
    samples_bibtex = [_generate_sample_bibtex() for x in range(6)]
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
        @due.dcite(BibTeX(samples_bibtex[5]), description='solution to life',
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


def test_bibtex_output():
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # in this case, since we're not citing any module or method, we shouldn't
    # output anything
    collector = DueCreditCollector()
    collector.cite(entry, path='package')

    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_equal(value, '', msg='Value was {0}'.format(value))

    # impose citing
    collector = DueCreditCollector()
    collector.cite(entry, path='package', cite_module=True)

    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_equal(value.strip(), _sample_bibtex.strip(), msg='Value was {0}'.format(value))

    # impose filtering
    collector = DueCreditCollector()
    collector.cite(entry, path='package', cite_module=True, tags=['edu'])
    collector.cite(entry2, path='package.module')

    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=['edu'])
    value = strio.getvalue()
    assert_equal(value.strip(), _sample_bibtex.strip(), msg='Value was {0}'.format(value))

    # no filtering
    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    assert_equal(value.strip(),
                 _sample_bibtex.strip() + _sample_bibtex2.rstrip(),
                 msg='Value was {0}'.format(value))

    # check the we output only unique bibtex entries
    collector.cite(entry2, path='package')
    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=['*'])
    value = strio.getvalue()
    value_ = sorted(value.strip().split('\n'))
    bibtex = sorted((_sample_bibtex.strip() + _sample_bibtex2.rstrip()).split('\n'))
    assert_equal(value_, bibtex,
                 msg='Value was {0}'.format(value_, bibtex))


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


def test_format_bibtex_zenodo_doi():
    """
    test that we can correctly parse bibtex entries obtained from a zenodo doi
    """
    # this was fetched on 2016-05-10
    bibtex_zenodo = """
    @data{0b1284ba-5ce5-4367-84f3-c44b4962ad90,
    doi = {10.5281/zenodo.50186},
    url = {http://dx.doi.org/10.5281/zenodo.50186},
    author = {Satrajit Ghosh; Chris Filo Gorgolewski; Oscar Esteban;
    Erik Ziegler; David Ellis; cindeem; Michael Waskom; Dav Clark; Michael;
    Fred Loney; Alexandre M. S.; Michael Notter; Hans Johnson;
    Anisha Keshavan; Yaroslav Halchenko; Carlo Hamalainen; Blake Dewey;
    Ben Cipollini; Daniel Clark; Julia Huntenburg; Drew Erickson;
    Michael Hanke; moloney; Jason W; Demian Wassermann; cdla;
    Nolan Nichols; Chris Markiewicz; Jarrod Millman; Arman Eshaghi; },
    publisher = {Zenodo},
    title = {nipype: Release candidate 1 for version 0.12.0},
    year = {2016}
    }
    """
    assert_equal(format_bibtex(BibTeX(bibtex_zenodo)),
                 """Ghosh, S. et al., 2016. nipype: Release candidate 1 for version 0.12.0.""")

def test_is_contained():
    toppath = 'package'
    assert_true(_is_contained(toppath, 'package.module'))
    assert_true(_is_contained(toppath, 'package.module.submodule'))
    assert_true(_is_contained(toppath, 'package.module.submodule:object'))
    assert_true(_is_contained(toppath, 'package:object'))
    assert_true(_is_contained(toppath, toppath))
    assert_false(_is_contained(toppath, 'package2'))
    assert_false(_is_contained(toppath, 'package2:anotherobject'))
    assert_false(_is_contained(toppath, 'package2.module:anotherobject'))
