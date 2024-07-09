# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
from __future__ import annotations

# Just for testing of robust operation
import os

if "DUECREDIT_TEST_EARLY_IMPORT_ERROR" in os.environ.keys():
    raise ImportError("DUECREDIT_TEST_EARLY_IMPORT_ERROR")

from collections import defaultdict
import locale
from os.path import dirname, exists
import pickle
import re
import tempfile
import time
from typing import TYPE_CHECKING, Any
import warnings

from packaging.version import Version

from .config import CACHE_DIR, DUECREDIT_FILE
from .entries import BibTeX, Doi, DueCreditEntry, Text, Url
from .log import lgr
from .versions import external_versions

if TYPE_CHECKING:
    from .collector import Citation

_PREFERRED_ENCODING = locale.getpreferredencoding()


def get_doi_cache_file(doi: str) -> str:
    # where to cache bibtex entries
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, doi)


def import_doi(doi: str, sleep: float = 0.5, retries: int = 10) -> str:
    import requests

    cached = get_doi_cache_file(doi)

    if exists(cached):
        with open(cached) as f:
            doi = f.read()
            return doi

    # else -- fetch it
    headers = {"Accept": "application/x-bibtex; charset=utf-8"}
    url = "https://doi.org/" + doi
    while retries > 0:
        lgr.debug("Submitting GET to %s with headers %s", url, headers)
        r = requests.get(url, headers=headers)
        r.encoding = "UTF-8"
        bibtex = r.text.strip()
        if bibtex.startswith("@"):
            # no more retries necessary
            break
        lgr.warning("Failed to obtain bibtex from doi.org, retrying...")
        time.sleep(sleep)  # give some time to the server
        retries -= 1
    status_code = r.status_code
    if not bibtex.startswith("@"):
        raise ValueError(
            "Query %(url)s for BibTeX for a DOI %(doi)s (wrong doi?) has failed. "
            "Response code %(status_code)d. "
            # 'BibTeX response was: %(bibtex)s'
            % locals()
        )
    if not exists(cached):
        cache_dir = dirname(cached)
        if not exists(cache_dir):
            os.makedirs(cache_dir)
        with open(cached, "w") as f:
            f.write(bibtex)
    return bibtex


def _is_contained(toppath: str, subpath: str) -> bool:
    if ":" not in toppath:
        return (
            (toppath == subpath)
            or (subpath.startswith(toppath + "."))
            or (subpath.startswith(toppath + ":"))
        )
    else:
        return subpath.startswith(toppath + ".")


class Output:
    """A generic class for setting up citations that then will be outputted
    differently (e.g., Bibtex, Text, etc.)"""

    def __init__(self, fd, collector) -> None:
        self.fd = fd
        self.collector = collector

    def _get_collated_citations(
        self, tags: list[str] | None = None, all_: bool | None = None
    ) -> tuple[
        dict[str, list[Citation]], dict[str, list[Citation]], dict[str, list[Citation]]
    ]:
        """Given all the citations, filter only those that the user wants and
        those that were actually used"""
        if not tags:
            env = os.environ.get(
                "DUECREDIT_REPORT_TAGS",
                "reference-implementation,implementation,dataset",
            )
            assert type(env) is str
            tags = env.split(",")
        if all_ is None:
            # consult env var
            env = os.environ.get("DUECREDIT_REPORT_ALL", "").lower()
            assert type(env) is str
            all_ = env in {"1", "true", "yes", "on"}
        tagset = set(tags)

        citations = self.collector.citations
        if tagset != {"*"}:
            # Filter out citations based on tags
            citations = {
                k: c for k, c in citations.items() if tagset.intersection(c.tags)
            }

        packages = defaultdict(list)
        modules = defaultdict(list)
        objects = defaultdict(list)

        # store the citations according to their path and divide them into
        # the right level
        for (path, _entry_key), citation in citations.items():
            if ":" in path:
                objects[path].append(citation)
            elif "." in path:
                modules[path].append(citation)
            else:
                packages[path].append(citation)

        # now we need to filter out the packages that don't have modules
        # or objects cited, or are specifically requested
        cited_packages = list(packages)
        cited_modobj = list(modules) + list(objects)
        for package in cited_packages:
            package_citations = packages[package]
            if (
                all_
                or any(
                    filter(lambda x: x.cite_module, package_citations)  # type: ignore
                )
                or any(
                    filter(lambda x: _is_contained(package, x), cited_modobj)  # type: ignore
                )
            ):
                continue
            else:
                # we don't need it
                del packages[package]

        return packages, modules, objects

    def dump(self, tags=None) -> None:
        raise NotImplementedError


class TextOutput(Output):
    def __init__(self, fd, collector, style=None) -> None:
        super().__init__(fd, collector)
        self.style = style
        if "DUECREDIT_STYLE" in os.environ.keys():
            self.style = os.environ["DUECREDIT_STYLE"]
        else:
            self.style = "harvard1"

    @staticmethod
    def _format_citations(citations, citation_nr) -> str:
        descriptions = map(str, {str(r.description) for r in citations})
        versions = map(str, {str(r.version) for r in citations})
        refnrs = map(str, [citation_nr[c.entry.key] for c in citations])
        path = citations[0].path

        return "- {} / {} (v {}) [{}]\n".format(
            ", ".join(descriptions), path, ", ".join(versions), ", ".join(refnrs)
        )

    def dump(self, tags=None) -> None:
        # get 'model' of citations
        packages, modules, objects = self._get_collated_citations(tags)
        # put everything into a single dict
        pmo = {}
        pmo.update(packages)
        pmo.update(modules)
        pmo.update(objects)

        # get all the paths
        paths = sorted(list(pmo))
        # get all the entry_keys in order
        entry_keys = [c.entry.key for p in paths for c in pmo[p]]
        # make a dictionary entry_key -> citation_nr
        citation_nr = defaultdict(int)
        refnr = 1
        for entry_key in entry_keys:
            if entry_key not in citation_nr:
                citation_nr[entry_key] = refnr
                refnr += 1

        self.fd.write("\nDueCredit Report:\n")
        start_refnr = 1
        for path in paths:
            # since they're lexicographically sorted by path, dependencies
            # should be maintained
            cites = pmo[path]
            if ":" in path or "." in path:
                self.fd.write("  ")
            self.fd.write(self._format_citations(cites, citation_nr))
            start_refnr += len(cites)

        # Print out some stats
        stats = [
            (len(packages), "package"),
            (len(modules), "module"),
            (len(objects), "function"),
        ]
        for n, cit_type in stats:
            self.fd.write(
                "\n{} {} cited".format(n, cit_type if n == 1 else cit_type + "s")
            )
        # now print out references
        printed_keys = []
        if len(pmo) > 0:
            self.fd.write("\n\nReferences\n" + "-" * 10 + "\n")
            for path in paths:
                for cit in pmo[path]:
                    # 'import Citation / assert type(cit) is Citation' would pollute environment
                    ek = cit.entry.key  # type: ignore
                    if ek not in printed_keys:
                        self.fd.write(f"\n[{citation_nr[ek]}] ")
                        self.fd.write(get_text_rendering(cit.entry, style=self.style))
                        printed_keys.append(ek)
            self.fd.write("\n")


def get_text_rendering(entry: DueCreditEntry, style: str = "harvard1") -> str:
    if isinstance(entry, Doi):
        return format_bibtex(get_bibtex_rendering(entry), style=style)
    elif isinstance(entry, BibTeX):
        return format_bibtex(entry, style=style)
    elif isinstance(entry, Text):
        return entry.format()
    elif isinstance(entry, Url):
        return f"URL: {entry.format()}"
    else:
        return str(entry)


def get_bibtex_rendering(entry: DueCreditEntry) -> BibTeX:
    if isinstance(entry, Doi):
        return BibTeX(import_doi(entry.doi))
    elif isinstance(entry, BibTeX):
        return entry
    else:
        raise ValueError("Have no clue how to get bibtex out of %s" % entry)


def condition_bibtex(bibtex: str) -> bytes:
    """Given a bibtex entry, "condition" it for processing with citeproc

    Primarily a set of workarounds for either non-standard BibTeX entries
    or citeproc bugs
    """
    # XXX: workaround atm to fix zenodo bibtexs, convert @data to @misc
    # and also ; into and
    if bibtex.startswith("@data"):
        bibtex = bibtex.replace("@data", "@misc", 1)
        bibtex = bibtex.replace(";", " and")
    bibtex = bibtex.replace("\u2013", "--") + "\n"
    # workaround for citeproc 0.3.0 failing to parse a single page pages field
    # as for BIDS paper.  Workaround to add trailing + after pages number
    # related issue asking for a new release: https://github.com/brechtm/citeproc-py/issues/72
    bibtex = re.sub(r'(pages\s*=\s*["{]\d+)(["}])', r"\1+\2", bibtex)
    # partial workaround for citeproc failing to parse page numbers when they contain non-numeric characters
    # remove opening letter, e.g. 'S123' -> '123'
    # related issue: https://github.com/brechtm/citeproc-py/issues/74
    bibtex = re.sub(r'(pages\s*=\s*["{])([a-zA-Z])', r"\g<1>", bibtex)
    return bibtex.encode("utf-8")


def format_bibtex(bibtex_entry: BibTeX, style: str = "harvard1") -> str:
    try:
        import citeproc as cp
        from citeproc.source.bibtex import BibTeX as cpBibTeX
    except ImportError as e:
        raise RuntimeError(
            "For formatted output we need citeproc and all of its dependencies "
            "(such as lxml) but there is a problem while importing citeproc: %s"
            % str(e)
        )
    decode_exceptions: tuple[type[Exception], ...]
    try:
        from citeproc.source.bibtex.bibparse import BibTeXDecodeError

        decode_exceptions = (UnicodeDecodeError, BibTeXDecodeError)
    except ImportError:
        # this version doesn't yet have this exception defined
        decode_exceptions = (UnicodeDecodeError,)
    key = bibtex_entry.get_key()
    # need to save it temporarily to use citeproc-py
    fname = tempfile.mktemp(suffix=".bib")
    try:
        with open(fname, "wb") as f:
            f.write(condition_bibtex(bibtex_entry.rawentry))
        # We need to avoid cpBibTex spitting out warnings
        old_filters = warnings.filters[:]  # store a copy of filters
        warnings.simplefilter("ignore", UserWarning)
        try:
            try:
                bib_source = cpBibTeX(fname)
            except decode_exceptions:
                # So .bib must be having UTF-8 characters.  With
                # a recent (not yet released past v0.3.0-68-g9800dad
                # we should be able to provide encoding argument
                bib_source = cpBibTeX(fname, encoding="utf-8")
        except Exception as e:
            msg = "Failed to process BibTeX file {}: {}.".format(fname, e)
            if "unexpected keyword argument" in str(e):
                citeproc_version = external_versions["citeproc"]
                if isinstance(citeproc_version, Version) and citeproc_version < Version(
                    "0.4"
                ):
                    err = "need a newer citeproc-py >= 0.4.0"
                    msg += " You might just " + err
            else:
                err = str(e)
            lgr.error(msg)
            return "ERRORED: %s" % err
        finally:
            # return warnings back
            warnings.filters = old_filters
        bib_style = cp.CitationStylesStyle(style, validate=False)
        # TODO: specify which tags of formatter we want
        bibliography = cp.CitationStylesBibliography(
            bib_style, bib_source, cp.formatter.plain
        )
        citation = cp.Citation([cp.CitationItem(key)])
        bibliography.register(citation)
    finally:
        if not os.environ.get("DUECREDIT_KEEPTEMP"):
            for i in range(50):
                try:
                    os.unlink(fname)
                except OSError:
                    if i < 49:
                        time.sleep(0.1)
                        continue
                    else:
                        raise
                break

    biblio_out = bibliography.bibliography()
    assert len(biblio_out) == 1
    biblio_out = "".join(biblio_out[0])
    return biblio_out  # if biblio_out else str(bibtex_entry)


# TODO: harmonize order of arguments
class PickleOutput:
    def __init__(self, collector, fn=DUECREDIT_FILE) -> None:
        self.collector = collector
        self.fn = fn

    def dump(self) -> None:
        with open(self.fn, "wb") as f:
            pickle.dump(self.collector, f)

    @classmethod
    def load(cls, filename: str = DUECREDIT_FILE) -> Any:
        with open(filename, "rb") as f:
            return pickle.load(f)


class BibTeXOutput(Output):
    def __init__(self, fd, collector) -> None:
        super().__init__(fd, collector)

    def dump(self, tags=None) -> None:
        packages, modules, objects = self._get_collated_citations(tags)
        # get all the citations in order
        pmo = {}
        pmo.update(packages)
        pmo.update(modules)
        pmo.update(objects)

        # get all the paths
        paths = sorted(list(pmo))

        entries = []
        for path in paths:
            for c in pmo[path]:
                if c.entry not in entries:
                    entries.append(c.entry)

        for entry in entries:
            try:
                bibtex = get_bibtex_rendering(entry)
            except Exception:
                lgr.warning("Failed to generate BibTeX for %s", entry)
                continue
            self.fd.write(bibtex.rawentry + "\n")


def load_due(filename: str) -> Any:
    return PickleOutput.load(filename)
