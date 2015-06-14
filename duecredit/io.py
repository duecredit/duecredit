from citeproc.source.bibtex import BibTeX as cpBibTeX
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import formatter
from citeproc import Citation, CitationItem

import os
from os.path import dirname, exists
import pickle
import requests
import tempfile
from six import PY2

from . import CACHE_DIR, DUECREDIT_FILE
from .entries import BibTeX, Doi

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
    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    bibtex = r.text.strip()
    if not bibtex.startswith('@'):
        raise ValueError('wrong doi specified')
    if not exists(cached):
        cache_dir = dirname(cached)
        if not exists(cache_dir):
            os.makedirs(cache_dir)
        with open(cached, 'w') as f:
            f.write(bibtex.encode('utf-8'))
    return bibtex


class TextOutput(object):  # TODO some parent class to do what...?
    def __init__(self, fd, collector):
        self.fd = fd
        self.collector = collector
        # TODO: check that CLS style actually exists
        if 'DUECREDIT_STYLE' in os.environ.keys():
            self.style = os.environ['DUECREDIT_STYLE']
        else:
            self.style = 'apa'

    def dump(self):
        citations_rendered = [
            get_text_rendering(citation, style=self.style)
            for citation in self.collector.citations.values()]

        self.fd.write("""
DueCredit Report

%d pieces were cited:
%s
""" % (len(self.collector.citations), '\n'.join(citations_rendered)))


def get_text_rendering(citation, style='apa'):
    entry = citation.entry
    if isinstance(entry, Doi):
        bibtex_rendering = get_bibtex_rendering(entry)
        return get_text_rendering(bibtex_rendering)
    elif isinstance(entry, BibTeX):
        return format_bibtex(entry, style=style)
    else:
        return str(entry)


def get_bibtex_rendering(entry):
    if isinstance(entry, Doi):
        return BibTeX(import_doi(entry.doi))


def format_bibtex(bibtex_entry, style='apa'):
    key = bibtex_entry.get_key()
    # need to save it temporarily to use citeproc-py
    fname = tempfile.mktemp(suffix='.bib')
    try:
        with open(fname, 'wt') as f:
            f.write(bibtex_entry.rawentry.encode('utf-8'))
        bib_source = cpBibTeX(fname)
        bib_style = CitationStylesStyle(style, validate=False)
        # TODO: specify which kind of formatter we want
        bibliography = CitationStylesBibliography(bib_style, bib_source,
                                                  formatter.plain)
        citation = Citation([CitationItem(key)])
        bibliography.register(citation)
    finally:
        os.unlink(fname)

    biblio_out = bibliography.bibliography()
    assert(len(biblio_out) == 1)
    biblio_out = ''.join(biblio_out[0])
    return biblio_out # if biblio_out else str(bibtex_entry)


class PickleOutput(object):
    def __init__(self, collector, fn=DUECREDIT_FILE):
        self.collector = collector
        self.fn = fn

    def dump(self):
        with open(self.fn, 'wb') as f:
            pickle.dump(self.collector, f)

    @classmethod
    def load(cls, filename=DUECREDIT_FILE):
        with open(filename) as f:
            return pickle.load(f)
