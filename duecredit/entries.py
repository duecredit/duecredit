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

import logging
lgr = logging.getLogger('duecredit.entries')


class DueCreditEntry(object):
    def __init__(self, rawentry, key=None):
        self._rawentry = rawentry
        self._key = key or rawentry.lower()

    def __eq__(self, other):
        return (
            (self._rawentry == other._rawentry) and
            (self._key == other._key)
        )

    def get_key(self):
        return self._key

    @property
    def key(self):
        return self.get_key()

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

    def format(self):
        # TODO: return nice formatting of the entry
        return str(self._rawentry)


class BibTeX(DueCreditEntry):
    def __init__(self, bibtex, key=None):
        super(BibTeX, self).__init__(bibtex.strip())
        self._key = None
        self._reference = None
        self._process_rawentry()
        if key is not None:
            # use the one provided, not the parsed one
            lgr.debug("Replacing parsed key %s for BibTeX with the provided %s",
                      self._key, key)
            self._key = key

    def _process_rawentry(self):
        reg = re.match(r"\s*@(?P<type>\S*)\s*\{\s*(?P<key>\S*)\s*,.*",
                       self._rawentry, flags=re.MULTILINE)
        assert(reg)
        matches = reg.groupdict()
        self._key = matches['key']


class Text(DueCreditEntry):
    """Just a free text entry without any special super powers in rendering etc
    """
    pass  # nothing special I guess


class Doi(DueCreditEntry):

    @property
    def doi(self):
        return self._rawentry


class Url(DueCreditEntry):

    @property
    def url(self):
        return self._rawentry

