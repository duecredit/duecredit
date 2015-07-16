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

from six import iteritems
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

__all__ = ['DueCreditInjector', 'find_object']

def find_object(mod, path):
    """Finds object among present within module "mod" given path specification within

    Returns
    """
    obj = mod  # we will look first within module
    for obj_name in path.split('.'):
        parent = obj
        obj = getattr(parent, obj_name)
    return parent, obj_name, obj


class DueCreditInjector(object):

    def __init__(self, collector=None):
        if collector is None:
            from duecredit import due
            collector = due
        self._collector = collector
        self._entry_records = {}  # dict:  modulename: {object: [('entry', cite kwargs)]}

    def add(self, modulename, obj, entry,
            min_version=None, max_version=None,
            **kwargs):
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
        **kwargs
          Keyword arguments to be passed into cite. Note that "level" will be automatically set
          if not provided
        """
        if modulename not in self._entry_records:
            self._entry_records[modulename] = {}
        if obj not in self._entry_records[modulename]:
            self._entry_records[modulename][obj] = []
        obj_entries = self._entry_records[modulename][obj]
        obj_entries.append({'entry': entry,
                            'kwargs': kwargs,
                            'min_version': min_version,
                            'max_version': max_version})

    def process(self, name, mod):
        """Process import of the module, possibly decorating some methods with duecredit entries
        """
        if not name in self._entry_records:
            return
        lgr.debug("Request to process known to injector module %s", name)

        try:
            mod = sys.modules[name]
        except KeyError:
            lgr.warning("Failed to access module %s among sys.modules" % name)
            return

        # go through the known entries and register them within the collector, and
        # decorate corresponding methods
        # There could be multiple records per module
        for obj_path, obj_entry_records in iteritems(self._entry_records[name]):
            try:
                parent, obj_name, obj = find_object(mod, obj_path)
            except KeyError as e:
                lgr.warning("Could not find %s in module %s: %s" % (obj_path, mod, e))
                continue

            # there could be multiple per func
            for obj_entry_record in obj_entry_records:
                entry = obj_entry_record['entry']
                # Add entry explicitly
                self._collector.add(entry)
                # TODO: decorate the object (function, method) which will also add entries
                decorator = self._collector.dcite(entry.get_key(), **obj_entry_record['kwargs'])
                setattr(parent, obj_name, decorator(obj))

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

