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
        self._delayed_injections = {}
        self._entry_records = {}  # dict:  modulename: {object: [('entry', cite kwargs)]}
        self._orig_import = None
        self._processed_modules = set()
        # We need to process modules only after we are done with all nested imports, otherwise we
        # might be trying to prcess them too early -- whenever they are not yet linked to their
        # parent's namespace. So we will keep track of import level and set of modules which
        # would need to be processed whenever we are back at __import_level == 1
        self.__import_level = 0
        self.__queue_to_process = set()

    def _populate_delayed_injections(self):
        self._delayed_injections = {}
        for inj_mod_name in get_modules_for_injection():
            assert(inj_mod_name.startswith('mod_'))
            mod_name = inj_mod_name[4:]
            lgr.debug("Adding delayed injection for %s", (mod_name,))
            self._delayed_injections[mod_name] = inj_mod_name

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

    @property
    def _import_level_prefix(self):
        return "." * self.__import_level

    def _process_delayed_injection(self, mod_name):
        lgr.debug("%sProcessing delayed injection for %s", self._import_level_prefix, mod_name)
        inj_mod_name = self._delayed_injections[mod_name]
        assert(not hasattr(self._orig_import, '__duecredited__'))
        try:
            inj_mod = self._orig_import("duecredit.injections." + inj_mod_name,
                                        fromlist=["duecredit.injections"])
        except Exception as e:
            raise RuntimeError("Failed to import %s: %r" % (inj_mod_name, e))
        # TODO: process min/max_versions etc
        assert(hasattr(inj_mod, 'inject'))
        inj_mod.inject(self)

    def process(self, mod_name): #, mod):
        """Process import of the module, possibly decorating some methods with duecredit entries
        """

        # We need to mark that module as processed EARLY, so we don't try to re-process it
        # while doing _process_delayed_injection
        self._processed_modules.add(mod_name)

        if mod_name in self._delayed_injections:
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

    def activate(self, retrospect=True):
        """
        Parameters
        ----------
        retrospect : bool, optional
          Either consider already loaded modules
        """

        if not self._orig_import: #not hasattr(self._orig_import, '__duecredited__'):
            # for paranoid Yarik so we have assurance we are not somehow
            # overriding our decorator
            self._orig_import = __builtin__.__import__

            # just a check for paranoid me
            @wraps(__builtin__.__import__)
            def __import(name, *args, **kwargs):
                # importing submodule might result in importing a new one and
                # name here is not sufficient to determine which module would actually
                # get imported unless level=0 (absolute import), but that one rarely used

                # could be old-style or new style relative import!
                # args[0] -> globals, [1] -> locals(), [2] -> fromlist, [3] -> level
                level = args[3] if len(args) >= 4 else kwargs.get('level', -1)
                # fromlist = args[2] if len(args) >= 3 else kwargs.get('fromlist', [])

                if not retrospect and not self._processed_modules:
                    # we were asked to not consider those modules which were already loaded
                    # so let's assume that they were all processed already
                    self._processed_modules = set(sys.modules)

                import_level_prefix = self._import_level_prefix
                try:
                    self.__import_level += 1

                    mod = self._orig_import(name, *args, **kwargs)

                    new_imported_modules = set(sys.modules.keys()) - self._processed_modules

                    if new_imported_modules:
                        #lgr.log(4, "%d new modules were detected upon import of %s (level=%s)", #. Prev imported now: %s",
                        #        len(new_imported_modules), name, level)#, prev_imported_modules)
                        lgr.log(2, "%s%d new modules were detected: %s, upon import of %s (level=%s)", #. Prev imported now: %s",
                                import_level_prefix, len(new_imported_modules), new_imported_modules, name, level)#, prev_imported_modules)

                    for imported_mod in new_imported_modules:
                        if imported_mod in self.__queue_to_process:
                            # we saw it already
                            continue
                        # lgr.log(1, "Name %r was imported as %r (path: %s). fromlist: %s, level: %s",
                        #        name, mod.__name__, getattr(mod, '__path__', None), fromlist, level)
                        # package
                        package = imported_mod.split('.', 1)[0]
                        if package != imported_mod \
                                and package not in self._processed_modules \
                                and package not in self.__queue_to_process:
                            # if its parent package wasn't yet imported before
                            lgr.log(3, "%sParent of %s, %s wasn't yet processed, doing now",
                                    import_level_prefix, imported_mod, package)
                            self.__queue_to_process.add(package)
                        self.__queue_to_process.add(imported_mod)
                finally:
                    self.__import_level -= 1

                if self.__import_level == 0:
                    # process the queue
                    lgr.debug("Processing queue of imported %d modules", len(self.__queue_to_process))
                    while self.__queue_to_process:
                        self.process(self.__queue_to_process.pop())
                    assert(not len(self.__queue_to_process))

                lgr.log(1, "%sReturning %s", import_level_prefix, mod)
                return mod
            __import.__duecredited__ = True

            self._populate_delayed_injections()

            if retrospect:
                lgr.debug("Considering previously loaded %d modules", len(sys.modules))
                # operate on keys() (not iterator) since we might end up importing delayed injection modules etc
                for mod_name in sys.modules.keys():
                    self.process(sys.modules[mod_name])

            lgr.debug("Assigning our importer")
            __builtin__.__import__ = __import

        else:
            lgr.warning("Seems that we are calling duecredit_importer twice."
                        " No harm is done but shouldn't happen")


    #@staticmethod
    def deactivate(self):
        if not self._orig_import:
            lgr.warning("_orig_import is not yet known, so we haven't decorated default importer yet."
                        " Nothing TODO")
            return

        lgr.debug("Assigning original importer")
        __builtin__.__import__ = self._orig_import
        self._orig_import = None

    def __del__(self):
        if self._orig_import is not None:
            self.deactivate()
            super(DueCreditInjector, self).__del__()

