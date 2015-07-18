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

from os.path import basename, join as pathjoin, dirname
from glob import glob
import sys
from functools import wraps

from .. import lgr

from six import iteritems
if sys.version_info < (3,):
    import __builtin__
else:
    import builtins as __builtin__


__all__ = ['DueCreditInjector', 'find_object']

def get_modules_for_injection():
    """Get local modules which provide "inject" method to provide delayed population of injector
    """
    return sorted([basename(x)[:-3]
                   for x in glob(pathjoin(dirname(__file__), "mod_*.py"))
                   ])

def find_object(mod, path):
    """Finds object among present within module "mod" given path specification within

    Returns
    -------

    parent, obj_name, obj
    """
    obj = mod  # we will look first within module
    for obj_name in path.split('.'):
        parent = obj
        obj = getattr(parent, obj_name)
    return parent, obj_name, obj


class DueCreditInjector(object):
    """Takes care about "injecting" duecredit references into 3rd party modules upon their import

    First entries to be "injected" need to be add'ed to the instance.
    To not incure significant duecredit startup penalty, those entries are added
    for a corresponding package only whenever corresponding top-level module gets
    imported.
    """
    def __init__(self, collector=None):
        if collector is None:
            from duecredit import due
            collector = due
        self._collector = collector
        self._delayed_entries = {}
        self._entry_records = {}  # dict:  modulename: {object: [('entry', cite kwargs)]}

    def _populate_delayed_entries(self):
        self._delayed_entries = {}
        for inj_mod_name in get_modules_for_injection():
            assert(inj_mod_name.startswith('mod_'))
            mod_name = inj_mod_name[4:]
            lgr.debug("Adding delayed injection for %s", (mod_name,))
            self._delayed_entries[mod_name] = inj_mod_name

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

    def _process_delayed_injection(self, mod_name):
        lgr.debug("Processing delayed injection for %s", mod_name)
        inj_mod_name = self._delayed_entries[mod_name]
        try:
            inj_mod = __import__("duecredit.injections." + inj_mod_name,
                                 fromlist=["duecredit.injections"])
        except Exception as e:
            raise RuntimeError("Failed to import %s: %s" % (inj_mod_name, e))
        # TODO: process min/max_versions etc
        assert(hasattr(inj_mod, 'inject'))
        inj_mod.inject(self)

    def process(self, mod_name, mod):
        """Process import of the module, possibly decorating some methods with duecredit entries
        """

        if mod_name in self._delayed_entries:
            # should be hit only once, "theoretically" unless I guess reimport is used etc
            self._process_delayed_injection(mod_name)

        if mod_name not in self._entry_records:
            return
        lgr.debug("Request to process known to injector module %s", mod_name)

        try:
            mod = sys.modules[mod_name]
        except KeyError:
            lgr.warning("Failed to access module %s among sys.modules" % mod_name)
            return

        # go through the known entries and register them within the collector, and
        # decorate corresponding methods
        # There could be multiple records per module
        for obj_path, obj_entry_records in iteritems(self._entry_records[mod_name]):
            if obj_path:
                # so we point to an object within the mod
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
                if obj_path:  # if not entire module -- decorate!
                    # TODO: decorate the object (function, method) which will also add entries
                    decorator = self._collector.dcite(entry.get_key(), **obj_entry_record['kwargs'])
                    setattr(parent, obj_name, decorator(obj))

    def activate(self):
        global _orig__import

        _orig__import_ = __builtin__.__import__
        if not hasattr(_orig__import_, '__duecredited__'):
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
            __import.__duecredited__ = True

            self._populate_delayed_entries()

            lgr.debug("Assigning our importer")
            __builtin__.__import__ = __import

            # TODO: retrospect sys.modules about possibly already loaded modules
            # which we cover, so they need to be decorated at this point
        else:
            lgr.warning("Seems that we are calling duecredit_importer twice."
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

