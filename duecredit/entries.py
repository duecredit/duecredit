#!/usr/bin/python
#emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*- 
#ex: set sts=4 ts=4 sw=4 noet:
"""

 COPYRIGHT: Yaroslav Halchenko 2014

 LICENSE: MIT

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""

__author__ = 'Yaroslav Halchenko'
__copyright__ = 'Copyright (c) 2014 Yaroslav Halchenko'
__license__ = 'MIT'

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


class Doi(DueCreditEntry):
    def __init__(self, doi, key=None):
        super(Doi, self).__init__(doi, key)
        # TODO


class Donate(DueCreditEntry):
    def __init__(self, url, key=None):
        super(Donate, self).__init__(url, key)
        self.url = url

