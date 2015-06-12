from functools import wraps

from .entries import DueCreditEntry

import logging
lgr = logging.getLogger('duecredit.collector')

class DueCreditCollector(object):
    """Collect the references

    The mighty beast which will might become later a proxy on the way to
    talk to a real collector
    """
    def __init__(self):
        self._entries = {}

    def add(self, entry):
        """entry should be a DueCreditEntry object"""
        if isinstance(entry, list):
            for e in entry:
                self.add(e)
        else:
            key = entry.get_key()
            reference = entry.get_reference()
            self._entries[key] = reference

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

    # TODO: figure out what would be the optimal use for the __call__
    def __call__(self, *args, **kwargs):
        # TODO: how to determine and cite originating module???
        #       - we could use inspect but many people complain
        #         that it might not work with other Python
        #         implementations
        pass # raise NotImplementedError

    def cite(self, entry, *args, **kwargs):
        """Decorator for references

        Parameters
        ----------
        key_entry: str or DueCreditEntry
          The entry to use, either identified by its id or a new one (to be added)
        """
        self.add(entry)
        key_entry = entry.get_key()

        # self._citations.add(key_entry)
        # raise NotImplementedError
        pass

    def dcite(self, *args, **kwargs):
        """Decorator for references.  Wrap a function or

        Examples
        --------

        @due.dcite('XXX00', use="Provides an answer for meaningless existence")
        def purpose_of_life():
            return None

        """
        def func_wrapper(func):
            @wraps(func)
            def cite_wrapper(*fargs, **fkwargs):
                self.cite(*args, **kwargs)
                return func(*fargs, **fkwargs)
            return cite_wrapper
        return func_wrapper

    def __del__(self):
        lgr.info("EXPORTING")


class InactiveDueCreditCollector(object):
    """A short construct which should serve a stub in the modules were we insert it"""
    @classmethod
    def _donothing(*args, **kwargs):  pass
    # TODO: would not work as a decorator
    @classmethod
    def dcite(*args, **kwargs):
        def nondecorating_decorator(func):
             return func
        return nondecorating_decorator
    cite = load = add = _donothing