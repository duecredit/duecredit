# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.   Originates from datalad package distributed
#   under MIT license
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
import re
from six import PY2

class DueCreditEntry(object):
    def __init__(self, rawentry, key=None):
        self._rawentry = rawentry
        self._key = key or rawentry.lower()

    def get_key(self):
        return self._key

    @property
    def rawentry(self):
        if PY2:
            return unicode(self._rawentry)
        else:
            return self._rawentry

    def _process_rawentry(self):
        pass

    def __repr__(self):
        args = [repr(self._rawentry),
                "key={0}".format(repr(self._key))]
        args = ", ".join(args)
        return self.__class__.__name__ + '({0})'.format(args)


class BibTeX(DueCreditEntry):
    def __init__(self, bibtex, key=None):
        super(BibTeX, self).__init__(bibtex.strip())
        self._key = None
        self._reference = None
        self._process_rawentry()

    def _process_rawentry(self):
        reg = re.match("\s*@(?P<type>\S*)\s*\{\s*(?P<key>\S*)\s*,.*",
                       self._rawentry, flags=re.MULTILINE)
        assert(reg)
        matches = reg.groupdict()
        self._key = matches['key']

    def format(self):
        # TODO: return nice formatting of the entry
        return str(self._rawentry)

class FreeTextEntry(DueCreditEntry):
    pass # nothing special I guess


class Doi(DueCreditEntry):
    def __init__(self, doi, key=None):
        super(Doi, self).__init__(doi, key)
        self.doi = doi
        # TODO


class Url(DueCreditEntry):
    def __init__(self, url, key=None):
        super(Url, self).__init__(url, key)
        self.url = url

