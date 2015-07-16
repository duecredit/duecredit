# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Citation and citations Collector classes"""

import os
import sys
from functools import wraps

from .config import DUECREDIT_FILE
from .entries import DueCreditEntry
from .stub import InactiveDueCreditCollector
from .io import TextOutput, PickleOutput
from .utils import never_fail, borrowdoc

import logging
lgr = logging.getLogger('duecredit.collector')


class Citation(object):
    """Encapsulates citations and information on their use"""

    def __init__(self, entry, description=None, path=None, version=None, tags=['implementation']):
        """Cite a reference

        Parameters
        ----------
        entry: str or DueCreditEntry
          The entry to use, either identified by its id or a new one (to be added)
        description: str, optional
          Description of what this functionality provides
        path: str, optional
          Path to the object which this citation associated with.  Format is
          "module[.submodules][:[class.]method]", i.e. ":" is used to separate module
          path from the path within the module.
        version: str or tuple, version
          Version of the beast (e.g. of the module) where applicable
        tags: list of str, optional
          Add tags for the reference for this method.  Some tags have associated
          semantics in duecredit, e.g.
          - "implementation" [default] tag describes as an implementation of the cited
             method
          - "reference" tag describes as the original implementation of
            the cited method
          - "use" tag points to publications demonstrating a worthwhile noting use
             the method
          - "edu" references to tutorials, textbooks and other materials useful to learn
            more
        """
        self._entry = entry
        self._description = description
        # We might want extract all the relevant functionality into a separate class
        self._path = path
        self.count = 0
        self.tags = tags or []
        self.version = version

    def __repr__(self):
        args = [repr(self._entry)]
        if self._description:
            args.append("description={0}".format(repr(self._description)))
        if self._path:
            args.append("path={0}".format(repr(self._path)))

        if args:
            args = ", ".join(args)
        else:
            args = ""
        return self.__class__.__name__ + '({0})'.format(args)

    @property
    def path(self):
        return self._path

    @property
    def entry(self):
        return self._entry

    @property
    def description(self):
        return self._description

    @property
    def cites_module(self):
        return self.path and ':' not in self.path

    @property
    def module(self):
        if not self.path:
            return None
        return self.path.split(':', 1)[0]

    def __contains__(self, entry):
        """Checks if provided entry 'contained' in this one given its path

        If current entry is associated with a module, contained will be an entry
        of
        - the same module
        - submodule of the current module or function within

        If current entry is associated with a specific function/class, it can contain
        another entry if it really contains it as an attribute
        """
        if self.cites_module:
            return ((self.path == entry.path) or
                    (entry.path.startswith(self.path + '.')) or
                    (entry.path.startswith(self.path + ':')))
        else:
            return entry.path.startswith(self.path + '.')


class DueCreditCollector(object):
    """Collect the references

    The mighty beast which will might become later a proxy on the way to
    talk to a real collector

    Parameters
    ----------
    entries : list of DueCreditEntry, optional
      List of reference items (BibTeX, Doi, etc) known to the collector
    citations : list of Citation, optional
      List of citations -- associations between references and particular
      code, with a description for its use, tags etc
    """

    # TODO?  rename "entries" to "references"?  or "references" is closer to "citations"
    def __init__(self, entries=None, citations=None):
        self._entries = entries or {}
        self.citations = citations or {}

    @never_fail
    def add(self, entry):
        """entry should be a DueCreditEntry object"""
        if isinstance(entry, list):
            for e in entry:
                self.add(e)
        else:
            key = entry.get_key()
            self._entries[key] = entry

    @never_fail
    def load(self, src):
        """Loads references from a file or other recognizable source

        ATM supported only
        - .bib files
        """
        # raise NotImplementedError
        if isinstance(src, str):
            if src.endswith('.bib'):
                self._load_bib(src)
            else:
                raise NotImplementedError('Format not yet supported')
        else:
            raise ValueError('Must be a string')

    def _load_bib(self, src):
        lgr.debug("Loading %s" % src)

    # # TODO: figure out what would be the optimal use for the __call__
    # def __call__(self, *args, **kwargs):
    #     # TODO: how to determine and cite originating module???
    #     #       - we could use inspect but many people complain
    #     #         that it might not work with other Python
    #     #         implementations
    #     pass # raise NotImplementedError

    @never_fail
    @borrowdoc(Citation, "__init__")
    def cite(self, entry, **kwargs):
        if isinstance(entry, DueCreditEntry):
            # new one -- add it
            self.add(entry)
            entry_ = entry
        else:
            entry_ = self._entries[entry]
        entry_key = entry_.get_key()

        # TODO: we must allow the same entry be present in multiple citations, so
        # RF to do so
        if entry_key not in self.citations:
            self.citations[entry_key] = Citation(entry_, **kwargs)

        citation = self.citations[entry_key]
        citation.count += 1
        if not citation.version:
            citation.version = kwargs.get('version', None)
        # TODO: update path and use here?

        return citation

    @never_fail
    @borrowdoc(Citation, "__init__", replace="PLUGDOCSTRING")
    def dcite(self, *args, **kwargs):
        """Decorator for references.  PLUGDOCSTRING

        Examples
        --------

        @due.dcite('XXX00', description="Provides an answer for meaningless existence")
        def purpose_of_life():
            return None

        """
        def func_wrapper(func):
            if 'path' not in kwargs:
                # deduce path from the actual function which was decorated
                # TODO: must include class name
                module_ = func.__module__
                # TODO: might make use of inspect.getmro
                # see e.g.
                # http://stackoverflow.com/questions/961048/get-class-that-defined-method
                lgr.debug("Decorating func %s within module %s" % (func.__name__, module_))
                kwargs['path'] = '%s:%s' % (module_, func.__name__)
                # TODO: unittest for all the __version__ madness
                module_loaded = sys.modules.get(module_)
                if module_loaded and hasattr(module_loaded, '__version__'):
                    # find the citation for that module
                    for citation in self.citations:
                        if citation.module == module_ \
                                and citation.version is None:
                            citation.version = module_loaded.__version__

            # TODO: check if we better use wrapt module which provides superior "correctness"
            #       of decorating.  vcrpy uses wrapt, and that thing seems to wrap
            @wraps(func)
            def cite_wrapper(*fargs, **fkwargs):
                citation = self.cite(*args, **kwargs)
                return func(*fargs, **fkwargs)
            return cite_wrapper
        return func_wrapper

    @never_fail
    def __repr__(self):
        args = []
        if self.citations:
            args.append("citations={0}".format(repr(self.citations)))
        if self._entries:
            args.append("entries={0}".format(repr(self._entries)))

        if args:
            args = ", ".join(args)
        else:
            args = ""
        return self.__class__.__name__ + '({0})'.format(args)

    @never_fail
    def __str__(self):
        return self.__class__.__name__ + \
            ' {0:d} entries, {1:d} citations'.format(
                len(self._entries), len(self.citations))


# TODO: redo heavily -- got very messy
class CollectorSummary(object):
    """A helper which would take care about exporting citations upon its Death
    """
    def __init__(self, collector, outputs="stdout,pickle", fn=DUECREDIT_FILE):
        self._due = collector
        self.fn = fn
        # for now decide on output "format" right here
        self._outputs = [
            self._get_output_handler(
                type_.lower().strip(), collector, fn=fn)
            for type_ in os.environ.get('DUECREDIT_OUTPUTS', outputs).split(',')
            if type_
        ]

    @staticmethod
    def _get_output_handler(type_, collector, fn=None):
        # just a little factory
        if type_ in ("stdout", "stderr"):
            return TextOutput(getattr(sys, type_), collector)
        elif type_ == "pickle":
            return PickleOutput(collector, fn=fn)
        else:
            raise NotImplementedError()

    def dump(self):
        for output in self._outputs:
            output.dump()


# TODO:  provide HTML, MD, RST etc formattings

