# ex: set sts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
from __future__ import annotations

from io import StringIO
import os
import pickle
import random
import re
from typing import Any

import pytest
from pytest import MonkeyPatch

import duecredit.io

from .test_collector import _sample_bibtex, _sample_bibtex2, _sample_doi
from ..collector import CitationKey, DueCreditCollector
from ..entries import BibTeX, Doi, Text, Url
from ..io import (
    BibTeXOutput,
    Output,
    PickleOutput,
    TextOutput,
    _is_contained,
    format_bibtex,
    get_text_rendering,
    import_doi,
)

try:
    # TODO: for some reason test below started to complain that we are trying
    # to overwrite the cassette.
    #
    # import vcr

    # @vcr.use_cassette()
    def test_import_doi() -> None:
        doi_good = "10.1038/nrd842"
        assert isinstance(import_doi(doi_good, sleep=0.00001, retries=2), str)

        doi_bad = "fasljfdldaksj"
        with pytest.raises(ValueError):
            import_doi(doi_bad, sleep=0.00001, retries=2)

        doi_zenodo = "10.5281/zenodo.50186"
        assert isinstance(import_doi(doi_zenodo, sleep=0.00001, retries=2), str)

except ImportError:
    # no vcr, and that is in 2015!
    pass


def test_pickleoutput(tmpdir) -> None:
    # entry = BibTeX('@article{XXX0, ...}')
    entry = BibTeX(
        "@article{Atkins_2002,\n"
        "title=title,\n"
        "volume=1, \n"
        "url=https://doi.org/10.1038/nrd842, \n"
        "DOI=10.1038/nrd842, \n"
        "number=7, \n"
        "journal={Nat. Rev. Drug Disc.}, \n"
        "publisher={Nature Publishing Group}, \n"
        "author={Atkins, Joshua H. and Gershell, Leland J.}, \n"
        "year={2002}, \n"
        "month={Jul}, \n"
        "pages={491--492}\n}"
    )
    collector_ = DueCreditCollector()
    collector_.add(entry)
    collector_.cite(entry, path="module")

    # test it doesn't puke with an empty collector
    collectors = [collector_, DueCreditCollector()]

    tempfile = str(tmpdir.mkdir("sub").join("tempfile.txt"))

    for collector in collectors:
        pickler = PickleOutput(collector, fn=tempfile)
        assert pickler.fn == tempfile
        assert pickler.dump() is None  # type: ignore

        with open(tempfile, "rb") as f:
            collector_loaded = pickle.load(f)

        assert collector.citations.keys() == collector_loaded.citations.keys()
        # TODO: implement comparison of citations
        assert collector._entries.keys() == collector_loaded._entries.keys()
        os.unlink(tempfile)


def test_output() -> None:
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # normal use
    collector = DueCreditCollector()
    collector.cite(entry, path="package")
    collector.cite(entry, path="package.module")

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["*"])

    assert len(packages) == 1
    assert len(modules) == 1
    assert len(objects) == 0

    assert (
        packages["package"][0]
        == collector.citations[CitationKey("package", entry.get_key())]
    )
    assert (
        modules["package.module"][0]
        == collector.citations[CitationKey("package.module", entry.get_key())]
    )

    # no toppackage
    collector = DueCreditCollector()
    collector.cite(entry, path="package")
    collector.cite(entry, path="package2.module")

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["*"])

    assert len(packages) == 0
    assert len(modules) == 1
    assert len(objects) == 0

    assert (
        modules["package2.module"][0]
        == collector.citations[CitationKey("package2.module", entry.get_key())]
    )

    # toppackage because required
    collector = DueCreditCollector()
    collector.cite(entry, path="package", cite_module=True)
    collector.cite(entry, path="package2.module")

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["*"])

    assert len(packages) == 1
    assert len(modules) == 1
    assert len(objects) == 0

    assert (
        packages["package"][0]
        == collector.citations[CitationKey("package", entry.get_key())]
    )
    assert (
        modules["package2.module"][0]
        == collector.citations[CitationKey("package2.module", entry.get_key())]
    )

    # check it returns multiple entries
    collector = DueCreditCollector()
    collector.cite(entry, path="package")
    collector.cite(entry2, path="package")
    collector.cite(entry, path="package.module")

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["*"])

    assert len(packages) == 1
    assert len(packages["package"]) == 2
    assert len(modules) == 1
    assert len(objects) == 0

    # sort them in order so we know who is who
    # entry2 key is Atk...
    # entry key is XX..
    packs = sorted(packages["package"], key=lambda x: x.entry.key)

    assert packs[0] == collector.citations[CitationKey("package", entry2.get_key())]
    assert packs[1] == collector.citations[CitationKey("package", entry.get_key())]
    assert (
        modules["package.module"][0]
        == collector.citations[CitationKey("package.module", entry.get_key())]
    )

    # check that filtering works
    collector = DueCreditCollector()
    collector.cite(entry, path="package", tags=["edu"])
    collector.cite(entry2, path="package")
    collector.cite(entry, path="package.module", tags=["edu"])

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["edu"])

    assert len(packages) == 1
    assert len(packages["package"]) == 1
    assert len(modules) == 1
    assert len(objects) == 0

    assert (
        packages["package"][0]
        == collector.citations[CitationKey("package", entry.get_key())]
    )
    assert (
        modules["package.module"][0]
        == collector.citations[CitationKey("package.module", entry.get_key())]
    )


def test_output_return_all(monkeypatch: MonkeyPatch) -> None:
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # normal use
    collector = DueCreditCollector()
    collector.cite(entry, path="package")
    collector.cite(entry2, path="package2")

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["*"])
    assert not packages
    assert not modules
    assert not objects

    for flag in ["1", "True", "TRUE", "true", "on", "yes"]:
        monkeypatch.setitem(os.environ, "DUECREDIT_REPORT_ALL", flag)
        # if _all is None then get the environment
        packages, modules, objects = output._get_collated_citations(tags=["*"])
        assert len(packages) == 2
        assert not modules
        assert not objects
        # however if _all is set it shouldn't work
        packages, modules, objects = output._get_collated_citations(
            tags=["*"], all_=False
        )
        assert not packages
        assert not modules
        assert not objects


def test_output_tags(monkeypatch: MonkeyPatch) -> None:
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # normal use
    collector = DueCreditCollector()
    collector.cite(entry, path="package", cite_module=True, tags=["edu"])
    collector.cite(entry2, path="package.module", tags=["wip"])

    output = Output(None, collector)

    packages, modules, objects = output._get_collated_citations(tags=["*"])
    assert len(packages) == 1
    assert len(modules) == 1
    assert not objects

    packages, modules, objects = output._get_collated_citations()
    assert not packages
    assert not modules
    assert not objects

    for tags in ["edu", "wip", "edu,wip"]:
        monkeypatch.setitem(os.environ, "DUECREDIT_REPORT_TAGS", tags)
        # if tags is None then get the environment
        packages, modules, objects = output._get_collated_citations()
        assert len(packages) == (1 if "edu" in tags else 0)
        assert len(modules) == (1 if "wip" in tags else 0)
        assert not objects
        # however if tags is set it shouldn't work
        packages, modules, objects = output._get_collated_citations(
            tags=["implementation"]
        )
        assert not packages
        assert not modules
        assert not objects


def test_text_output() -> None:
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # in this case, since we're not citing any module or method, we shouldn't
    # output anything
    collector = DueCreditCollector()
    collector.cite(entry, path="package")

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert "0 packages cited" in value, "value was %s" % value
    assert "0 modules cited" in value, "value was %s" % value
    assert "0 functions cited" in value, "value was %s" % value

    # but it should be cited if cite_module=True
    collector = DueCreditCollector()
    collector.cite(entry, path="package", cite_module=True)

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert "1 package cited" in value, "value was %s" % value
    assert "0 modules cited" in value, "value was %s" % value
    assert "0 functions cited" in value, "value was %s" % value

    # in this case, we should be citing the package since we are also citing a
    # submodule
    collector = DueCreditCollector()
    collector.cite(entry, path="package")
    collector.cite(entry, path="package.module")

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert "1 package cited" in value, "value was %s" % value
    assert "1 module cited" in value, "value was %s" % value
    assert "0 functions cited" in value, "value was %s" % value
    assert "Halchenko, Y.O." in value, "value was %s" % value
    assert value.strip().endswith("Frontiers in Neuroinformatics, 6(22).")

    # in this case, we should be citing the package since we are also citing a
    # submodule
    collector = DueCreditCollector()
    collector.cite(entry, path="package")
    collector.cite(entry2, path="package")
    collector.cite(entry, path="package.module")

    strio = StringIO()
    TextOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert "1 package cited" in value, "value was %s" % value
    assert "1 module cited" in value, "value was %s" % value
    assert "0 functions cited" in value, "value was %s" % value
    assert "Halchenko, Y.O." in value, "value was %s" % value
    assert "[1, 2]" in value, "value was %s" % value
    assert "[3]" not in value, "value was %s" % value


def test_text_output_dump_formatting() -> None:
    due = DueCreditCollector()

    # XXX: atm just to see if it spits out stuff
    @due.dcite(
        BibTeX(_sample_bibtex),
        description="solution to life",
        path="mymodule",
        version="0.0.16",
    )
    def mymodule(arg1: Any, kwarg2: Any = "blah") -> Any:
        """docstring"""
        assert arg1 == "magical"
        assert kwarg2 == 1

        @due.dcite(
            BibTeX(_sample_bibtex2),
            description="solution to life",
            path="mymodule:myfunction",
        )
        def myfunction(arg42):
            pass

        myfunction("argh")
        return "load"

    # check we don't have anything output
    strio = StringIO()
    TextOutput(strio, due).dump(tags=["*"])
    value = strio.getvalue()
    assert "0 modules cited" in value, f"value was {value}"
    assert "0 functions cited" in value, f"value was {value}"

    # now we call it -- check it prints stuff
    strio = StringIO()
    mymodule("magical", kwarg2=1)
    TextOutput(strio, due).dump(tags=["*"])
    value = strio.getvalue()
    assert "1 package cited" in value, f"value was {value}"
    assert "1 function cited" in value, f"value was {value}"
    assert "(v 0.0.16)" in value, f"value was {value}"
    assert len(value.split("\n")) == 16, "value was {}".format(len(value.split("\n")))

    # test we get the reference numbering right
    samples_bibtex = [_generate_sample_bibtex() for x in range(6)]
    # this sucks but at the moment it's the only way to have multiple
    # references for a function

    @due.dcite(
        BibTeX(samples_bibtex[0]),
        description="another solution",
        path="myothermodule",
        version="0.0.666",
    )
    def myothermodule(arg1: Any, kwarg2: Any = "blah") -> Any:
        """docstring"""
        assert arg1 == "magical"
        assert kwarg2 == 1

        @due.dcite(
            BibTeX(samples_bibtex[1]),
            description="solution to life",
            path="myothermodule:myotherfunction",
        )
        @due.dcite(
            BibTeX(samples_bibtex[2]),
            description="solution to life",
            path="myothermodule:myotherfunction",
        )
        @due.dcite(
            BibTeX(samples_bibtex[3]),
            description="solution to life",
            path="myothermodule:myotherfunction",
        )
        @due.dcite(
            BibTeX(samples_bibtex[4]),
            description="solution to life",
            path="myothermodule:myotherfunction",
        )
        @due.dcite(
            BibTeX(samples_bibtex[5]),
            description="solution to life",
            path="myothermodule:myotherfunction",
        )
        def myotherfunction(arg42):
            pass

        myotherfunction("argh")
        return "load"

    myothermodule("magical", kwarg2=1)
    strio = StringIO()
    TextOutput(strio, due).dump(tags=["*"])
    value = strio.getvalue()
    lines = value.split("\n")

    citation_numbers: list[str] = []
    reference_numbers = []
    references = []
    for line in lines:
        match_citation = re.search(r"\[([0-9, ]+)\]$", line)
        match_reference = re.search(r"^\[([0-9])\]", line)
        if match_citation:
            citation_numbers.extend(match_citation.group(1).split(", "))
        elif match_reference:
            reference_numbers.append(match_reference.group(1))
            references.append(line.replace(match_reference.group(), ""))

    assert set(citation_numbers) == set(reference_numbers)
    assert len(set(references)) == len(set(citation_numbers))
    assert len(citation_numbers) == 8
    # verify that we have returned to previous state of filters
    import warnings

    assert ("ignore", None, UserWarning, None, 0) not in warnings.filters


def test_bibtex_output() -> None:
    entry = BibTeX(_sample_bibtex)
    entry2 = BibTeX(_sample_bibtex2)

    # in this case, since we're not citing any module or method, we shouldn't
    # output anything
    collector = DueCreditCollector()
    collector.cite(entry, path="package")

    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert value == "", f"Value was {value}"

    # impose citing
    collector = DueCreditCollector()
    collector.cite(entry, path="package", cite_module=True)

    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert value.strip() == _sample_bibtex.strip(), f"Value was {value}"

    # impose filtering
    collector = DueCreditCollector()
    collector.cite(entry, path="package", cite_module=True, tags=["edu"])
    collector.cite(entry2, path="package.module")

    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=["edu"])
    value = strio.getvalue()
    assert value.strip() == _sample_bibtex.strip(), f"Value was {value}"

    # no filtering
    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    assert (
        value.strip() == _sample_bibtex.strip() + _sample_bibtex2.rstrip()
    ), f"Value was {value}"

    # check the we output only unique bibtex entries
    collector.cite(entry2, path="package")
    strio = StringIO()
    BibTeXOutput(strio, collector).dump(tags=["*"])
    value = strio.getvalue()
    value_ = sorted(value.strip().split("\n"))
    bibtex = sorted((_sample_bibtex.strip() + _sample_bibtex2.rstrip()).split("\n"))
    assert value_ == bibtex, f"Value was {value_} instead of {bibtex}"

    # assert_equal(value_, bibtex,
    #              msg='Value was {0}'.format(value_, bibtex))


def _generate_sample_bibtex() -> str:
    """
    Generate a random sample bibtex to test multiple references
    """
    letters = "abcdefghilmnopqrstuvxz"
    numbers = "0123456789"
    letters_numbers = letters + letters.upper() + numbers
    letters_numbers_spaces = letters_numbers + " "

    key = "".join(random.sample(letters_numbers, 7))
    title = "".join(random.sample(letters_numbers_spaces, 20))
    journal = "".join(random.sample(letters_numbers_spaces, 20))
    publisher = "".join(random.sample(letters_numbers_spaces, 10))
    author = (
        "".join(random.sample(letters, 6)) + ", " + "".join(random.sample(letters, 4))
    )
    year = "".join(random.sample(numbers, 4))

    elements = [
        ("title", title),
        ("journal", journal),
        ("publisher", publisher),
        ("author", author),
        ("year", year),
    ]

    sample_bibtex = "@ARTICLE{%s,\n" % key
    for string, value in elements:
        sample_bibtex += "{}={{{}}},\n".format(string, value)
    sample_bibtex += "}"
    return sample_bibtex


def test_get_text_rendering(monkeypatch: MonkeyPatch) -> None:
    # Patch bibtex_rendering
    sample_bibtex = BibTeX(_sample_bibtex)

    def get_bibtex_rendering(*_args: Any, **_kwargs: Any) -> BibTeX:
        return sample_bibtex

    monkeypatch.setattr(duecredit.io, "get_bibtex_rendering", get_bibtex_rendering)

    # Patch format_bibtex
    fmt_args = {}

    def format_bibtex(entry: str, style: str) -> None:
        fmt_args["entry"] = entry
        fmt_args["style"] = style

    monkeypatch.setattr(duecredit.io, "format_bibtex", format_bibtex)

    # test if bibtex type is passed
    bibtex_output = get_text_rendering(sample_bibtex)
    assert fmt_args["entry"] == sample_bibtex
    assert fmt_args["style"] == "harvard1"
    fmt_args.clear()

    # test if doi type is passed
    doi_output = get_text_rendering(Doi(_sample_doi))
    assert fmt_args["entry"] == sample_bibtex
    assert fmt_args["style"] == "harvard1"

    assert bibtex_output == doi_output


def test_text_text_rendering() -> None:
    text = "I am so free"
    assert get_text_rendering(Text(text)) == text


def test_url_text_rendering() -> None:
    url = "http://example.com"
    assert get_text_rendering(Url(url)) == "URL: " + url


def test_format_bibtex_zenodo_doi() -> None:
    """
    test that we can correctly parse bibtex entries obtained from a zenodo doi
    """
    # this was fetched on 2016-05-10
    bibtex_zenodo = """
    @data{0b1284ba-5ce5-4367-84f3-c44b4962ad90,
    doi = {10.5281/zenodo.50186},
    url = {https://doi.org/10.5281/zenodo.50186},
    author = {Satrajit Ghosh; Chris Filo Gorgolewski; Oscar Esteban;
    Erik Ziegler; David Ellis; cindeem; Michael Waskom; Dav Clark; Michael;
    Fred Loney; Alexandre M. S.; Michael Notter; Hans Johnson;
    Anisha Keshavan; Yaroslav Halchenko; Carlo Hamalainen; Blake Dewey;
    Ben Cipollini; Daniel Clark; Julia Huntenburg; Drew Erickson;
    Michael Hanke; moloney; Jason W; Demian Wassermann; cdla;
    Nolan Nichols; Chris Markiewicz; Jarrod Millman; Arman Eshaghi; },
    publisher = {Zenodo},
    title = {nipype: Release candidate 1 for version 0.12.0},
    year = {2016}
    }
    """
    assert (
        format_bibtex(BibTeX(bibtex_zenodo))
        == """Ghosh, S. et al., 2016. nipype: Release candidate 1 for version 0.12.0."""
    )


def test_format_bibtex_with_utf_characters() -> None:
    """
    test that we can correctly parse bibtex entry if it contains utf-8 characters
    """
    # this was fetched on 2017-08-16
    # replaced Brett with Brótt to have utf-8 characters in first author's name as well
    bibtex_utf8 = (
        "@misc{https://doi.org/10.5281/zenodo.60847,\n  doi = {10.5281/zenodo.60847},\n  url = {"
        "http://zenodo.org/record/60847},\n  author = {Brótt, Matthew and Hanke, Michael and Cipollini, "
        "Ben and {Marc-Alexandre Côté} and Markiewicz, Chris and Gerhard, Stephan and Larson, "
        "Eric and Lee, Gregory R. and Halchenko, Yaroslav and Kastman, Erik and {Cindeem} and Morency, "
        "Félix C. and {Moloney} and Millman, Jarrod and Rokem, Ariel and {Jaeilepp} and Gramfort, "
        "Alexandre and Bosch, Jasper J.F. Van Den and {Krish Subramaniam} and Nichols, Nolan and {Embaker} "
        "and {Bpinsard} and {Chaselgrove} and Oosterhof, Nikolaas N. and St-Jean, Samuel and {Bago "
        "Amirbekian} and Nimmo-Smith, Ian and {Satrajit Ghosh}},\n  keywords = {},\n  title = {nibabel "
        "2.0.1},\n  publisher = {Zenodo},\n  year = {2015}\n} "
    )
    assert (
        format_bibtex(BibTeX(bibtex_utf8)) == "Brótt, M. et al., 2015. nibabel 2.0.1."
    )


def test_is_contained() -> None:
    toppath = "package"
    assert _is_contained(toppath, "package.module")
    assert _is_contained(toppath, "package.module.submodule")
    assert _is_contained(toppath, "package.module.submodule:object")
    assert _is_contained(toppath, "package:object")
    assert _is_contained(toppath, toppath)
    assert not _is_contained(toppath, "package2")
    assert not _is_contained(toppath, "package2:anotherobject")
    assert not _is_contained(toppath, "package2.module:anotherobject")
