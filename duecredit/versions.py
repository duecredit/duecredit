# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
from __future__ import annotations

"""Module to help maintain a registry of versions for external modules etc
"""
from collections.abc import KeysView
from importlib.metadata import version as metadata_version
from os import linesep
import sys
from types import ModuleType
from typing import Any

from looseversion import LooseVersion
from packaging.version import Version


# To depict an unknown version, which can't be compared by mistake etc
class UnknownVersion:
    """For internal use"""

    def __str__(self) -> str:
        return "UNKNOWN"

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        raise TypeError("UNKNOWN version is not comparable")


class ExternalVersions:
    """Helper to figure out/use versions of the external modules.

    It maintains a dictionary of `packaging.version.Version`s to make
    comparisons easy.  If a version string doesn't conform to Version,
    LooseVersion will be used.  If a version can't be deduced for a module,
    'None' is assigned
    """

    UNKNOWN = UnknownVersion()

    def __init__(self) -> None:
        self._versions: dict[str, Version | LooseVersion | UnknownVersion] = {}

    @classmethod
    def _deduce_version(
        klass, module: ModuleType
    ) -> Version | LooseVersion | UnknownVersion:
        version = None
        for attr in ("__version__", "version"):
            if hasattr(module, attr):
                version = getattr(module, attr)
                break

        if isinstance(version, tuple) or isinstance(version, list):
            #  Generate string representation
            version = ".".join(str(x) for x in version)

        if not version:
            # Try importlib.metadata
            # module name might be different, and I found no way to
            # deduce it for citeproc which comes from "citeproc-py"
            # distribution
            modname = module.__name__
            try:
                version = metadata_version(
                    {"citeproc": "citeproc-py"}.get(modname, modname)
                )
            except Exception:
                pass  # oh well - no luck either

        if version:
            try:
                return Version(version)
            except ValueError:
                # let's then go with Loose one
                return LooseVersion(version)
        else:
            return klass.UNKNOWN

    def __getitem__(
        self, module: Any
    ) -> Version | LooseVersion | UnknownVersion | None:
        # when ran straight in its source code -- fails to discover nipy's version.. TODO
        # if module == 'nipy':
        if not isinstance(module, str):
            modname = module.__name__
        else:
            modname = module
            module = None

        if modname not in self._versions:
            if module is None:
                if modname not in sys.modules:
                    try:
                        module = __import__(modname)
                    except ImportError:
                        return None
                else:
                    module = sys.modules[modname]

            self._versions[modname] = self._deduce_version(module)

        return self._versions.get(modname, self.UNKNOWN)

    def keys(self) -> KeysView[str]:
        """Return names of the known modules"""
        return self._versions.keys()

    def __contains__(self, item: str) -> bool:
        return item in self._versions

    @property
    def versions(self) -> dict[str, Version | LooseVersion | UnknownVersion]:
        """Return dictionary (copy) of versions"""
        return self._versions.copy()

    def dumps(self, indent: bool | str = False, preamble: str = "Versions:") -> str:
        """Return listing of versions as a string

        Parameters
        ----------
        indent: bool or str, optional
          If set would instruct on how to indent entries (if just True, ' '
          is used). Otherwise returned in a single line
        preamble: str, optional
          What preamble to the listing to use
        """
        items = ["{}={}".format(k, self._versions[k]) for k in sorted(self._versions)]
        out = "%s" % preamble
        if indent:
            indent_ = " " if indent is True else indent
            out += (linesep + indent_).join([""] + items) + linesep
        else:
            out += " " + " ".join(items)
        return out


external_versions = ExternalVersions()
