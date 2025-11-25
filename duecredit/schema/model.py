# Auto generated from duecredit.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-11-25T15:47:10
# Schema: duecredit
#
# id: https://github.com/duecredit/duecredit/schema
# description: A LinkML schema for DueCredit citation tracking data structures.
#   This schema provides a standardized data model that is compatible with
#   CodeMeta (https://codemeta.github.io/) and other software citation schemas.
#
# license: BSD-2-Clause

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Boolean, Integer, String
from linkml_runtime.utils.metamodelcore import Bool

metamodel_version = "1.7.0"
version = "1.0.0"

# Namespaces
CODEMETA = CurieNamespace('codemeta', 'https://codemeta.github.io/terms/')
DC = CurieNamespace('dc', 'http://purl.org/dc/terms/')
DUECREDIT = CurieNamespace('duecredit', 'https://github.com/duecredit/duecredit/schema/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = DUECREDIT


# Types

# Class references
class EntryKey(extended_str):
    pass


class BibTeXEntryKey(EntryKey):
    pass


class DoiEntryKey(EntryKey):
    pass


class UrlEntryKey(EntryKey):
    pass


class TextEntryKey(EntryKey):
    pass


class SoftwareComponentPath(extended_str):
    pass


@dataclass(repr=False)
class Person(YAMLRoot):
    """
    A person who contributed to a work
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Person"]
    class_class_curie: ClassVar[str] = "schema:Person"
    class_name: ClassVar[str] = "Person"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.Person

    given_name: Optional[str] = None
    family_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    orcid: Optional[str] = None
    affiliation: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.given_name is not None and not isinstance(self.given_name, str):
            self.given_name = str(self.given_name)

        if self.family_name is not None and not isinstance(self.family_name, str):
            self.family_name = str(self.family_name)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.email is not None and not isinstance(self.email, str):
            self.email = str(self.email)

        if self.orcid is not None and not isinstance(self.orcid, str):
            self.orcid = str(self.orcid)

        if self.affiliation is not None and not isinstance(self.affiliation, str):
            self.affiliation = str(self.affiliation)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Entry(YAMLRoot):
    """
    Base class for citation entries. Maps to schema:CreativeWork in CodeMeta.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["CreativeWork"]
    class_class_curie: ClassVar[str] = "schema:CreativeWork"
    class_name: ClassVar[str] = "Entry"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.Entry

    key: Union[str, EntryKey] = None
    entry_type: Union[str, "EntryType"] = None
    raw_entry: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.key):
            self.MissingRequiredField("key")
        if not isinstance(self.key, EntryKey):
            self.key = EntryKey(self.key)

        if self._is_empty(self.entry_type):
            self.MissingRequiredField("entry_type")
        if not isinstance(self.entry_type, EntryType):
            self.entry_type = EntryType(self.entry_type)

        if self.raw_entry is not None and not isinstance(self.raw_entry, str):
            self.raw_entry = str(self.raw_entry)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BibTeXEntry(Entry):
    """
    A BibTeX formatted citation entry
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["ScholarlyArticle"]
    class_class_curie: ClassVar[str] = "schema:ScholarlyArticle"
    class_name: ClassVar[str] = "BibTeXEntry"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.BibTeXEntry

    key: Union[str, BibTeXEntryKey] = None
    entry_type: Union[str, "EntryType"] = None
    bibtex_type: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[Union[Union[dict, Person], list[Union[dict, Person]]]] = empty_list()
    year: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    number: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.key):
            self.MissingRequiredField("key")
        if not isinstance(self.key, BibTeXEntryKey):
            self.key = BibTeXEntryKey(self.key)

        if self.bibtex_type is not None and not isinstance(self.bibtex_type, str):
            self.bibtex_type = str(self.bibtex_type)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if not isinstance(self.authors, list):
            self.authors = [self.authors] if self.authors is not None else []
        self.authors = [v if isinstance(v, Person) else Person(**as_dict(v)) for v in self.authors]

        if self.year is not None and not isinstance(self.year, str):
            self.year = str(self.year)

        if self.journal is not None and not isinstance(self.journal, str):
            self.journal = str(self.journal)

        if self.volume is not None and not isinstance(self.volume, str):
            self.volume = str(self.volume)

        if self.number is not None and not isinstance(self.number, str):
            self.number = str(self.number)

        if self.pages is not None and not isinstance(self.pages, str):
            self.pages = str(self.pages)

        if self.publisher is not None and not isinstance(self.publisher, str):
            self.publisher = str(self.publisher)

        if self.doi is not None and not isinstance(self.doi, str):
            self.doi = str(self.doi)

        if self.url is not None and not isinstance(self.url, str):
            self.url = str(self.url)

        if self.abstract is not None and not isinstance(self.abstract, str):
            self.abstract = str(self.abstract)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DoiEntry(Entry):
    """
    A DOI reference entry
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["CreativeWork"]
    class_class_curie: ClassVar[str] = "schema:CreativeWork"
    class_name: ClassVar[str] = "DoiEntry"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.DoiEntry

    key: Union[str, DoiEntryKey] = None
    entry_type: Union[str, "EntryType"] = None
    doi: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.key):
            self.MissingRequiredField("key")
        if not isinstance(self.key, DoiEntryKey):
            self.key = DoiEntryKey(self.key)

        if self._is_empty(self.doi):
            self.MissingRequiredField("doi")
        if not isinstance(self.doi, str):
            self.doi = str(self.doi)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class UrlEntry(Entry):
    """
    A URL reference entry
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["WebPage"]
    class_class_curie: ClassVar[str] = "schema:WebPage"
    class_name: ClassVar[str] = "UrlEntry"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.UrlEntry

    key: Union[str, UrlEntryKey] = None
    entry_type: Union[str, "EntryType"] = None
    url: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.key):
            self.MissingRequiredField("key")
        if not isinstance(self.key, UrlEntryKey):
            self.key = UrlEntryKey(self.key)

        if self._is_empty(self.url):
            self.MissingRequiredField("url")
        if not isinstance(self.url, str):
            self.url = str(self.url)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class TextEntry(Entry):
    """
    A free-form text citation entry
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["CreativeWork"]
    class_class_curie: ClassVar[str] = "schema:CreativeWork"
    class_name: ClassVar[str] = "TextEntry"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.TextEntry

    key: Union[str, TextEntryKey] = None
    entry_type: Union[str, "EntryType"] = None
    text: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.key):
            self.MissingRequiredField("key")
        if not isinstance(self.key, TextEntryKey):
            self.key = TextEntryKey(self.key)

        if self._is_empty(self.text):
            self.MissingRequiredField("text")
        if not isinstance(self.text, str):
            self.text = str(self.text)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Citation(YAMLRoot):
    """
    Associates a reference entry with a specific code path, providing context
    about how the reference relates to the code.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DUECREDIT["Citation"]
    class_class_curie: ClassVar[str] = "duecredit:Citation"
    class_name: ClassVar[str] = "Citation"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.Citation

    entry_key: str = None
    path: str = None
    description: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[Union[Union[str, "CitationTag"], list[Union[str, "CitationTag"]]]] = empty_list()
    cite_module: Optional[Union[bool, Bool]] = None
    count: Optional[int] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.entry_key):
            self.MissingRequiredField("entry_key")
        if not isinstance(self.entry_key, str):
            self.entry_key = str(self.entry_key)

        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if not isinstance(self.tags, list):
            self.tags = [self.tags] if self.tags is not None else []
        self.tags = [v if isinstance(v, CitationTag) else CitationTag(v) for v in self.tags]

        if self.cite_module is not None and not isinstance(self.cite_module, Bool):
            self.cite_module = Bool(self.cite_module)

        if self.count is not None and not isinstance(self.count, int):
            self.count = int(self.count)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SoftwareComponent(YAMLRoot):
    """
    A software component (package, module, or function)
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["SoftwareSourceCode"]
    class_class_curie: ClassVar[str] = "schema:SoftwareSourceCode"
    class_name: ClassVar[str] = "SoftwareComponent"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.SoftwareComponent

    path: Union[str, SoftwareComponentPath] = None
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    citations: Optional[Union[Union[dict, Citation], list[Union[dict, Citation]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, SoftwareComponentPath):
            self.path = SoftwareComponentPath(self.path)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if not isinstance(self.citations, list):
            self.citations = [self.citations] if self.citations is not None else []
        self.citations = [v if isinstance(v, Citation) else Citation(**as_dict(v)) for v in self.citations]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DueCreditReport(YAMLRoot):
    """
    Top-level container for all DueCredit data. This maps to a CodeMeta
    SoftwareSourceCode with associated citations.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["SoftwareSourceCode"]
    class_class_curie: ClassVar[str] = "schema:SoftwareSourceCode"
    class_name: ClassVar[str] = "DueCreditReport"
    class_model_uri: ClassVar[URIRef] = DUECREDIT.DueCreditReport

    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    entries: Optional[Union[dict[Union[str, EntryKey], Union[dict, Entry]], list[Union[dict, Entry]]]] = empty_dict()
    citations: Optional[Union[Union[dict, Citation], list[Union[dict, Citation]]]] = empty_list()
    packages: Optional[Union[dict[Union[str, SoftwareComponentPath], Union[dict, SoftwareComponent]], list[Union[dict, SoftwareComponent]]]] = empty_dict()
    modules: Optional[Union[dict[Union[str, SoftwareComponentPath], Union[dict, SoftwareComponent]], list[Union[dict, SoftwareComponent]]]] = empty_dict()
    functions: Optional[Union[dict[Union[str, SoftwareComponentPath], Union[dict, SoftwareComponent]], list[Union[dict, SoftwareComponent]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        self._normalize_inlined_as_list(slot_name="entries", slot_type=Entry, key_name="key", keyed=True)

        if not isinstance(self.citations, list):
            self.citations = [self.citations] if self.citations is not None else []
        self.citations = [v if isinstance(v, Citation) else Citation(**as_dict(v)) for v in self.citations]

        self._normalize_inlined_as_list(slot_name="packages", slot_type=SoftwareComponent, key_name="path", keyed=True)

        self._normalize_inlined_as_list(slot_name="modules", slot_type=SoftwareComponent, key_name="path", keyed=True)

        self._normalize_inlined_as_list(slot_name="functions", slot_type=SoftwareComponent, key_name="path", keyed=True)

        super().__post_init__(**kwargs)


# Enumerations
class EntryType(EnumDefinitionImpl):
    """
    The type of citation entry
    """
    bibtex = PermissibleValue(
        text="bibtex",
        description="A BibTeX formatted citation")
    doi = PermissibleValue(
        text="doi",
        description="A Digital Object Identifier")
    url = PermissibleValue(
        text="url",
        description="A URL reference")
    text = PermissibleValue(
        text="text",
        description="Free-form text citation")

    _defn = EnumDefinition(
        name="EntryType",
        description="The type of citation entry",
    )

class CitationTag(EnumDefinitionImpl):
    """
    Tags that describe the relationship between code and the referenced work.
    See https://github.com/duecredit/duecredit/#tags
    """
    implementation = PermissibleValue(
        text="implementation",
        description="An implementation of the cited method (default)")
    use = PermissibleValue(
        text="use",
        description="Publications demonstrating a worthwhile noting use of the method")
    edu = PermissibleValue(
        text="edu",
        description="Tutorials, textbooks and other educational materials")
    donate = PermissibleValue(
        text="donate",
        description="URLs describing how to contribute funds to the project")
    funding = PermissibleValue(
        text="funding",
        description="Sources of funding for the implementation")
    dataset = PermissibleValue(
        text="dataset",
        description="References to datasets")

    _defn = EnumDefinition(
        name="CitationTag",
        description="""Tags that describe the relationship between code and the referenced work.
See https://github.com/duecredit/duecredit/#tags""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "reference-implementation",
            PermissibleValue(
                text="reference-implementation",
                description="The original implementation by the authors of the paper"))
        setattr(cls, "another-implementation",
            PermissibleValue(
                text="another-implementation",
                description="Some other implementation of the method"))

# Slots
class slots:
    pass

slots.person__given_name = Slot(uri=SCHEMA.givenName, name="person__given_name", curie=SCHEMA.curie('givenName'),
                   model_uri=DUECREDIT.person__given_name, domain=None, range=Optional[str])

slots.person__family_name = Slot(uri=SCHEMA.familyName, name="person__family_name", curie=SCHEMA.curie('familyName'),
                   model_uri=DUECREDIT.person__family_name, domain=None, range=Optional[str])

slots.person__name = Slot(uri=SCHEMA.name, name="person__name", curie=SCHEMA.curie('name'),
                   model_uri=DUECREDIT.person__name, domain=None, range=Optional[str])

slots.person__email = Slot(uri=SCHEMA.email, name="person__email", curie=SCHEMA.curie('email'),
                   model_uri=DUECREDIT.person__email, domain=None, range=Optional[str])

slots.person__orcid = Slot(uri=SCHEMA.identifier, name="person__orcid", curie=SCHEMA.curie('identifier'),
                   model_uri=DUECREDIT.person__orcid, domain=None, range=Optional[str])

slots.person__affiliation = Slot(uri=SCHEMA.affiliation, name="person__affiliation", curie=SCHEMA.curie('affiliation'),
                   model_uri=DUECREDIT.person__affiliation, domain=None, range=Optional[str])

slots.entry__key = Slot(uri=DUECREDIT.key, name="entry__key", curie=DUECREDIT.curie('key'),
                   model_uri=DUECREDIT.entry__key, domain=None, range=URIRef)

slots.entry__entry_type = Slot(uri=DUECREDIT.entry_type, name="entry__entry_type", curie=DUECREDIT.curie('entry_type'),
                   model_uri=DUECREDIT.entry__entry_type, domain=None, range=Union[str, "EntryType"])

slots.entry__raw_entry = Slot(uri=DUECREDIT.raw_entry, name="entry__raw_entry", curie=DUECREDIT.curie('raw_entry'),
                   model_uri=DUECREDIT.entry__raw_entry, domain=None, range=Optional[str])

slots.bibTeXEntry__bibtex_type = Slot(uri=DUECREDIT.bibtex_type, name="bibTeXEntry__bibtex_type", curie=DUECREDIT.curie('bibtex_type'),
                   model_uri=DUECREDIT.bibTeXEntry__bibtex_type, domain=None, range=Optional[str])

slots.bibTeXEntry__title = Slot(uri=SCHEMA.name, name="bibTeXEntry__title", curie=SCHEMA.curie('name'),
                   model_uri=DUECREDIT.bibTeXEntry__title, domain=None, range=Optional[str])

slots.bibTeXEntry__authors = Slot(uri=SCHEMA.author, name="bibTeXEntry__authors", curie=SCHEMA.curie('author'),
                   model_uri=DUECREDIT.bibTeXEntry__authors, domain=None, range=Optional[Union[Union[dict, Person], list[Union[dict, Person]]]])

slots.bibTeXEntry__year = Slot(uri=SCHEMA.datePublished, name="bibTeXEntry__year", curie=SCHEMA.curie('datePublished'),
                   model_uri=DUECREDIT.bibTeXEntry__year, domain=None, range=Optional[str])

slots.bibTeXEntry__journal = Slot(uri=SCHEMA.isPartOf, name="bibTeXEntry__journal", curie=SCHEMA.curie('isPartOf'),
                   model_uri=DUECREDIT.bibTeXEntry__journal, domain=None, range=Optional[str])

slots.bibTeXEntry__volume = Slot(uri=DUECREDIT.volume, name="bibTeXEntry__volume", curie=DUECREDIT.curie('volume'),
                   model_uri=DUECREDIT.bibTeXEntry__volume, domain=None, range=Optional[str])

slots.bibTeXEntry__number = Slot(uri=DUECREDIT.number, name="bibTeXEntry__number", curie=DUECREDIT.curie('number'),
                   model_uri=DUECREDIT.bibTeXEntry__number, domain=None, range=Optional[str])

slots.bibTeXEntry__pages = Slot(uri=SCHEMA.pagination, name="bibTeXEntry__pages", curie=SCHEMA.curie('pagination'),
                   model_uri=DUECREDIT.bibTeXEntry__pages, domain=None, range=Optional[str])

slots.bibTeXEntry__publisher = Slot(uri=SCHEMA.publisher, name="bibTeXEntry__publisher", curie=SCHEMA.curie('publisher'),
                   model_uri=DUECREDIT.bibTeXEntry__publisher, domain=None, range=Optional[str])

slots.bibTeXEntry__doi = Slot(uri=SCHEMA.identifier, name="bibTeXEntry__doi", curie=SCHEMA.curie('identifier'),
                   model_uri=DUECREDIT.bibTeXEntry__doi, domain=None, range=Optional[str])

slots.bibTeXEntry__url = Slot(uri=SCHEMA.url, name="bibTeXEntry__url", curie=SCHEMA.curie('url'),
                   model_uri=DUECREDIT.bibTeXEntry__url, domain=None, range=Optional[str])

slots.bibTeXEntry__abstract = Slot(uri=SCHEMA.abstract, name="bibTeXEntry__abstract", curie=SCHEMA.curie('abstract'),
                   model_uri=DUECREDIT.bibTeXEntry__abstract, domain=None, range=Optional[str])

slots.doiEntry__doi = Slot(uri=SCHEMA.identifier, name="doiEntry__doi", curie=SCHEMA.curie('identifier'),
                   model_uri=DUECREDIT.doiEntry__doi, domain=None, range=str)

slots.urlEntry__url = Slot(uri=SCHEMA.url, name="urlEntry__url", curie=SCHEMA.curie('url'),
                   model_uri=DUECREDIT.urlEntry__url, domain=None, range=str)

slots.textEntry__text = Slot(uri=DUECREDIT.text, name="textEntry__text", curie=DUECREDIT.curie('text'),
                   model_uri=DUECREDIT.textEntry__text, domain=None, range=str)

slots.citation__entry_key = Slot(uri=DUECREDIT.entry_key, name="citation__entry_key", curie=DUECREDIT.curie('entry_key'),
                   model_uri=DUECREDIT.citation__entry_key, domain=None, range=str)

slots.citation__path = Slot(uri=CODEMETA.targetProduct, name="citation__path", curie=CODEMETA.curie('targetProduct'),
                   model_uri=DUECREDIT.citation__path, domain=None, range=str)

slots.citation__description = Slot(uri=SCHEMA.description, name="citation__description", curie=SCHEMA.curie('description'),
                   model_uri=DUECREDIT.citation__description, domain=None, range=Optional[str])

slots.citation__version = Slot(uri=SCHEMA.softwareVersion, name="citation__version", curie=SCHEMA.curie('softwareVersion'),
                   model_uri=DUECREDIT.citation__version, domain=None, range=Optional[str])

slots.citation__tags = Slot(uri=DUECREDIT.tags, name="citation__tags", curie=DUECREDIT.curie('tags'),
                   model_uri=DUECREDIT.citation__tags, domain=None, range=Optional[Union[Union[str, "CitationTag"], list[Union[str, "CitationTag"]]]])

slots.citation__cite_module = Slot(uri=DUECREDIT.cite_module, name="citation__cite_module", curie=DUECREDIT.curie('cite_module'),
                   model_uri=DUECREDIT.citation__cite_module, domain=None, range=Optional[Union[bool, Bool]])

slots.citation__count = Slot(uri=DUECREDIT.count, name="citation__count", curie=DUECREDIT.curie('count'),
                   model_uri=DUECREDIT.citation__count, domain=None, range=Optional[int])

slots.softwareComponent__path = Slot(uri=SCHEMA.identifier, name="softwareComponent__path", curie=SCHEMA.curie('identifier'),
                   model_uri=DUECREDIT.softwareComponent__path, domain=None, range=URIRef)

slots.softwareComponent__name = Slot(uri=SCHEMA.name, name="softwareComponent__name", curie=SCHEMA.curie('name'),
                   model_uri=DUECREDIT.softwareComponent__name, domain=None, range=Optional[str])

slots.softwareComponent__description = Slot(uri=SCHEMA.description, name="softwareComponent__description", curie=SCHEMA.curie('description'),
                   model_uri=DUECREDIT.softwareComponent__description, domain=None, range=Optional[str])

slots.softwareComponent__version = Slot(uri=SCHEMA.softwareVersion, name="softwareComponent__version", curie=SCHEMA.curie('softwareVersion'),
                   model_uri=DUECREDIT.softwareComponent__version, domain=None, range=Optional[str])

slots.softwareComponent__citations = Slot(uri=DUECREDIT.citations, name="softwareComponent__citations", curie=DUECREDIT.curie('citations'),
                   model_uri=DUECREDIT.softwareComponent__citations, domain=None, range=Optional[Union[Union[dict, Citation], list[Union[dict, Citation]]]])

slots.dueCreditReport__name = Slot(uri=SCHEMA.name, name="dueCreditReport__name", curie=SCHEMA.curie('name'),
                   model_uri=DUECREDIT.dueCreditReport__name, domain=None, range=Optional[str])

slots.dueCreditReport__version = Slot(uri=SCHEMA.softwareVersion, name="dueCreditReport__version", curie=SCHEMA.curie('softwareVersion'),
                   model_uri=DUECREDIT.dueCreditReport__version, domain=None, range=Optional[str])

slots.dueCreditReport__description = Slot(uri=SCHEMA.description, name="dueCreditReport__description", curie=SCHEMA.curie('description'),
                   model_uri=DUECREDIT.dueCreditReport__description, domain=None, range=Optional[str])

slots.dueCreditReport__entries = Slot(uri=DUECREDIT.entries, name="dueCreditReport__entries", curie=DUECREDIT.curie('entries'),
                   model_uri=DUECREDIT.dueCreditReport__entries, domain=None, range=Optional[Union[dict[Union[str, EntryKey], Union[dict, Entry]], list[Union[dict, Entry]]]])

slots.dueCreditReport__citations = Slot(uri=DUECREDIT.citations, name="dueCreditReport__citations", curie=DUECREDIT.curie('citations'),
                   model_uri=DUECREDIT.dueCreditReport__citations, domain=None, range=Optional[Union[Union[dict, Citation], list[Union[dict, Citation]]]])

slots.dueCreditReport__packages = Slot(uri=DUECREDIT.packages, name="dueCreditReport__packages", curie=DUECREDIT.curie('packages'),
                   model_uri=DUECREDIT.dueCreditReport__packages, domain=None, range=Optional[Union[dict[Union[str, SoftwareComponentPath], Union[dict, SoftwareComponent]], list[Union[dict, SoftwareComponent]]]])

slots.dueCreditReport__modules = Slot(uri=DUECREDIT.modules, name="dueCreditReport__modules", curie=DUECREDIT.curie('modules'),
                   model_uri=DUECREDIT.dueCreditReport__modules, domain=None, range=Optional[Union[dict[Union[str, SoftwareComponentPath], Union[dict, SoftwareComponent]], list[Union[dict, SoftwareComponent]]]])

slots.dueCreditReport__functions = Slot(uri=DUECREDIT.functions, name="dueCreditReport__functions", curie=DUECREDIT.curie('functions'),
                   model_uri=DUECREDIT.dueCreditReport__functions, domain=None, range=Optional[Union[dict[Union[str, SoftwareComponentPath], Union[dict, SoftwareComponent]], list[Union[dict, SoftwareComponent]]]])

