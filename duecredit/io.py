from citeproc.source.bibtex import BibTeX as cpBibTeX
import citeproc as cp

import sys
import os
from os.path import dirname, exists
import pickle
import requests
import tempfile
from six import PY2
import warnings

from . import CACHE_DIR, DUECREDIT_FILE
from .entries import BibTeX, Doi
from . import lgr

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
            if PY2:
                f.write(bibtex.encode('utf-8'))
            else:
                f.write(bibtex)
    return bibtex


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

    def dump(self):
        citations_rendered = [(i+1, citation,
            "[%d] " % (i+1) + get_text_rendering(citation, style=self.style))
            for i, citation in enumerate(self.collector.citations.values())]

        count_modules = 0
        count_functions = 0
        self.fd.write('DueCredit Report:\n')
        for refnr, citation, _ in citations_rendered:
            if citation.cites_module:
                count_modules += 1
                this_module = citation.module
                self.fd.write('- {0} (v {1}) [{2}]\n'.format(
                    this_module,
                    citation.version,
                    refnr))
                # TODO: make this better
                for refnr_, citation_, _ in citations_rendered:
                    # TODO -- extract module name and compare
                    if this_module in citation_.path \
                            and citation.path != citation_.path:
                        count_functions += 1
                        try:
                            self.fd.write('  - {0} ({1}) [{2}]\n'.format(
                                citation_.module,
                                citation_.description,
                                refnr_))
                        except Exception as e:
                            lgr.warning("CRAPPED HERE: %s" % (str(e)))
                            continue
        self.fd.write('\n{0} modules cited\n{1} functions cited\n'.format(
            count_modules, count_functions))
        if count_modules or count_functions:
            self.fd.write('References\n' + '-' * 10 + '\n')
        self.fd.write('\n'.join([c[-1] for c in citations_rendered]))
        self.fd.write('\n')

def get_text_rendering(citation, style='harvard1'):
    # TODO: smth fked up smwhere
    from .collector import Citation
    # TODO: and we need to move it away -- circular imports etc
    if isinstance(citation, Citation):
        entry = citation.entry
    else:
        entry = citation
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

