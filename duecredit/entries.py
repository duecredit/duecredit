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

class DueCreditEntry(object):
    def __init__(self, rawentry, load=None):
        self._load = load
        self._rawentry = rawentry
        self._key = None
        self._reference = None

    def get_key(self):
        return self._key

    def get_reference(self):
        return self._reference

class BibTeX(DueCreditEntry):
    def __init__(self, bibtex):
        super(BibTeX, self).__init__(bibtex)
        # TODO
        self._key = None
        self._reference = None


class Doi(DueCreditEntry):
    def __init__(self, doi, load=None, id_=None):
        super(Doi, self).__init__(doi)
        self._id = id_
        # TODO
        self._key = None
        self._reference = None

class Donate(DueCreditEntry):
    def __init__(self, url):
        self.url = url

class BirthCertificate(DueCreditEntry):
    pass
