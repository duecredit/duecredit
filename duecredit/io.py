# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

# Just for testing of robust operation
import os
if 'DUECREDIT_TEST_EARLY_IMPORT_ERROR' in os.environ.keys():
    raise ImportError("DUECREDIT_TEST_EARLY_IMPORT_ERROR")

import re
import locale
import time
from collections import defaultdict
import copy
from os.path import dirname, exists
import pickle
import tempfile
from six import PY2, itervalues, iteritems
import warnings
import platform
from time import sleep

from .config import CACHE_DIR, DUECREDIT_FILE
from .entries import BibTeX, Doi, Text, Url
from .log import lgr
from .versions import external_versions

_PREFERRED_ENCODING = locale.getpreferredencoding()
platform_system = platform.system().lower()
on_windows = platform_system == 'windows'


def get_doi_cache_file(doi):
    # where to cache bibtex entries
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, doi)


def import_doi(doi, sleep=0.5, retries=10):
    import requests
    cached = get_doi_cache_file(doi)

    if exists(cached):
        with open(cached) as f:
            doi = f.read()
            if PY2:
                return doi.decode('utf-8')
            return doi

    # else -- fetch it
    headers = {'Accept': 'application/x-bibtex; charset=utf-8'}
    url = 'https://doi.org/' + doi
    while retries > 0:
        lgr.debug("Submitting GET to %s with headers %s", url, headers)
        r = requests.get(url, headers=headers)
        r.encoding = 'UTF-8'
        bibtex = r.text.strip()
        if bibtex.startswith('@'):
            # no more retries necessary
            break
        lgr.warning("Failed to obtain bibtex from doi.org, retrying...")
        time.sleep(sleep)  # give some time to the server
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


def _is_contained(toppath, subpath):
    if ':' not in toppath:
        return ((toppath == subpath) or
                (subpath.startswith(toppath + '.')) or
                (subpath.startswith(toppath + ':')))
    else:
        return subpath.startswith(toppath + '.')


class Output(object):
    """A generic class for setting up citations that then will be outputted
    differently (e.g., Bibtex, Text, etc.)"""
    def __init__(self, fd, collector):
        self.fd = fd
        self.collector = collector

    def _get_collated_citations(self, tags=None, all_=None):
        """Given all the citations, filter only those that the user wants and
        those that were actually used"""
        if not tags:
            tags = os.environ.get('DUECREDIT_REPORT_TAGS', 'reference-implementation,implementation,dataset').split(',')
        if all_ is None:
            # consult env var
            all_ = os.environ.get('DUECREDIT_REPORT_ALL', '').lower() in {'1', 'true', 'yes', 'on'}
        tags = set(tags)

        citations = self.collector.citations
        if tags != {'*'}:
            # Filter out citations based on tags
            citations = dict((k, c)
                             for k, c in iteritems(citations)
                             if tags.intersection(c.tags))

        packages = defaultdict(list)
        modules = defaultdict(list)
        objects = defaultdict(list)

        # store the citations according to their path and divide them into
        # the right level
        for (path, entry_key), citation in iteritems(citations):
            if ':' in path:
                objects[path].append(citation)
            elif '.' in path:
                modules[path].append(citation)
            else:
                packages[path].append(citation)

        # now we need to filter out the packages that don't have modules
        # or objects cited, or are specifically requested
        cited_packages = list(packages)
        cited_modobj = list(modules) + list(objects)
        for package in cited_packages:
            package_citations = packages[package]
            if all_ or \
                any(filter(lambda x: x.cite_module, package_citations)) or \
                any(filter(lambda x: _is_contained(package, x), cited_modobj)):
                continue
            else:
                # we don't need it
                del packages[package]

        return packages, modules, objects

    def dump(self, tags=None):
        raise NotImplementedError



class TextOutput(Output):
    def __init__(self, fd, collector, style=None):
        super(TextOutput, self).__init__(fd, collector)
        self.style = style
        if 'DUECREDIT_STYLE' in os.environ.keys():
            self.style = os.environ['DUECREDIT_STYLE']
        else:
            self.style = 'harvard1'


    @staticmethod
    def _format_citations(citations, citation_nr):
        descriptions = map(str, set(str(r.description) for r in citations))
        versions = map(str, set(str(r.version) for r in citations))
        refnrs = map(str, [citation_nr[c.entry.key] for c in citations])
        path = citations[0].path

        return '- {0} / {1} (v {2}) [{3}]\n'.format(
            ", ".join(descriptions), path, ', '.join(versions), ', '.join(refnrs))

    def dump(self, tags=None):
        # get 'model' of citations
        packages, modules, objects = self._get_collated_citations(tags)
        # put everything into a single dict
        pmo = {}
        pmo.update(packages)
        pmo.update(modules)
        pmo.update(objects)

        # get all the paths
        paths = sorted(list(pmo))
        # get all the entry_keys in order
        entry_keys = [c.entry.key for p in paths for c in pmo[p]]
        # make a dictionary entry_key -> citation_nr
        citation_nr = defaultdict(int)
        refnr = 1
        for entry_key in entry_keys:
            if entry_key not in citation_nr:
                citation_nr[entry_key] = refnr
                refnr += 1

        self.fd.write('\nDueCredit Report:\n')
        start_refnr = 1
        for path in paths:
            # since they're lexicographically sorted by path, dependencies
            # should be maintained
            cit = pmo[path]
            if ':' in path or '.' in path:
                self.fd.write('  ')
            self.fd.write(self._format_citations(cit, citation_nr))
            start_refnr += len(cit)

        # Print out some stats
        stats = [(len(packages), 'package'),
                 (len(modules), 'module'),
                 (len(objects), 'function')]
        for n, cit_type in stats:
            self.fd.write('\n{0} {1} cited'.format(n, cit_type if n == 1
                                                      else cit_type + 's'))
        # now print out references
        printed_keys = []
        if len(pmo) > 0:
            self.fd.write('\n\nReferences\n' + '-' * 10 + '\n')
            for path in paths:
                for cit in pmo[path]:
                    ek = cit.entry.key
                    if ek not in printed_keys:
                        self.fd.write('\n[{0}] '.format(citation_nr[ek]))
                        self.fd.write(get_text_rendering(cit,
                                                        style=self.style))
                        printed_keys.append(ek)
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
    elif isinstance(entry, Text):
        return entry.format()
    elif isinstance(entry, Url):
        return "URL: {}".format(entry.format())
    else:
        return str(entry)


def get_bibtex_rendering(entry):
    if isinstance(entry, Doi):
        return BibTeX(import_doi(entry.doi))
    elif isinstance(entry, BibTeX):
        return entry
    else:
        raise ValueError("Have no clue how to get bibtex out of %s" % entry)


def condition_bibtex(bibtex):
    """Given a bibtex entry, "condition" it for processing with citeproc

    Primarily a set of workarounds for either non-standard BibTeX entries
    or citeproc bugs
    """
    # XXX: workaround atm to fix zenodo bibtexs, convert @data to @misc
    # and also ; into and
    if bibtex.startswith('@data'):
        bibtex = bibtex.replace('@data', '@misc', 1)
        bibtex = bibtex.replace(';', ' and')
    bibtex = bibtex.replace(u'\u2013', '--') + "\n"
    # workaround for citeproc 0.3.0 failing to parse a single page pages field
    # as for BIDS paper.  Workaround to add trailing + after pages number
    # related issue asking for a new release: https://github.com/brechtm/citeproc-py/issues/72
    bibtex = re.sub(r'(pages\s*=\s*["{]\d+)(["}])', r'\1+\2', bibtex)
    # partial workaround for citeproc failing to parse page numbers when they contain non-numeric characters
    # remove opening letter, e.g. 'S123' -> '123'
    # related issue: https://github.com/brechtm/citeproc-py/issues/74
    bibtex = re.sub(r'(pages\s*=\s*["{])([a-zA-Z])', r'\g<1>', bibtex)
    bibtex = bibtex.encode('utf-8')
    return bibtex


def format_bibtex(bibtex_entry, style='harvard1'):
    try:
        from citeproc.source.bibtex import BibTeX as cpBibTeX
        import citeproc as cp
    except ImportError as e:
        raise RuntimeError(
            "For formatted output we need citeproc and all of its dependencies "
            "(such as lxml) but there is a problem while importing citeproc: %s"
            % str(e))
    decode_exceptions = UnicodeDecodeError
    try:
        from citeproc.source.bibtex.bibparse import BibTeXDecodeError
        decode_exceptions = (decode_exceptions, BibTeXDecodeError)
    except ImportError:
        # this version doesn't yet have this exception defined
        pass
    key = bibtex_entry.get_key()
    # need to save it temporarily to use citeproc-py
    fname = tempfile.mktemp(suffix='.bib')
    try:
        with open(fname, 'wb') as f:
            f.write(condition_bibtex(bibtex_entry.rawentry))
        # We need to avoid cpBibTex spitting out warnings
        old_filters = warnings.filters[:]  # store a copy of filters
        warnings.simplefilter('ignore', UserWarning)
        try:
            try:
                bib_source = cpBibTeX(fname)
            except decode_exceptions as e:
                # So .bib must be having UTF-8 characters.  With
                # a recent (not yet released past v0.3.0-68-g9800dad
                # we should be able to provide encoding argument
                bib_source = cpBibTeX(fname, encoding='utf-8')
        except Exception as e:
            msg = "Failed to process BibTeX file %s: %s." % (fname, e)
            citeproc_version = external_versions['citeproc']
            if 'unexpected keyword argument' in str(e) and \
                    citeproc_version and citeproc_version < '0.4':
                err = "need a newer citeproc-py >= 0.4.0"
                msg += " You might just " + err
            else:
                err = str(e)
            lgr.error(msg)
            return "ERRORED: %s" % err
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
        if not os.environ.get("DUECREDIT_KEEPTEMP"):
            exceptions = (OSError, WindowsError) if on_windows else OSError
            for i in range(50):
                try:
                    os.unlink(fname)
                except exceptions:
                    if i < 49:
                        sleep(0.1)
                        continue
                    else:
                        raise
                break

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

class BibTeXOutput(Output):
    def __init__(self, fd, collector):
        super(BibTeXOutput, self).__init__(fd, collector)

    def dump(self, tags=None):
        packages, modules, objects = self._get_collated_citations(tags)
        # get all the citations in order
        pmo = {}
        pmo.update(packages)
        pmo.update(modules)
        pmo.update(objects)

        # get all the paths
        paths = sorted(list(pmo))

        entries = []
        for path in paths:
            for c in pmo[path]:
                if c.entry not in entries:
                    entries.append(c.entry)

        for entry in entries:
            try:
                bibtex = get_bibtex_rendering(entry)
            except:
                lgr.warning("Failed to generate bibtex for %s" % entry)
                continue
            self.fd.write(bibtex.rawentry + "\n")


def load_due(filename):
    return PickleOutput.load(filename)
