# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from citeproc.source.bibtex import BibTeX as cpBibTeX
import citeproc as cp
import time
from collections import defaultdict, Iterator
import copy
import os
from os.path import dirname, exists
import pickle
import requests
import tempfile
from six import PY2, itervalues, iteritems
import warnings

from .config import CACHE_DIR, DUECREDIT_FILE
from .entries import BibTeX, Doi
from .log import lgr

def get_doi_cache_file(doi):
    return os.path.join(CACHE_DIR, doi)


def import_doi(doi):
    cached = get_doi_cache_file(doi)

    if exists(cached):
        with open(cached) as f:
            doi = f.read()
            if PY2:
                return doi.decode('utf-8')
            return doi

    # else -- fetch it
    headers = {'Accept': 'text/bibliography; style=bibtex'}
    url = 'http://dx.doi.org/' + doi
    retries = 10
    while retries > 0:
        r = requests.get(url, headers=headers)
        r.encoding = 'UTF-8'
        bibtex = r.text.strip()
        if bibtex.startswith('@'):
            # no more retries necessary
            break
        lgr.warning("Failed to obtain bibtex from doi.org, retrying...")
        time.sleep(0.5)  # give some time to the server
        retries -= 1
    status_code = r.status_code
    if not bibtex.startswith('@'):
        raise ValueError('Query %(url)s for BibTeX for a DOI %(doi)s (wrong doi?) has failed. '
                         'Response code %(status_code)d. '
                         #'BibTeX response was: %(bibtex)s'
                         % locals())
    if not exists(cached):
        cache_dir = dirname(cached)
        if not exists(cache_dir):
            os.makedirs(cache_dir)
        with open(cached, 'w') as f:
            if PY2:
                f.write(bibtex.encode('utf-8'))
            else:
                f.write(bibtex)
    return bibtex


class EnumeratedEntries(Iterator):
    """A container of entries enumerated referenced by their entry_key"""
    def __init__(self):
        self._keys2refnr = {}
        self._refnr2keys = {}
        self._refnr = 1

    def add(self, entry_key):
        """Add entry_key and update refnr"""
        if entry_key not in self._keys2refnr:
            self._keys2refnr[entry_key] = self._refnr
            self._refnr2keys[self._refnr] = entry_key
            self._refnr += 1

    def __getitem__(self, item):
        if item not in self._keys2refnr:
            raise KeyError('{0} not present'.format(item))
        return self._keys2refnr[item]

    def fromrefnr(self, refnr):
        if refnr not in self._refnr2keys:
            raise KeyError('{0} not present'.format(refnr))
        return self._refnr2keys[refnr]

    def __iter__(self):
        return iteritems(self._keys2refnr)

    # Python 3
    def __next__(self):
        return self.next()

    def next(self):
        yield next(self.__iter__())

    def __len__(self):
        return len(self._keys2refnr)


class TextOutput(object):  # TODO some parent class to do what...?
    def __init__(self, fd, collector, style=None):
        self.fd = fd
        self.collector = collector
        # TODO: check that CLS style actually exists
        self.style = style
        if 'DUECREDIT_STYLE' in os.environ.keys():
            self.style = os.environ['DUECREDIT_STYLE']
        else:
            self.style = 'harvard1'

    # TODO: refactor name to sth more intuitive
    def _model_citations(self, tags=None):
        if not tags:
            tags = os.environ.get('DUECREDIT_REPORT_TAGS', 'reference-implementation,implementation').split(',')
        tags = set(tags)

        citations = self.collector.citations
        if tags != {'*'}:
            # Filter out citations
            citations = dict((k, c)
                             for k, c in iteritems(citations)
                             if tags.intersection(c.tags))

        packages = {}
        modules = {}
        objects = {}

        for key in ('citations', 'entry_keys'):
            packages[key] = defaultdict(list)
            modules[key] = defaultdict(list)
            objects[key] = defaultdict(list)

        # for each path store both a list of entry keys and of citations
        for (path, entry_key), citation in iteritems(citations):
            if ':' in path:
                target_dict = objects
            elif '.' in path:
                target_dict = modules
            else:
                target_dict = packages
            target_dict['citations'][path].append(citation)
            target_dict['entry_keys'][path].append(entry_key)
        return packages, modules, objects

    def dump(self, tags=None):
        # get 'model' of citations
        packages, modules, objects = self._model_citations(tags)
        # mapping key -> refnr
        enum_entries = EnumeratedEntries()

        citations_ordered = []
        # set up view

        # package level
        sublevels = [modules, objects]
        for package in sorted(packages['entry_keys']):
            for entry_key in packages['entry_keys'][package]:
                enum_entries.add(entry_key)
            citations_ordered.append(package)
            # sublevels
            for sublevel in sublevels:
                for obj in sorted(filter(lambda x: package in x, sublevel['entry_keys'])):
                    for entry_key_obj in sublevel['entry_keys'][obj]:
                        enum_entries.add(entry_key_obj)
                    citations_ordered.append(obj)

        # Now we can "render" different views of our "model"
        # Here for now just text BUT that is where we can "split" the logic and provide
        # different renderings given the model -- text, rest, md, tex+latex, whatever
        self.fd.write('\nDueCredit Report:\n')

        for path in citations_ordered:
            if ':' in path:
                self.fd.write('  ')
                target_dict = objects
            elif '.' in path:
                self.fd.write('  ')
                target_dict = modules
            else:
                target_dict = packages
            # TODO: absorb common logic into a common function
            citations = target_dict['citations'][path]
            entry_keys = target_dict['entry_keys'][path]
            descriptions = sorted(map(str, set(str(r.description) for r in citations)))
            versions = sorted(map(str, set(str(r.version) for r in citations)))
            refnrs = sorted([str(enum_entries[entry_key]) for entry_key in entry_keys])
            self.fd.write('- {0} / {1} (v {2}) [{3}]\n'.format(
                ", ".join(descriptions), path, ', '.join(versions), ', '.join(refnrs)))

        # Print out some stats
        obj_names = ('packages', 'modules', 'functions')
        n_citations = map(len, (packages['citations'], modules['citations'], objects['citations']))
        for citation_type, n in zip(obj_names, n_citations):
            self.fd.write('\n{0} {1} cited'.format(n, citation_type))

        if enum_entries:
            citations_fromentrykey = self.collector._citations_fromentrykey()
            self.fd.write('\n\nReferences\n' + '-' * 10 + '\n')
            # collect all the entries used
            refnr_key = [(nr, enum_entries.fromrefnr(nr)) for nr in range(1, len(enum_entries)+1)]
            for nr, key in refnr_key:
                self.fd.write('\n[{0}] '.format(nr))
                self.fd.write(get_text_rendering(citations_fromentrykey[key], style=self.style))
            self.fd.write('\n')

def get_text_rendering(citation, style='harvard1'):
    from .collector import Citation
    entry = citation.entry
    if isinstance(entry, Doi):
        bibtex_rendering = get_bibtex_rendering(entry)
        bibtex_citation = copy.copy(citation)
        bibtex_citation.set_entry(bibtex_rendering)
        return get_text_rendering(bibtex_citation)
    elif isinstance(entry, BibTeX):
        return format_bibtex(entry, style=style)
    else:
        return str(entry)


def get_bibtex_rendering(entry):
    if isinstance(entry, Doi):
        return BibTeX(import_doi(entry.doi))
    elif isinstance(entry, BibTeX):
        return entry
    else:
        raise ValueError("Have no clue how to get bibtex out of %s" % entry)


def format_bibtex(bibtex_entry, style='harvard1'):
    key = bibtex_entry.get_key()
    # need to save it temporarily to use citeproc-py
    fname = tempfile.mktemp(suffix='.bib')
    try:
        with open(fname, 'wt') as f:
            bibtex = bibtex_entry.rawentry
            bibtex = bibtex.replace(u'\u2013', '--') + "\n"
            # TODO: manage to save/use UTF-8
            if PY2:
                bibtex = bibtex.encode('ascii', 'ignore')
            f.write(bibtex)
        # We need to avoid cpBibTex spitting out warnings
        old_filters = warnings.filters[:]  # store a copy of filters
        warnings.simplefilter('ignore', UserWarning)
        try:
            bib_source = cpBibTeX(fname)
        except Exception as e:
            lgr.error("Failed to process BibTeX file %s" % fname)
            return "ERRORED: %s" % str(e)
        finally:
            # return warnings back
            warnings.filters = old_filters
        bib_style = cp.CitationStylesStyle(style, validate=False)
        # TODO: specify which tags of formatter we want
        bibliography = cp.CitationStylesBibliography(bib_style, bib_source,
                                                     cp.formatter.plain)
        citation = cp.Citation([cp.CitationItem(key)])
        bibliography.register(citation)
    finally:
        os.unlink(fname)

    biblio_out = bibliography.bibliography()
    assert(len(biblio_out) == 1)
    biblio_out = ''.join(biblio_out[0])
    return biblio_out # if biblio_out else str(bibtex_entry)

# TODO: harmonize order of arguments
class PickleOutput(object):
    def __init__(self, collector, fn=DUECREDIT_FILE):
        self.collector = collector
        self.fn = fn

    def dump(self):
        with open(self.fn, 'wb') as f:
            pickle.dump(self.collector, f)

    @classmethod
    def load(cls, filename=DUECREDIT_FILE):
        with open(filename, 'rb') as f:
            return pickle.load(f)

class BibTeXOutput(object):  # TODO some parent class to do what...?
    def __init__(self, fd, collector):
        self.fd = fd
        self.collector = collector

    def dump(self):
        for citation in self.collector.citations.values():
            try:
                bibtex = get_bibtex_rendering(citation.entry)
            except:
                lgr.warning("Failed to generate bibtex for %s" % citation.entry)
                continue
            self.fd.write(bibtex.rawentry + "\n")


def load_due(filename):
    return PickleOutput.load(filename)
