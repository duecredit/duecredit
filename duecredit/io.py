from citeproc.source.bibtex import BibTeX as cpBibTeX
import citeproc as cp

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

    def dump(self, tags=None):

        # TODO: all that configuration/options should be done outside
        if not tags:
            tags = os.environ.get('DUECREDIT_REPORT_TAGS', 'reference,implementation').split(',')
        tags = set(tags)

        citations = self.collector.citations
        if tags != {'*'}:
            # Filter out citations
            citations = dict((k, c)
                             for k, c in iteritems(citations)
                             if tags.intersection(c.tags))


        # Separate logic (model) from presentation (view).  Let's first create a "model"
        # Collect all citations under their corresponding packages

        # TODO: such logic/setup would not work if we want to allow citations for modules
        # within packages, so we really need a 3 level reporting:  package / module / obj
        cited_packages = {}
        for citation in itervalues(citations):
            package = citation.package
            objname = citation.objname

            if package not in cited_packages:
                # list of two lists -- one citations for the package itself,
                # another one will be also dictionary for citations for functions
                cited_packages[package] = [[], {}]

            if citation.cites_module is True:
                cited_packages[package][0].append(citation)
            else:
                if objname not in cited_packages[package][1]:
                    # initiate a list of citations for that object
                    cited_packages[package][1][objname] = []
                cited_packages[package][1][objname].append(citation)

        # Now prune references to packages which had no citations ot internal functionality
        # TODO: theoretically should be done before pruning based on tags so we still
        # catch those which were used anyhow
        for package, (package_citations, obj_citations) in list(iteritems(cited_packages)): # operate on a copy
            # check if any citation is tagged as 'cite-on-import', so we
            # always cite if it was imported
            if any('cite-on-import' in c.tags for c in package_citations):
                continue
            if not obj_citations:
                cited_packages.pop(package)

        # Now we can "render" different views of our "model"
        # Here for now just text BUT that is where we can "split" the logic and provide
        # different renderings given the model -- text, rest, md, tex+latex, whatever
        self.fd.write('DueCredit Report:\n')

        refnr = 1
        citations_ordered = []

        for package, (package_citations, obj_citations) in iteritems(cited_packages):
            # package level citation
            versions = sorted(map(str, set(str(r.version) for r in package_citations)))
            refnr = len(citations_ordered) + 1
            self.fd.write('- {0} (v {1}) [{2}]\n'.format(
                package,
                ', '.join(versions),
                ', '.join(str(x) for x in range(refnr, refnr+len(package_citations)))))
            citations_ordered.extend(package_citations)


            # function level citations
            for obj, citations in iteritems(obj_citations):
                # TODO -- there could be multiple, and they might have different
                # description so must be groupped accordingly. For now just simply listing them
                # all separately
                for citation in citations:
                    refnr = len(citations_ordered) + 1
                    self.fd.write('  - {0} ({1}) [{2}]\n'.format(
                        citation.path,
                        citation.description,
                        refnr))
                    citations_ordered.extend(citations)

        # Let's collect some stats now (before it was misleading since multiple citations
        # could have been for the same package or object)
        self.fd.write('\n{0} modules cited\n{1} functions cited\n'.format(
            len(cited_packages), sum(len(x[1]) for x in itervalues(cited_packages))))
        if citations_ordered:
            self.fd.write('\nReferences\n' + '-' * 10 + '\n')
            for i, citation in enumerate(citations_ordered):
                self.fd.write('\n'"[%d] " % (i+1) + get_text_rendering(citation, style=self.style))
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
