# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
LinkML schema and generated data models for DueCredit.

This package provides:
- A LinkML schema (duecredit.yaml) that formalizes duecredit's data model
- Generated Python dataclasses (model.py) from the LinkML schema
- JSON-LD context (duecredit.context.jsonld) for CodeMeta interoperability

The schema provides crosswalks to:
- CodeMeta (https://codemeta.github.io/)
- schema.org (http://schema.org/)
- Dublin Core (http://purl.org/dc/terms/)

This formalization enables interoperability with other software citation schemas
and tools built on the LinkML ecosystem.
"""

from pathlib import Path

# Location of schema files
SCHEMA_DIR = Path(__file__).parent
SCHEMA_FILE = SCHEMA_DIR / "duecredit.yaml"
CONTEXT_FILE = SCHEMA_DIR / "duecredit.context.jsonld"

__all__ = ["CONTEXT_FILE", "SCHEMA_DIR", "SCHEMA_FILE"]
