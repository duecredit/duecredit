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
    from .collector import Citation, DueCreditCollector


def parse_bibtex_field(bibtex: str, field: str) -> str | None:
    """Extract a field value from a BibTeX entry.

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
    # Match field = {value} or field = "value" or field = value
    pattern = rf'{field}\s*=\s*[\{{""]?([^{{}}"]+)[\}}""]?'
    match = re.search(pattern, bibtex, re.IGNORECASE)
    if match:
        return match.group(1).strip().rstrip(",")
    return None


def parse_bibtex_type(bibtex: str) -> str | None:
    """Extract the entry type from a BibTeX entry.

    Parameters
    ----------
    bibtex : str
        The raw BibTeX string

    Returns
    -------
    str or None
        The entry type (article, book, etc.) if found
    """
    match = re.match(r"\s*@(\w+)\s*\{", bibtex, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None


def parse_authors(author_string: str | None) -> list[dict[str, Any]]:
    """Parse author string into list of schema.org Person objects.

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
    parts = re.split(r"\s+and\s+", author_string, flags=re.IGNORECASE)

    for raw_part in parts:
        part = raw_part.strip()
        if not part:
            continue

        person: dict[str, Any] = {"@type": "Person"}

        # Try to parse "Last, First" format
        if "," in part:
            names = part.split(",", 1)
            person["familyName"] = names[0].strip()
            if len(names) > 1:
                person["givenName"] = names[1].strip()
        else:
            # Assume "First Last" format
            names = part.split()
            if len(names) == 1:
                person["name"] = names[0]
            elif len(names) >= 2:
                person["givenName"] = " ".join(names[:-1])
                person["familyName"] = names[-1]

        authors.append(person)

    return authors


def entry_to_codemeta(entry: DueCreditEntry) -> dict[str, Any]:
    """Convert a DueCreditEntry to a CodeMeta-compatible schema.org object.

    Parameters
    ----------
    entry : DueCreditEntry
        The entry to convert

    Returns
    -------
    dict
        A schema.org compatible dictionary
    """
    if isinstance(entry, BibTeX):
        return bibtex_to_codemeta(entry)
    elif isinstance(entry, Doi):
        return doi_to_codemeta(entry)
    elif isinstance(entry, Url):
        return url_to_codemeta(entry)
    elif isinstance(entry, Text):
        return text_to_codemeta(entry)
    else:
        return {"@type": "CreativeWork", "name": str(entry.rawentry)}


def bibtex_to_codemeta(entry: BibTeX) -> dict[str, Any]:
    """Convert a BibTeX entry to a CodeMeta-compatible schema.org object.

    Parameters
    ----------
    entry : BibTeX
        The BibTeX entry to convert

    Returns
    -------
    dict
        A schema.org ScholarlyArticle or appropriate type
    """
    bibtex = entry.rawentry
    bib_type = parse_bibtex_type(bibtex)

    # Map BibTeX types to schema.org types
    type_mapping = {
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

    schema_type = type_mapping.get(bib_type or "", "ScholarlyArticle")

    result: dict[str, Any] = {"@type": schema_type}

    # Extract and add standard fields
    title = parse_bibtex_field(bibtex, "title")
    if title:
        # Clean up BibTeX braces in title
        title = re.sub(r"[{}]", "", title)
        result["name"] = title

    authors = parse_authors(parse_bibtex_field(bibtex, "author"))
    if authors:
        result["author"] = authors

    year = parse_bibtex_field(bibtex, "year")
    if year:
        result["datePublished"] = year

    doi = parse_bibtex_field(bibtex, "doi")
    if doi:
        result["@id"] = f"https://doi.org/{doi}"
        result["identifier"] = [
            {"@type": "PropertyValue", "propertyID": "doi", "value": doi}
        ]

    url = parse_bibtex_field(bibtex, "url")
    if url:
        result["url"] = url

    journal = parse_bibtex_field(bibtex, "journal")
    volume = parse_bibtex_field(bibtex, "volume")
    number = parse_bibtex_field(bibtex, "number")
    pages = parse_bibtex_field(bibtex, "pages")

    if journal:
        issue_info: dict[str, Any] = {"@type": "Periodical", "name": journal}
        if volume:
            volume_info: dict[str, Any] = {
                "@type": "PublicationVolume",
                "volumeNumber": volume,
            }
            volume_info["isPartOf"] = issue_info
            issue_info = volume_info
        if number:
            issue_num: dict[str, Any] = {
                "@type": "PublicationIssue",
                "issueNumber": number,
            }
            issue_num["isPartOf"] = issue_info
            issue_info = issue_num
        result["isPartOf"] = issue_info

    if pages:
        result["pagination"] = pages

    publisher = parse_bibtex_field(bibtex, "publisher")
    if publisher:
        result["publisher"] = {"@type": "Organization", "name": publisher}

    abstract = parse_bibtex_field(bibtex, "abstract")
    if abstract:
        result["abstract"] = abstract

    return result


def doi_to_codemeta(entry: Doi) -> dict[str, Any]:
    """Convert a DOI entry to a CodeMeta-compatible schema.org object.

    Parameters
    ----------
    entry : Doi
        The DOI entry to convert

    Returns
    -------
    dict
        A schema.org CreativeWork dictionary with DOI as identifier
    """
    return {
        "@type": "CreativeWork",
        "@id": f"https://doi.org/{entry.doi}",
        "identifier": [
            {"@type": "PropertyValue", "propertyID": "doi", "value": entry.doi}
        ],
    }


def url_to_codemeta(entry: Url) -> dict[str, Any]:
    """Convert a URL entry to a CodeMeta-compatible schema.org object.

    Parameters
    ----------
    entry : Url
        The URL entry to convert

    Returns
    -------
    dict
        A schema.org WebPage dictionary
    """
    return {"@type": "WebPage", "@id": entry.url, "url": entry.url}


def text_to_codemeta(entry: Text) -> dict[str, Any]:
    """Convert a Text entry to a CodeMeta-compatible schema.org object.

    Parameters
    ----------
    entry : Text
        The Text entry to convert

    Returns
    -------
    dict
        A schema.org CreativeWork dictionary
    """
    return {"@type": "CreativeWork", "name": entry.rawentry}


def citation_to_codemeta(citation: Citation) -> dict[str, Any]:
    """Convert a Citation to CodeMeta format including the entry and metadata.

    Parameters
    ----------
    citation : Citation
        The citation to convert

    Returns
    -------
    dict
        A schema.org compatible dictionary representing the citation
    """
    result = entry_to_codemeta(citation.entry)

    # Add description as about/abstract if not already present
    if citation.description and "abstract" not in result:
        result["description"] = citation.description

    return result


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
        "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
        "@type": "SoftwareSourceCode",
    }

    if name:
        codemeta["name"] = name
    if version:
        codemeta["version"] = version
    if description:
        codemeta["description"] = description

    # Get citations using the Output helper for consistent filtering
    output = Output(None, collector)
    packages, modules, objects = output._get_collated_citations(tags=tags)

    # Combine all citations
    all_citations: dict[str, Citation] = {}
    for path_citations in [packages, modules, objects]:
        for citations in path_citations.values():
            for citation in citations:
                # Use entry key to deduplicate
                all_citations[citation.entry.key] = citation

    # Convert to CodeMeta citation format
    if all_citations:
        codemeta["citation"] = [
            citation_to_codemeta(citation) for citation in all_citations.values()
        ]

    # Add software requirements/dependencies based on packages
    if packages:
        codemeta["softwareRequirements"] = [
            {
                "@type": "SoftwareApplication",
                "identifier": path,
                "name": path,
                "version": (
                    citations[0].version if citations and citations[0].version else None
                ),
            }
            for path, citations in packages.items()
        ]
        # Remove None versions
        for req in codemeta["softwareRequirements"]:
            if req.get("version") is None:
                del req["version"]

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
        """Initialize CodeMeta output handler.

        Parameters
        ----------
        fd : file-like
            File descriptor to write to
        collector : DueCreditCollector
            The collector containing citations
        name : str, optional
            Name of the software project
        version : str, optional
            Version of the software
        description : str, optional
            Description of the software
        indent : int, optional
            JSON indentation level (default: 2)
        """
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
