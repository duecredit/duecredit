from . import CACHE_DIR, DUECREDIT_FILE
from .entries import BibTeX, Doi
import os
from os.path import dirname, exists
import pickle
import requests
from six import PY2

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

    def dump(self):
        self.fd.write('\nDueCredit Report\n%d pieces were cited:\n'
                      % len(self.collector.citations))
        for entry in self.collector.citations.values():
            self.fd.write('{0}\n'.format(get_text_rendering(entry)))

def get_text_rendering(entry):
    if isinstance(entry, Doi):
        bibtex_rendering = get_bibtex_rendering(entry)
        return get_text_rendering(bibtex_rendering)
    elif isinstance(entry, BibTeX):
        # TODO: get Text rendering of bibtex
        return entry.format()
    else:
        return str(entry)

def get_bibtex_rendering(entry):
    if isinstance(entry, Doi):
        return BibTeX(import_doi(entry.doi))

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
