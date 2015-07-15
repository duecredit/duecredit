# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Importer which would also call decoration on a module upon import
"""

__docformat__ = 'restructuredtext'

import sys
from functools import wraps

from .. import lgr

if sys.version_info < (3,):
    import __builtin__
else:
    import builtins as __builtin__

"""
Original version which is too fragile and just too intrusive
since we are literally to replace the entire importer

import imp

class DueCreditImporter(object):
    def __init__(self):
        print("Initialized our importer")
        pass

    def find_module(self,  fullname, path=None):
        print(" Storing path %s for %s" % (path, fullname))
        self.path = path
        return self # for now for every module

    def load_module(self, name):
        if name in sys.modules:
            print("  Returning loaded already module for %s" % name)
            return sys.modules[name]
        path = self.path if '.' in name else None
        print("   Finding module %s under %s" % (name.split('.')[-1], path))
        module_info = imp.find_module(name.split('.')[-1], path)
        module = imp.load_module(name, *module_info)
        sys.modules[name] = module

        print ("  Imported %s" % name)
        return module

sys.meta_path = [DueCreditImporter()]
"""

__all__ = ['DueCreditInjector']

class DueCreditInjector(object):

    def __init__(self):
        self._entries = {}  # dict:  modulename: {object: [(cite args, cite kwargs)]}

    def add(self, modulename, obj, min_version=None, max_version=None,
            *args, **kwargs):
        """Add a citation for a given module or object within it

        Parameters
        ----------
        modulename : string
          Name of the module (possibly a sub-module)
        obj : string or None
          Name of the object (function, method within a class) or None (if for entire module)
        min_version, max_version : string or tuple, optional
          Min (inclusive) / Max (exclusive) version of the module where this
          citation is applicable
        *args, **kwargs
          Arguments to be passed into cite. Note that "level" will be automatically set
          if not provided
        """
        if modulename not in self._entries:
            self._entries[modulename] = {}
        if obj not in self._entries[modulename]:
            self._entries[modulename][obj] = []
        obj_entries = self._entries[modulename][obj]
        obj_entries.append({'args': args, 'kwargs': kwargs,
                            'min_version': min_version,
                            'max_version': max_version})

    def process(self, name, mod):
        """Process import of the module, possibly decorating some methods with duecredit entries
        """
        if name in self._entries:
            lgr.info("Module %s known to injector was imported", name)
            # TODO: decorate those registered things
            pass  # TODO -- decorate those objects
        pass

    def activate(self):
        global _orig__import

        _orig__import_ = __builtin__.__import__
        if not hasattr(_orig__import_, '__duecredited'):
            # for paranoid Yarik so we have assurance we are not somehow
            # overriding our decorator
            _orig__import = _orig__import_

            # just a check for paranoid me
            @wraps(__builtin__.__import__)
            def __import(name, *args, **kwargs):
                already_imported = name in sys.modules
                mod = _orig__import(name, *args, **kwargs)
                # Optimization: worth processing only when importing was done for the first time
                if not already_imported:
                    lgr.log(1, "Module %s was imported", name)
                    self.process(name, mod)
                return mod
            __import.__duecredited = True

            lgr.debug("Assigning our importer")
            __builtin__.__import__ = __import
        else:
            lgr.warning("Seems that we are activating duecredit_importer is called twice."
                        " No harm is done but shouldn't happen")

    @staticmethod
    def deactivate():
        if '_orig__import' not in globals():
            lgr.warning("_orig_import is not known, so we haven't decorated default importer yet."
                        " Nothing TODO")
            return

        lgr.debug("Assigning original importer")
        global _orig__import
        __builtin__.__import__ = _orig__import

