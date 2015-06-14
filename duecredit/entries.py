#!/usr/bin/python
#emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*- 
#ex: set sts=4 ts=4 sw=4 noet:
import re

class DueCreditEntry(object):
    def __init__(self, rawentry, key=None):
        self._rawentry = rawentry
        self._key = key or rawentry.lower()

    def get_key(self):
        return self._key

    def _process_rawentry(self):
        pass

    def __repr__(self):
        args = [repr(self._rawentry),
                "key={0}".format(repr(self._key))]
        args = ", ".join(args)
        return self.__class__.__name__ + '({0})'.format(args)


class BibTeX(DueCreditEntry):
    def __init__(self, bibtex, key=None):
        super(BibTeX, self).__init__(bibtex)
        self._key = None
        self._reference = None
        self._process_rawentry()

    def _process_rawentry(self):
        reg = re.match("@(?P<type>\S*)\s*{\s*(?P<key>\S*)\s*,.*",
                       self._rawentry, flags=re.MULTILINE)
        assert(reg)
        matches = reg.groupdict()
        self._key = matches['key']


class FreeTextEntry(DueCreditEntry):
    pass # nothing special I guess


class Doi(DueCreditEntry):
    def __init__(self, doi, key=None):
        super(Doi, self).__init__(doi, key)
        # TODO


class Donate(DueCreditEntry):
    def __init__(self, url, key=None):
        super(Donate, self).__init__(url, key)
        self.url = url

