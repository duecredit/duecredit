"""TODO"""

import logging
import os

from .entries import *
from .version import __version__, __release_date__

_logger = logging.get('duecredit')
_logger.setLevel(logging.DEBUG)

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
        if isinstance(src, basestr):
            if src.endswith('.bib'):
                self._load_bib(src)

    def _load_bib(self, src):
        _logger.debug("Loading %s" % src)

    def __call__(self, *args, **kwargs):
        # TODO: how to determine and cite originating module???
        #       - we could use inspect but many people complain
        #         that it might not work with other Python
        #         implementations
        pass # raise NotImplementedError

    def dec(self, *args, **kwargs):
        """Decorator for references
        """
        # raise NotImplementedError
        pass

    def export(self):
        _logger.info("EXPORTING")

def is_active():
    env_enable = os.environ.get('DUECREDIT_ENABLE')
    if env_enable and env_enable.lower() in ('1', 'yes'):
        return True
    return False

# Rebind the collector's methods to the module here
if is_active():
    due = DueCreditCollector()
else:
    # provide stubs which would do nothing
    raise NotImplementedError()
    pass
