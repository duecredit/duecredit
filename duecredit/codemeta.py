# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
Export duecredit citations to CodeMeta (https://codemeta.github.io/) format.

CodeMeta is a standardized software metadata schema that builds on schema.org
and provides crosswalks to other metadata schemas used in software citation.

This module provides functionality to export duecredit's collected citations
to CodeMeta-compliant JSON-LD format.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

from .entries import BibTeX, Doi, DueCreditEntry, Text, Url
from .io import Output

if TYPE_CHECKING:
    from collections.abc import Callable

    from .collector import Citation, DueCreditCollector

CODEMETA_CONTEXT = "https://doi.org/10.5063/schema/codemeta-2.0"

#: BibTeX entry types mapped to schema.org types
#: (anything unlisted falls back to ScholarlyArticle)
BIBTEX_TYPE_MAPPING = {
    "article": "ScholarlyArticle",
    "book": "Book",
    "inproceedings": "ScholarlyArticle",
    "proceedings": "ScholarlyArticle",
    "incollection": "Chapter",
    "inbook": "Chapter",
    "phdthesis": "Thesis",
    "mastersthesis": "Thesis",
    "techreport": "Report",
    "manual": "TechArticle",
    "misc": "CreativeWork",
    "unpublished": "CreativeWork",
    "data": "Dataset",
}

#: BibTeX fields copied verbatim into the schema.org object
_BIBTEX_FIELD_MAPPING = (
    ("year", "datePublished"),
    ("url", "url"),
    ("pages", "pagination"),
    ("abstract", "abstract"),
)


def parse_bibtex_field(bibtex: str, field: str) -> str | None:
    """Extract a field value from a BibTeX entry.

    Handles ``field = {value}`` (with one level of nested braces),
    ``field = "value"``, and bare ``field = value`` forms.  Whitespace in
    multi-line values is normalized to single spaces.

    Parameters
    ----------
    bibtex : str
        The raw BibTeX string
    field : str
        The field name to extract (case-insensitive)

    Returns
    -------
    str or None
        The field value if found, None otherwise
    """
    pattern = (
        rf"\b{re.escape(field)}\s*=\s*"
        r"(?:\{((?:[^{}]|\{[^{}]*\})*)\}"  # {value}, one nesting level
        r'|"([^"]*)"'  # "value"
        r"|([^\s,}]+))"  # bare value
    )
    match = re.search(pattern, bibtex, re.IGNORECASE)
    if not match:
        return None
    value = next(g for g in match.groups() if g is not None)
    return " ".join(value.split())


def parse_bibtex_type(bibtex: str) -> str | None:
    """Extract the entry type (article, book, etc.) from a BibTeX entry."""
    match = re.match(r"\s*@(\w+)\s*\{", bibtex, re.IGNORECASE)
    return match.group(1).lower() if match else None


def parse_authors(author_string: str | None) -> list[dict[str, Any]]:
    """Parse a BibTeX author string into schema.org Person objects.

    Parameters
    ----------
    author_string : str or None
        Author string, typically in "Last, First and Last2, First2" format

    Returns
    -------
    list of dict
        List of schema.org Person dictionaries
    """
    if not author_string:
        return []

    authors = []
    # Split by " and " (BibTeX standard separator)
    for raw_part in re.split(r"\s+and\s+", author_string, flags=re.IGNORECASE):
        part = raw_part.strip()
        if not part:
            continue

        person: dict[str, Any] = {"@type": "Person"}
        if "," in part:
            # "Last, First" format
            family, given = part.split(",", 1)
            person["familyName"] = family.strip()
            person["givenName"] = given.strip()
        else:
            # "First [Middle ...] Last" format, or a mononym
            names = part.split()
            if len(names) == 1:
                person["name"] = names[0]
            else:
                person["givenName"] = " ".join(names[:-1])
                person["familyName"] = names[-1]
        authors.append(person)

    return authors


def _doi_refs(doi: str) -> dict[str, Any]:
    """schema.org ``@id`` and ``identifier`` properties for a DOI."""
    return {
        "@id": f"https://doi.org/{doi}",
        "identifier": [{"@type": "PropertyValue", "propertyID": "doi", "value": doi}],
    }


def bibtex_to_codemeta(entry: BibTeX) -> dict[str, Any]:
    """Convert a BibTeX entry to a schema.org object (ScholarlyArticle, Book, ...)."""
    bibtex = entry.rawentry
    bib_type = parse_bibtex_type(bibtex) or ""
    result: dict[str, Any] = {
        "@type": BIBTEX_TYPE_MAPPING.get(bib_type, "ScholarlyArticle")
    }

    title = parse_bibtex_field(bibtex, "title")
    if title:
        # Drop BibTeX protection braces, e.g. {DNA} -> DNA
        result["name"] = re.sub(r"[{}]", "", title)

    authors = parse_authors(parse_bibtex_field(bibtex, "author"))
    if authors:
        result["author"] = authors

    for bib_field, schema_property in _BIBTEX_FIELD_MAPPING:
        value = parse_bibtex_field(bibtex, bib_field)
        if value:
            result[schema_property] = value

    doi = parse_bibtex_field(bibtex, "doi")
    if doi:
        result.update(_doi_refs(doi))

    journal = parse_bibtex_field(bibtex, "journal")
    if journal:
        # Nest as issue > volume > journal, innermost last
        part: dict[str, Any] = {"@type": "Periodical", "name": journal}
        volume = parse_bibtex_field(bibtex, "volume")
        if volume:
            part = {
                "@type": "PublicationVolume",
                "volumeNumber": volume,
                "isPartOf": part,
            }
        number = parse_bibtex_field(bibtex, "number")
        if number:
            part = {
                "@type": "PublicationIssue",
                "issueNumber": number,
                "isPartOf": part,
            }
        result["isPartOf"] = part

    publisher = parse_bibtex_field(bibtex, "publisher")
    if publisher:
        result["publisher"] = {"@type": "Organization", "name": publisher}

    return result


def doi_to_codemeta(entry: Doi) -> dict[str, Any]:
    """Convert a DOI entry to a schema.org CreativeWork with the DOI as identifier."""
    return {"@type": "CreativeWork", **_doi_refs(entry.doi)}


def url_to_codemeta(entry: Url) -> dict[str, Any]:
    """Convert a URL entry to a schema.org WebPage."""
    return {"@type": "WebPage", "@id": entry.url, "url": entry.url}


def text_to_codemeta(entry: Text) -> dict[str, Any]:
    """Convert a Text entry to a schema.org CreativeWork."""
    return {"@type": "CreativeWork", "name": entry.rawentry}


#: (entry class, converter) pairs checked in order by entry_to_codemeta;
#: subclasses must be listed before their base classes
_ENTRY_CONVERTERS: tuple[
    tuple[type[DueCreditEntry], Callable[[Any], dict[str, Any]]], ...
] = (
    (BibTeX, bibtex_to_codemeta),
    (Doi, doi_to_codemeta),
    (Url, url_to_codemeta),
    (Text, text_to_codemeta),
)


def entry_to_codemeta(entry: DueCreditEntry) -> dict[str, Any]:
    """Convert any DueCreditEntry to a schema.org object."""
    for entry_class, converter in _ENTRY_CONVERTERS:
        if isinstance(entry, entry_class):
            return converter(entry)
    return {"@type": "CreativeWork", "name": str(entry.rawentry)}


def citation_to_codemeta(citation: Citation) -> dict[str, Any]:
    """Convert a Citation (entry + context) to a schema.org object."""
    result = entry_to_codemeta(citation.entry)
    if citation.description and "abstract" not in result:
        result["description"] = citation.description
    return result


def _software_requirement(path: str, citations: list[Citation]) -> dict[str, Any]:
    """schema.org SoftwareApplication describing a cited package."""
    requirement: dict[str, Any] = {
        "@type": "SoftwareApplication",
        "identifier": path,
        "name": path,
    }
    if citations and citations[0].version:
        requirement["version"] = citations[0].version
    return requirement


def collector_to_codemeta(
    collector: DueCreditCollector,
    name: str | None = None,
    version: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Convert a DueCreditCollector to CodeMeta format.

    Parameters
    ----------
    collector : DueCreditCollector
        The collector containing citations to export
    name : str, optional
        Name of the software project
    version : str, optional
        Version of the software
    description : str, optional
        Description of the software
    tags : list of str, optional
        Citation tags to filter by

    Returns
    -------
    dict
        A CodeMeta (JSON-LD) compatible dictionary
    """
    codemeta: dict[str, Any] = {
        "@context": CODEMETA_CONTEXT,
        "@type": "SoftwareSourceCode",
        "name": name,
        "version": version,
        "description": description,
    }
    # drop the properties which were not provided
    codemeta = {prop: value for prop, value in codemeta.items() if value}

    # Reuse the Output helper for consistent tag filtering and collation
    packages, modules, objects = Output(None, collector)._get_collated_citations(
        tags=tags
    )

    # Deduplicate citations by entry key across all paths
    all_citations: dict[str, Citation] = {
        citation.entry.key: citation
        for path_citations in (packages, modules, objects)
        for citations in path_citations.values()
        for citation in citations
    }
    if all_citations:
        codemeta["citation"] = [
            citation_to_codemeta(citation) for citation in all_citations.values()
        ]

    if packages:
        codemeta["softwareRequirements"] = [
            _software_requirement(path, citations)
            for path, citations in packages.items()
        ]

    return codemeta


class CodeMetaOutput(Output):
    """Output handler for CodeMeta (JSON-LD) format."""

    def __init__(
        self,
        fd,
        collector: DueCreditCollector,
        name: str | None = None,
        version: str | None = None,
        description: str | None = None,
        indent: int = 2,
    ) -> None:
        super().__init__(fd, collector)
        self.name = name
        self.version = version
        self.description = description
        self.indent = indent

    def dump(self, tags: list[str] | None = None) -> None:
        """Write CodeMeta JSON-LD to the file descriptor.

        Parameters
        ----------
        tags : list of str, optional
            Citation tags to filter by
        """
        codemeta = collector_to_codemeta(
            self.collector,
            name=self.name,
            version=self.version,
            description=self.description,
            tags=tags,
        )
        self.fd.write(json.dumps(codemeta, indent=self.indent))
        self.fd.write("\n")
