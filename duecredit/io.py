from . import CACHE_DIR
from .entries import BibTeX, Doi
import os
import pickle
import requests

def import_doi(doi):
    headers = {'Accept': 'text/bibliography; style=bibtex'}
    url = 'http://dx.doi.org/' + doi
    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    if not r.text.strip().startswith('@'):
        raise ValueError('wrong doi specified')
    cached = os.path.join(CACHE_DIR, doi)
    if not os.path.exists(cached):
        with open(cached) as f:
            f.write(r)
    return r.text.strip()


class TextOutput(object):  # TODO some parent class to do what...?
    def __init__(self, fd, collector):
        self.fd = fd
        self.collector = collector

    def dump(self):
        self.fd.write('\nDueCredit Report\n%d pieces were cited:\n'
                      % len(self.collector.citations))
        for entry in self.collector.citations.itervalues():
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
    def __init__(self, collector, fn='.duecredit.p'):
        self.collector = collector
        self.fn = fn

    def dump(self):
        with open(self.fn, 'wb') as f:
            pickle.dump(self.collector, f)
