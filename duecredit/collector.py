# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Citation and citations Collector classes"""
from __future__ import annotations

from collections import namedtuple
from functools import wraps
import logging
import os
import sys
from typing import TYPE_CHECKING, Any

from .config import DUECREDIT_FILE
from .entries import DueCreditEntry
from .io import PickleOutput, TextOutput
from .utils import borrowdoc, never_fail
from .versions import external_versions

lgr = logging.getLogger("duecredit.collector")

if TYPE_CHECKING:
    from typing_extensions import Self

CitationKey = namedtuple("CitationKey", ["path", "entry_key"])


class Citation:
    """Encapsulates citations and information on their use"""

    def __init__(
        self,
        entry: DueCreditEntry,
        description: str | None = None,
        path: str | None = None,
        version: None | str | tuple[str, str] = None,
        cite_module: bool = False,
        tags: list[str] | None = None,
    ):
        """Cite a reference

        Parameters
        ----------
        entry: str or DueCreditEntry
          The entry to use, either identified by its id or a new one (to be added)
        description: str, optional
          Description of what this functionality provides
        path: str
          Path to the object which this citation associated with.  Format is
          "module[.submodules][:[class.]method]", i.e. ":" is used to separate module
          path from the path within the module.
        version: str or tuple, version
          Version of the beast (e.g. of the module) where applicable
        cite_module: bool, optional
          If it is a module citation, setting it to True would make that module citeable
          even without internal duecredited functionality invoked.  Should be used only for
          core packages whenever it is reasonable to assume that its import constitute
          its use (e.g. numpy)
        tags: list of str, optional
          Tags to associate with the given code/reference combination.  Some tags have
          associated semantics in duecredit, e.g. (see full list in README.md or
          https://github.com/duecredit/duecredit/#tags)
          - "implementation" [default] tag describes as an implementation of the cited
            method
          - "reference-implementation" tag describes as the original implementation (ideally
            by the authors of the paper) of the cited method
          - "another-implementation" tag describes some other implementation of the method
          - "use" tag points to publications demonstrating a worthwhile noting use
            the method
          - "edu" references to tutorials, textbooks and other materials useful to learn
            more
          - "donate" should be commonly used with Url entries to point to the websites
            describing how to contribute some funds to the referenced project
        """
        if path is None:
            raise ValueError("Must specify path")
        self._entry = entry
        self._description = description
        # We might want extract all the relevant functionality into a separate class
        self._path = path
        self._cite_module = cite_module
        if tags is None:
            tags = ["implementation"]
        self.tags = tags or []
        self.version = version
        self.count = 0

    def __repr__(self) -> str:
        argl = [repr(self._entry)]
        if self._description:
            argl.append(f"description={self._description!r}")
        if self._path:
            argl.append(f"path={self._path!r}")
        if self._cite_module:
            argl.append(f"cite_module={self._cite_module!r}")

        if argl:
            args = ", ".join(argl)
        else:
            args = ""
        return self.__class__.__name__ + f"({args})"

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        # TODO: verify value, if we are not up for it -- just make _path public
        self._path = path

    @property
    def entry(self) -> DueCreditEntry:
        return self._entry

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def cite_module(self) -> bool:
        return self._cite_module

    @property
    def cites_module(self) -> bool | None:
        if not self.path:
            return None
        return ":" not in self.path

    @property
    def module(self) -> str | None:
        if not self.path:
            return None
        return self.path.split(":", 1)[0]

    @property
    def package(self) -> str | None:
        module = self.module
        if not module:
            return None
        return module.split(".", 1)[0]

    @property
    def objname(self) -> str | None:
        if not self.path:
            return None
        spl = self.path.split(":", 1)
        if len(spl) > 1:
            return spl[1]
        else:
            return None

    def __contains__(self, entry: Self) -> bool:
        """Checks if provided entry 'contained' in this one given its path

        If current entry is associated with a module, contained will be an entry
        of
        - the same module
        - submodule of the current module or function within

        If current entry is associated with a specific function/class, it can contain
        another entry if it really contains it as an attribute
        """
        if self.cites_module:
            return (
                (self.path == entry.path)
                or (entry.path.startswith(self.path + "."))
                or (entry.path.startswith(self.path + ":"))
            )
        else:
            return entry.path.startswith(self.path + ".")

    @property
    def key(self) -> CitationKey:
        return CitationKey(self.path, self.entry.key)

    @staticmethod
    def get_key(path: str, entry_key: str) -> CitationKey:
        return CitationKey(path, entry_key)

    def set_entry(self, newentry: DueCreditEntry) -> None:
        self._entry = newentry


class DueCreditCollector:
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
    def __init__(
        self,
        entries: dict[str, DueCreditEntry] | None = None,
        citations: dict[CitationKey, Citation] | None = None,
    ) -> None:
        self._entries = entries or {}
        self.citations = citations or {}

    @never_fail
    def add(self, entry: DueCreditEntry | list[DueCreditEntry]) -> None:
        """entry should be a DueCreditEntry object"""
        if isinstance(entry, list):
            for e in entry:
                self.add(e)
        else:
            key = entry.get_key()
            self._entries[key] = entry
            lgr.log(1, "Collector added entry %s", key)

    @never_fail
    def load(self, src: str) -> None:
        """Loads references from a file or other recognizable source

        ATM supported only
        - .bib files
        """
        # raise NotImplementedError
        if isinstance(src, str):
            if src.endswith(".bib"):
                self._load_bib(src)
            else:
                raise NotImplementedError("Format not yet supported")
        else:
            raise ValueError("Must be a string")

    def _load_bib(self, src: str) -> None:
        lgr.debug(f"Loading {src}")

    # # TODO: figure out what would be the optimal use for the __call__
    # def __call__(self, *args, **kwargs):
    #     # TODO: how to determine and cite originating module???
    #     #       - we could use inspect but many people complain
    #     #         that it might not work with other Python
    #     #         implementations
    #     pass # raise NotImplementedError

    @never_fail
    @borrowdoc(Citation, "__init__")
    def cite(self, entry: DueCreditEntry | str, **kwargs: Any) -> Citation:
        # TODO: if cite is invoked but no path is provided -- we must figure it out
        # I guess from traceback, otherwise how would we know later to associate it
        # with modules???
        path = kwargs.get("path")
        if path is None:
            raise ValueError("path must be provided")

        if isinstance(entry, DueCreditEntry):
            # new one -- add it
            self.add(entry)
            entry_ = self._entries[entry.get_key()]
        else:
            entry_ = self._entries[entry]

        entry_key = entry_.get_key()
        citation_key = Citation.get_key(path=path, entry_key=entry_key)
        try:
            citation = self.citations[citation_key]
        except KeyError:
            self.citations[citation_key] = citation = Citation(entry_, **kwargs)
        assert isinstance(citation, Citation)
        assert citation.key == citation_key
        # update citation count
        citation.count += 1

        # TODO: theoretically version shouldn't differ if we don't preload previous results
        if not citation.version:
            version = kwargs.get("version")

            if not version and citation.path:
                modname = citation.path.split(".", 1)[0]

                if "." in modname:
                    package = modname.split(".", 1)[0]
                else:
                    package = modname

                # package_loaded = sys.modules.get(package)
                # if package_loaded:
                #     # find the citation for that module
                #     for citation in self.citations.values():
                #         if citation.package == package \
                #                 and not citation.version:
                version = external_versions[package]
            citation.version = version

        return citation

    def _citations_fromentrykey(self) -> dict[str, Citation]:
        """Return a dictionary with the current citations indexed by the entry key"""
        citations_key = dict()
        for (_path, entry_key), citation in self.citations.items():
            if entry_key not in citations_key:
                citations_key[entry_key] = citation

        return citations_key

    @staticmethod
    def _args_match_conditions(
        conditions: dict[Any, Any], *fargs: Any, **fkwargs: Any
    ) -> bool:
        """Helper to identify when to trigger citation given parameters to the function call"""
        for (argpos, kwarg), values in conditions.items():
            # main logic -- assess default and if get to the next one if
            # given argument is not present
            if not ((len(fargs) > argpos) or (kwarg in fkwargs)):
                if "DC_DEFAULT" not in values:
                    # if value was specified but not provided and not default
                    # conditions are not satisfied
                    return False
                continue

            # "extract" the value.  Must be defined here
            value = "__duecredit_magical_undefined__"
            if len(fargs) > argpos:
                value = fargs[argpos]
            if kwarg in fkwargs:
                value = fkwargs[kwarg]
            assert value != "__duecredit_magical_undefined__"

            if "." in kwarg:
                # we were requested to condition based on the value of the attribute
                # of the value.  So get to the attribute(s) value
                for attr in kwarg.split(".")[1:]:
                    value = getattr(value, attr)

            # Value is present but not matching
            if value not in values:
                return False

        # if checks passed -- we must have matched conditions
        return True

    @never_fail
    @borrowdoc(Citation, "__init__", replace="PLUGDOCSTRING")
    def dcite(self, *args, **kwargs):
        """Decorator for references.  PLUGDOCSTRING

        Parameters
        ----------
        conditions: dict, optional
          If reference should be cited whenever parameters to the function call
          satisfy given values (all of the specified).
          Each key in the dictionary is a 2 element tuple with first element, integer,
          pointing to a position of the argument in the original function call signature,
          while second provides the name, thus if used as a keyword argument.
          Use "DC_DEFAULT" keyword as a value to depict default value (e.g. if no
          explicit value was provided for that positional or keyword argument).
          If "keyword argument" is of the form "obj.attr1.attr2", then actual value
          for comparison would be taken by extracting attr1 (and then attr2) attributes
          from the provided value.  So, if desired to condition of the state of the object,
          you can use `(0, "self.attr1") : {...values...}`

        Examples
        --------

        >>> from duecredit import due
        >>> @due.dcite('XXX00', description="Provides an answer for meaningless existence")
        ... def purpose_of_life():
        ...     return None

        Conditional citation given argument to the function

        >>> @due.dcite('XXX00', description="Relief through the movement",
        ...            conditions={(1, 'method'): {'purge', 'DC_DEFAULT'}})
        ... @due.dcite('XXX01', description="Relief through the drug treatment",
        ...            conditions={(1, 'method'): {'drug'}})
        ... def relief(x, method='purge'):
        ...     if method == 'purge': return "crap"
        ...     elif method == 'drug': return "swallow"
        >>> relief("doesn't matter")
        'crap'

        Conditional based on the state of the object

        >>> class Citeable:
        ...     def __init__(self, param=None):
        ...         self.param = param
        ...     @due.dcite('XXX00', description="The same good old relief",
        ...                conditions={(0, 'self.param'): {'magic'}})
        ...     def __call__(self, data):
        ...         return sum(data)
        >>> Citeable('magic')([1, 2])
        3
        """

        def func_wrapper(func):
            conditions = kwargs.pop("conditions", {})
            path = kwargs.get("path")
            if not path:
                # deduce path from the actual function which was decorated
                # TODO: must include class name  but can't !!!???
                modname = func.__module__
                path = kwargs["path"] = f"{modname}:{func.__name__}"
            else:
                # TODO: we indeed need to separate path logic outside
                modname = path.split(":", 1)[0]

            # if decorated function was invoked, it means that we need
            # to cite that even if it is a module. But do not override
            # value if user explicitly stated
            if "cite_module" not in kwargs:
                kwargs["cite_module"] = True

            # TODO: might make use of inspect.getmro
            # see e.g.
            # http://stackoverflow.com/questions/961048/get-class-that-defined-method
            lgr.debug(f"Decorating func {func.__name__} within module {modname}")
            # TODO: unittest for all the __version__ madness

            # TODO: check if we better use wrapt module which provides superior "correctness"
            #       of decorating.  vcrpy uses wrapt, and that thing seems to wrap
            @wraps(func)
            def cite_wrapper(*fargs, **fkwargs):
                try:
                    if not conditions or self._args_match_conditions(
                        conditions, *fargs, **fkwargs
                    ):
                        self.cite(*args, **kwargs)
                except Exception as e:
                    lgr.warning(f"Failed to cite due to {e}")
                return func(*fargs, **fkwargs)

            cite_wrapper.__duecredited__ = func
            return cite_wrapper

        return func_wrapper

    @never_fail
    def __repr__(self) -> str:
        argl = []
        if self.citations:
            argl.append(f"citations={self.citations!r}")
        if self._entries:
            argl.append(f"entries={self._entries!r}")

        if argl:
            args = ", ".join(argl)
        else:
            args = ""
        return self.__class__.__name__ + f"({args})"

    @never_fail
    def __str__(self) -> str:
        return f"{self.__class__.__name__} {len(self._entries)} entries, {len(self.citations)} citations"


# TODO: redo heavily -- got very messy
class CollectorSummary:
    """A helper which would take care about exporting citations upon its Death"""

    def __init__(
        self,
        collector: DueCreditCollector,
        outputs: str = "stdout,pickle",
        fn: str = DUECREDIT_FILE,
    ) -> None:
        self._due = collector
        self.fn = fn
        # for now decide on output "format" right here
        self._outputs = [
            self._get_output_handler(type_.lower().strip(), collector, fn=fn)
            for type_ in os.environ.get("DUECREDIT_OUTPUTS", outputs).split(",")
            if type_
        ]

    @staticmethod
    def _get_output_handler(
        type_: str, collector: DueCreditCollector, fn: str | None = None
    ) -> TextOutput | PickleOutput:
        # just a little factory
        if type_ in ("stdout", "stderr"):
            return TextOutput(getattr(sys, type_), collector)
        elif type_ == "pickle":
            return PickleOutput(collector, fn=fn)
        else:
            raise NotImplementedError()

    def dump(self) -> None:
        for output in self._outputs:
            output.dump()


# TODO:  provide HTML, MD, RST etc output formats
