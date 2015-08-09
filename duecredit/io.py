from citeproc.source.bibtex import BibTeX as cpBibTeX
import citeproc as cp

from collections import defaultdict
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

    # TODO: refactor name to sth more intuitive
    def _model_citations(self, tags=None):
        if not tags:
            tags = os.environ.get('DUECREDIT_REPORT_TAGS', 'reference,implementation').split(',')
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
                objects['citations'][path].append(citation)
                objects['entry_keys'][path].append(entry_key)
            elif '.' in path:
                modules['citations'][path].append(citation)
                modules['entry_keys'][path].append(entry_key)
            else:
                packages['citations'][path].append(citation)
                packages['entry_keys'][path].append(entry_key)
        return packages, modules, objects

    def dump(self, tags=None):
        # get 'model' of citations
        packages, modules, objects = self._model_citations(tags)

        citations_ordered = []
        # set up view
        keys2refnr = defaultdict(int)  # mapping key -> ref nr
        refnr = 1

        # package level
        for package in sorted(packages['entry_keys']):
            for entry_key in packages['entry_keys'][package]:
                if entry_key not in keys2refnr:
                    keys2refnr[entry_key] = refnr
                    refnr += 1
            citations_ordered.append(package)
            # module level
            for module in sorted(filter(lambda x: package in x, modules['entry_keys'])):
                for entry_key_mod in modules['entry_keys'][module]:
                    if entry_key_mod not in keys2refnr:
                        keys2refnr[entry_key_mod] = refnr
                        refnr += 1
                citations_ordered.append(module)
            # object level
            for obj in sorted(filter(lambda x: package in x, objects['entry_keys'])):
                for entry_key_obj in objects['entry_keys'][obj]:
                    if entry_key_obj not in keys2refnr:
                        keys2refnr[entry_key_obj] = refnr
                        refnr += 1
                citations_ordered.append(obj)

        # Now we can "render" different views of our "model"
        # Here for now just text BUT that is where we can "split" the logic and provide
        # different renderings given the model -- text, rest, md, tex+latex, whatever
        self.fd.write('DueCredit Report:\n')

        for path in citations_ordered:
            if ':' in path:
                self.fd.write('  ')
                citations = objects['citations'][path]
                entry_keys = objects['entry_keys'][path]
            elif '.' in path:
                self.fd.write('  ')
                citations = modules['citations'][path]
                entry_keys = modules['entry_keys'][path]
            else:
                citations = packages['citations'][path]
                entry_keys = packages['entry_keys'][path]
            versions = sorted(map(str, set(str(r.version) for r in citations)))
            refnrs = sorted([str(keys2refnr[entry_key]) for entry_key in entry_keys])
            self.fd.write('- {0} (v {1}) [{2}]\n'.format(path, ' '.join(versions), ', '.join(refnrs)))

        # Print out some stats
        obj_names = ('packages', 'modules', 'functions')
        n_citations = map(len, (packages['citations'], modules['citations'], objects['citations']))
        for citation_type, n in zip(obj_names, n_citations):
            self.fd.write('\n{0} {1} cited'.format(n, citation_type))

        if keys2refnr:
            citations_fromentrykey = self.collector.citations_fromentrykey()
            self.fd.write('\n\nReferences\n' + '-' * 10 + '\n')
            # collect all the entries used
            refnr2keys = sorted([(nr, keys) for keys, nr in iteritems(keys2refnr)])
            for nr, key in refnr2keys:
                self.fd.write('\n[{0}] '.format(nr))
                self.fd.write(get_text_rendering(citations_fromentrykey[key], style=self.style))
            self.fd.write('\n')

def get_text_rendering(citation, style='harvard1'):
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
