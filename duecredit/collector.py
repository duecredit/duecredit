from functools import wraps
import logging
lgr = logging.getLogger('lgr')

class DueCreditCollector(object):
    """Collect the references

    The mighty beast which will might become later a proxy on the way to
    talk to a real collector
    """

    def add(self, entry):
        # raise NotImplementedError
        pass

    def load(self, src):
        """Loads references from a file or other recognizable source

        ATM supported only
        - .bib files
        """
        # raise NotImplementedError
        if isinstance(src, str):
            if src.endswith('.bib'):
                self._load_bib(src)

    def _load_bib(self, src):
        lgr.debug("Loading %s" % src)

    # TODO: figure out what would be the optimal use for the __call__
    def __call__(self, *args, **kwargs):
        # TODO: how to determine and cite originating module???
        #       - we could use inspect but many people complain
        #         that it might not work with other Python
        #         implementations
        pass # raise NotImplementedError

    def cite(self, *args, **kwargs):
        """Decorator for references
        """
        # raise NotImplementedError
        pass

    def dcite(self, *args, **kwargs):
        """Decorator for references
        """
        # raise NotImplementedError
        #@wraps
        pass

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