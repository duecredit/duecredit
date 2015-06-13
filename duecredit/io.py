import pickle
import requests

def import_doi(doi):
    headers = {'Accept': 'text/bibliography; style=bibtex'}
    url = 'http://dx.doi.org/' + doi
    r = requests.get(url, headers=headers)
    if not r.text.strip().startswith('@'):
        raise ValueError('wrong doi specified')
    return r.text.strip()


class TextOutput(object):  # TODO some parent class to do what...?
    def __init__(self, fd, collector):
        self.fd = fd
        self.collector = collector

    def dump(self):
        self.fd.write("""
DueCredit Report

%d pieces were cited:
        """ % len(self.collector.citations))
        # Group by type???? e.g. Donations should have different meaning from regular ones
        # Should we provide some base classes to differentiate between types? probbly not -- tags?


class PickleOutput(object):
    def __init__(self, collector, fn='.duecredit.p'):
        self.collector = collector
        self.fn = fn

    def dump(self):
        with open(self.fn, 'wb') as f:
            pickle.dump(self.collector, f)
