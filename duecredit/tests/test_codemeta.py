# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Tests for CodeMeta export functionality."""

from __future__ import annotations

from io import StringIO
import json

from ..codemeta import (
    CodeMetaOutput,
    bibtex_to_codemeta,
    collector_to_codemeta,
    doi_to_codemeta,
    entry_to_codemeta,
    parse_authors,
    parse_bibtex_field,
    parse_bibtex_type,
    text_to_codemeta,
    url_to_codemeta,
)
from ..collector import DueCreditCollector
from ..entries import BibTeX, Doi, Text, Url

# Sample BibTeX for testing
_sample_bibtex = """
@ARTICLE{XXX0,
  author = {Halchenko, Yaroslav O. and Hanke, Michael},
  title = {Open is not enough. Let{'}s take the next step: An integrated, community-driven
    computing platform for neuroscience},
  journal = {Frontiers in Neuroinformatics},
  year = {2012},
  volume = {6},
  number = {00022},
  doi = {10.3389/fninf.2012.00022},
  issn = {1662-5196},
}
"""

_sample_bibtex_book = """
@BOOK{TestBook,
  author = {Smith, John and Doe, Jane},
  title = {A Great Book Title},
  publisher = {Academic Press},
  year = {2020},
}
"""


class TestParseBibtex:
    """Tests for BibTeX parsing functions."""

    def test_parse_bibtex_type_article(self) -> None:
        assert parse_bibtex_type(_sample_bibtex) == "article"

    def test_parse_bibtex_type_book(self) -> None:
        assert parse_bibtex_type(_sample_bibtex_book) == "book"

    def test_parse_bibtex_type_none(self) -> None:
        assert parse_bibtex_type("not a bibtex") is None

    def test_parse_bibtex_field_author(self) -> None:
        result = parse_bibtex_field(_sample_bibtex, "author")
        assert result is not None
        assert "Halchenko" in result
        assert "Hanke" in result

    def test_parse_bibtex_field_year(self) -> None:
        result = parse_bibtex_field(_sample_bibtex, "year")
        assert result == "2012"

    def test_parse_bibtex_field_doi(self) -> None:
        result = parse_bibtex_field(_sample_bibtex, "doi")
        assert result == "10.3389/fninf.2012.00022"

    def test_parse_bibtex_field_missing(self) -> None:
        result = parse_bibtex_field(_sample_bibtex, "nonexistent")
        assert result is None


class TestParseAuthors:
    """Tests for author string parsing."""

    def test_parse_authors_last_first(self) -> None:
        authors = parse_authors("Smith, John and Doe, Jane")
        assert len(authors) == 2
        assert authors[0]["familyName"] == "Smith"
        assert authors[0]["givenName"] == "John"
        assert authors[1]["familyName"] == "Doe"
        assert authors[1]["givenName"] == "Jane"

    def test_parse_authors_first_last(self) -> None:
        authors = parse_authors("John Smith")
        assert len(authors) == 1
        assert authors[0]["familyName"] == "Smith"
        assert authors[0]["givenName"] == "John"

    def test_parse_authors_single_name(self) -> None:
        authors = parse_authors("Mononym")
        assert len(authors) == 1
        assert authors[0]["name"] == "Mononym"

    def test_parse_authors_empty(self) -> None:
        assert parse_authors(None) == []
        assert parse_authors("") == []


class TestEntryToCodemeta:
    """Tests for converting DueCreditEntry objects to CodeMeta."""

    def test_bibtex_entry(self) -> None:
        entry = BibTeX(_sample_bibtex)
        result = entry_to_codemeta(entry)

        assert result["@type"] == "ScholarlyArticle"
        assert "name" in result  # title
        assert "author" in result
        assert len(result["author"]) == 2
        assert result["datePublished"] == "2012"
        assert "@id" in result  # DOI URL
        assert "https://doi.org/10.3389/fninf.2012.00022" == result["@id"]

    def test_bibtex_book(self) -> None:
        entry = BibTeX(_sample_bibtex_book)
        result = bibtex_to_codemeta(entry)

        assert result["@type"] == "Book"
        assert result["name"] == "A Great Book Title"
        assert "publisher" in result
        assert result["publisher"]["name"] == "Academic Press"

    def test_doi_entry(self) -> None:
        entry = Doi("10.1234/test.doi")
        result = doi_to_codemeta(entry)

        assert result["@type"] == "CreativeWork"
        assert result["@id"] == "https://doi.org/10.1234/test.doi"
        assert result["identifier"][0]["value"] == "10.1234/test.doi"

    def test_url_entry(self) -> None:
        entry = Url("https://example.com/software")
        result = url_to_codemeta(entry)

        assert result["@type"] == "WebPage"
        assert result["@id"] == "https://example.com/software"
        assert result["url"] == "https://example.com/software"

    def test_text_entry(self) -> None:
        entry = Text("A simple text citation")
        result = text_to_codemeta(entry)

        assert result["@type"] == "CreativeWork"
        assert result["name"] == "A simple text citation"


class TestCollectorToCodemeta:
    """Tests for converting DueCreditCollector to CodeMeta."""

    def test_empty_collector(self) -> None:
        collector = DueCreditCollector()
        result = collector_to_codemeta(collector, name="Test Software")

        assert result["@context"] == "https://doi.org/10.5063/schema/codemeta-2.0"
        assert result["@type"] == "SoftwareSourceCode"
        assert result["name"] == "Test Software"
        assert "citation" not in result  # No citations yet

    def test_collector_with_citations(self) -> None:
        collector = DueCreditCollector()
        entry = BibTeX(_sample_bibtex)
        collector.cite(entry, path="package", cite_module=True)

        result = collector_to_codemeta(
            collector, name="MyPackage", version="1.0.0", description="A great package"
        )

        assert result["name"] == "MyPackage"
        assert result["version"] == "1.0.0"
        assert result["description"] == "A great package"
        assert "citation" in result
        assert len(result["citation"]) == 1

    def test_collector_with_multiple_citations(self) -> None:
        collector = DueCreditCollector()
        entry1 = BibTeX(_sample_bibtex)
        entry2 = Doi("10.1234/example")

        collector.cite(entry1, path="package", cite_module=True)
        collector.cite(entry2, path="package.module")

        result = collector_to_codemeta(collector, tags=["*"])

        assert "citation" in result
        assert len(result["citation"]) == 2

    def test_collector_with_software_requirements(self) -> None:
        collector = DueCreditCollector()
        entry = BibTeX(_sample_bibtex)
        collector.cite(entry, path="numpy", cite_module=True)

        result = collector_to_codemeta(collector, tags=["*"])

        assert "softwareRequirements" in result
        assert len(result["softwareRequirements"]) == 1
        assert result["softwareRequirements"][0]["identifier"] == "numpy"


class TestCodeMetaOutput:
    """Tests for CodeMetaOutput class."""

    def test_dump_basic(self) -> None:
        collector = DueCreditCollector()
        entry = BibTeX(_sample_bibtex)
        collector.cite(entry, path="package", cite_module=True)

        strio = StringIO()
        output = CodeMetaOutput(strio, collector, name="TestPackage")
        output.dump(tags=["*"])

        result = json.loads(strio.getvalue())
        assert result["@context"] == "https://doi.org/10.5063/schema/codemeta-2.0"
        assert result["@type"] == "SoftwareSourceCode"
        assert result["name"] == "TestPackage"
        assert "citation" in result

    def test_dump_with_indent(self) -> None:
        collector = DueCreditCollector()

        strio = StringIO()
        output = CodeMetaOutput(strio, collector, name="Test", indent=4)
        output.dump()

        # Check that the output is properly indented
        value = strio.getvalue()
        assert "    " in value  # 4-space indent

    def test_dump_empty_collector(self) -> None:
        collector = DueCreditCollector()

        strio = StringIO()
        output = CodeMetaOutput(strio, collector)
        output.dump()

        result = json.loads(strio.getvalue())
        assert result["@type"] == "SoftwareSourceCode"
        assert "citation" not in result


class TestCodeMetaValidation:
    """Tests to validate CodeMeta output structure."""

    def test_codemeta_context(self) -> None:
        """Ensure we use the correct CodeMeta context."""
        collector = DueCreditCollector()
        result = collector_to_codemeta(collector)
        assert result["@context"] == "https://doi.org/10.5063/schema/codemeta-2.0"

    def test_person_structure(self) -> None:
        """Ensure Person objects have correct schema.org structure."""
        entry = BibTeX(_sample_bibtex)
        result = bibtex_to_codemeta(entry)

        for author in result["author"]:
            assert author["@type"] == "Person"
            # Should have either name or familyName
            assert "name" in author or "familyName" in author

    def test_identifier_structure(self) -> None:
        """Ensure DOI identifiers follow schema.org PropertyValue structure."""
        entry = Doi("10.1234/test")
        result = doi_to_codemeta(entry)

        assert "identifier" in result
        assert result["identifier"][0]["@type"] == "PropertyValue"
        assert result["identifier"][0]["propertyID"] == "doi"
