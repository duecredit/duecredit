# 0.9.2 (Wed Feb 01 2023)

#### 🐛 Bug Fix

- Tell LGTM to ignore unused imports in stub.py [#179](https://github.com/duecredit/duecredit/pull/179) ([@jwodder](https://github.com/jwodder))

#### 🏠 Internal

- Make Debian Python version PEP440 compliant [#184](https://github.com/duecredit/duecredit/pull/184) ([@bdrung](https://github.com/bdrung))

#### Authors: 2

- Benjamin Drung ([@bdrung](https://github.com/bdrung))
- John T. Wodder II ([@jwodder](https://github.com/jwodder))

---

# 0.9.1 (Tue Apr 13 2021)

#### 🐛 Bug Fix

- Set up intuit auto to automate releases [#178](https://github.com/duecredit/duecredit/pull/178) ([@jwodder](https://github.com/jwodder) [@yarikoptic](https://github.com/yarikoptic))
- BF: make pypi upload happen in py 3.8 matrix (2.7 was removed) [#178](https://github.com/duecredit/duecredit/pull/178) ([@yarikoptic](https://github.com/yarikoptic))

#### Authors: 2

- John T. Wodder II ([@jwodder](https://github.com/jwodder))
- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))

---

# [0.9.0](https://github.com/duecredit/duecredit/tree/0.9.0) (2021-04-13)

- Drop support for Python < 3.6
- Python packaging is reworked, importlib-metadata is added
  as a dependency for python < 3.8

# [0.8.1](https://github.com/duecredit/duecredit/tree/0.8.0) (2021-01-26)

- Announce lines with unescaped \ as r(aw)

# [0.8.0](https://github.com/duecredit/duecredit/tree/0.8.0) (2020-02-09)

- Variety of small fixes
- Added .zenodo.json for more proper citation of duecredit
- drop testing for 3.4 -- rare beast, lxml does not provide pkg for it
- Support for citing matplotlib via injection
- Address a few deprecation warnings (#146)
- Provide more informative message whenever using older citeproc without encoding arg

# [0.7.0](https://github.com/duecredit/duecredit/tree/0.7.0) (2019-03-01)

- Prevent warnings from the injector's `__del__`.
- InactiveDueCollector in `stub.py` now provides also `active=False`
  attribute (so external tools could directly query if duecredit is 
  active) and no-op `activate` and `dump` for consistent API with a
  `due` object whenever `duecredit` is available.
- Provide `Text` citation entry for free form text. It does not have any
  meaningful rendering in BibTex but is present in text rendering.
  `Url` entry also acquired text rendering with prefix `URL: `.

# [0.6.5](https://github.com/duecredit/duecredit/tree/0.6.5) (2019-02-04)

- Delay import of imports (thanks [Chris Markiewicz (@effigies)](https://github.com/effigies)
  - serves also as a workaround due to inconsistent installation of
    3rd party modules/libraries such as openssl
	[\#142](https://github.com/duecredit/duecredit/issues/142)
- Use https://doi.org as preferred DOI resolver.
  Thanks [Katrin Leinweber (@katrinleinweber)](https://github.com/katrinleinweber)
  for the contribution

# [0.6.4](https://github.com/duecredit/duecredit/tree/0.6.4) (2018-06-25)

- Added doi to numpy injection
- Minor tune-ups to the docs

# [0.6.3](https://github.com/duecredit/duecredit/tree/0.6.3) (2017-08-01)

  Fixed a bug disallowing installation of duecredit in environments with
  crippled/too-basic locale setting.

# [0.6.2](https://github.com/duecredit/duecredit/tree/0.6.2) (2017-06-23)

- Testing was converted to pytest
- Various enhancements in supporting python3 and BiBTeX with utf-8
- New tag 'dataset' to describe datasets

# [0.6.1](https://github.com/duecredit/duecredit/tree/0.6.1) (2016-07-09)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.6.0...0.6.1)

**Merged pull requests:**

- ENH: workaround for pages handling fixed in citeproc post 0.3.0 [\#98](https://github.com/duecredit/duecredit/pull/98) ([yarikoptic](https://github.com/yarikoptic))

# [0.6.0](https://github.com/duecredit/duecredit/tree/0.6.0) (2016-06-17)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.5.0...0.6.0)

**Implemented enhancements:**

- Support system-specific references [\#81](https://github.com/duecredit/duecredit/issues/81)
- export to bibtex doesn't support tags yet [\#19](https://github.com/duecredit/duecredit/issues/19)
- ENH: support DUECREDIT\_REPORT\_ALL=1 to report all citations, not only with functionality used [\#92](https://github.com/duecredit/duecredit/pull/92) ([yarikoptic](https://github.com/yarikoptic))

**Fixed bugs:**

- Outputting to bibtex doesn't filter by used citations [\#68](https://github.com/duecredit/duecredit/issues/68)
- references package even if no cited functions/methods used [\#48](https://github.com/duecredit/duecredit/issues/48)
- When injecting multiple citations at the same point, only one referenced [\#47](https://github.com/duecredit/duecredit/issues/47)

**Merged pull requests:**

- BF: allow multiple injections at the same path, avoid resetting \_orig\_import if already deactivated [\#91](https://github.com/duecredit/duecredit/pull/91) ([yarikoptic](https://github.com/yarikoptic))
- DOC: Update readme to reflect current output of duecredit summary [\#89](https://github.com/duecredit/duecredit/pull/89) ([mvdoc](https://github.com/mvdoc))
- enable codecov coverage reports [\#87](https://github.com/duecredit/duecredit/pull/87) ([yarikoptic](https://github.com/yarikoptic))
- REF,ENH: refactor {BibTeX,Text}Output into Output class with subclasses [\#86](https://github.com/duecredit/duecredit/pull/86) ([mvdoc](https://github.com/mvdoc))

# [0.5.0](https://github.com/duecredit/duecredit/tree/0.5.0) (2016-05-11)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.8...0.5.0)

**Fixed bugs:**

- test\_noincorrect\_import\_if\_no\_lxml fails on my laptop \(and on travis\) [\#84](https://github.com/duecredit/duecredit/issues/84)
- zenodo and "unofficial" bibtex entry types [\#77](https://github.com/duecredit/duecredit/issues/77)

**Closed issues:**

- duecredit on nipype [\#72](https://github.com/duecredit/duecredit/issues/72)

**Merged pull requests:**

- BF: workaround for zenodo bibtex entries imported with import\_doi [\#85](https://github.com/duecredit/duecredit/pull/85) ([mvdoc](https://github.com/mvdoc))
- enable testing under python 3.5 on travis [\#79](https://github.com/duecredit/duecredit/pull/79) ([yarikoptic](https://github.com/yarikoptic))
- ENH: appveyor configuration \(based on shablona's\) based on mix of conda and pip [\#70](https://github.com/duecredit/duecredit/pull/70) ([yarikoptic](https://github.com/yarikoptic))

# [0.4.8](https://github.com/duecredit/duecredit/tree/0.4.8) (2016-05-04)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.7...0.4.8)

**Closed issues:**

- Referencing articles with no DOI [\#74](https://github.com/duecredit/duecredit/issues/74)
- doi importer doesn't work with zenodo dois [\#73](https://github.com/duecredit/duecredit/issues/73)

**Merged pull requests:**

- BF: change request command to make it work with zenodo too [\#76](https://github.com/duecredit/duecredit/pull/76) ([mvdoc](https://github.com/mvdoc))
- DOC: Show that user can also enter BibTeX entries [\#75](https://github.com/duecredit/duecredit/pull/75) ([mvdoc](https://github.com/mvdoc))

# [0.4.7](https://github.com/duecredit/duecredit/tree/0.4.7) (2016-04-21)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.6...0.4.7)

# [0.4.6](https://github.com/duecredit/duecredit/tree/0.4.6) (2016-04-19)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.5...0.4.6)

**Fixed bugs:**

- In PyMVPA, fail to handle failures if lxml, types not available [\#64](https://github.com/duecredit/duecredit/issues/64)

**Merged pull requests:**

- Primarily PEP8 for stub.py  \(the rest needs more work\) [\#69](https://github.com/duecredit/duecredit/pull/69) ([yarikoptic](https://github.com/yarikoptic))
- Use HTTPS for GitHub URL [\#67](https://github.com/duecredit/duecredit/pull/67) ([jwilk](https://github.com/jwilk))
- Fix typos [\#66](https://github.com/duecredit/duecredit/pull/66) ([jwilk](https://github.com/jwilk))

# [0.4.5](https://github.com/duecredit/duecredit/tree/0.4.5) (2015-12-03)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.4...0.4.5)

**Merged pull requests:**

- Make duecredit import and stub more robust to failures with e.g. import of lxml [\#65](https://github.com/duecredit/duecredit/pull/65) ([yarikoptic](https://github.com/yarikoptic))

# [0.4.4](https://github.com/duecredit/duecredit/tree/0.4.4) (2015-11-08)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.3...0.4.4)

# [0.4.3](https://github.com/duecredit/duecredit/tree/0.4.3) (2015-09-28)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.2...0.4.3)

**Implemented enhancements:**

- Make "conditions" even more powerful [\#36](https://github.com/duecredit/duecredit/issues/36)

**Merged pull requests:**

- add mod\_ files for nibabel, nipy, nipype [\#62](https://github.com/duecredit/duecredit/pull/62) ([jgors](https://github.com/jgors))
- fixed headers for injections/mod\_ files and added item to .gitignore [\#60](https://github.com/duecredit/duecredit/pull/60) ([jgors](https://github.com/jgors))
- ENH+BF: recently introduced entries got fixed up [\#59](https://github.com/duecredit/duecredit/pull/59) ([yarikoptic](https://github.com/yarikoptic))
- add mod\_\* files [\#58](https://github.com/duecredit/duecredit/pull/58) ([jgors](https://github.com/jgors))
- ENH: versions -- provide dumps, keys, \_\_contains\_\_ [\#57](https://github.com/duecredit/duecredit/pull/57) ([yarikoptic](https://github.com/yarikoptic))
- ENH: Two more module level injections [\#56](https://github.com/duecredit/duecredit/pull/56) ([yarikoptic](https://github.com/yarikoptic))

# [0.4.2](https://github.com/duecredit/duecredit/tree/0.4.2) (2015-09-03)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.1...0.4.2)

**Closed issues:**

- we should output description \(not just path\) in the listing [\#49](https://github.com/duecredit/duecredit/issues/49)

**Merged pull requests:**

- BF: print description, not just path. Closes \#49 [\#52](https://github.com/duecredit/duecredit/pull/52) ([yarikoptic](https://github.com/yarikoptic))
- Overhaul conditions -- "and" logic \(all must be met\) + allow to access attributes of the arguments [\#50](https://github.com/duecredit/duecredit/pull/50) ([yarikoptic](https://github.com/yarikoptic))
- BF: Fix get\_text\_rendering when Citation is passed with Doi [\#46](https://github.com/duecredit/duecredit/pull/46) ([mvdoc](https://github.com/mvdoc))

# [0.4.1](https://github.com/duecredit/duecredit/tree/0.4.1) (2015-08-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.0...0.4.1)

# [0.4.0](https://github.com/duecredit/duecredit/tree/0.4.0) (2015-08-21)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.3.0...0.4.0)

**Fixed bugs:**

- Cross-referencing does not work [\#30](https://github.com/duecredit/duecredit/issues/30)

**Closed issues:**

- DUECREDIT\_ENABLE doesn't work anymore [\#45](https://github.com/duecredit/duecredit/issues/45)
- test\_no\_double\_activation on injector fails on travis and locally with Python 2.7.{6,9} [\#43](https://github.com/duecredit/duecredit/issues/43)
- possible bug \(race condition\) in injector's \_\_import\_\_ handling [\#40](https://github.com/duecredit/duecredit/issues/40)

**Merged pull requests:**

- ENH+DOC: always check if \_orig\_import is not None \(Closes \#40\) [\#44](https://github.com/duecredit/duecredit/pull/44) ([yarikoptic](https://github.com/yarikoptic))
- \[Injections\] Add all references for sklearn.cluster [\#42](https://github.com/duecredit/duecredit/pull/42) ([mvdoc](https://github.com/mvdoc))
- REF: text output, divide "model" from "view" [\#41](https://github.com/duecredit/duecredit/pull/41) ([mvdoc](https://github.com/mvdoc))
- RF to provide \_\_main\_\_ so we could do   python -m duecredit  existing script [\#39](https://github.com/duecredit/duecredit/pull/39) ([yarikoptic](https://github.com/yarikoptic))

# [0.3.0](https://github.com/duecredit/duecredit/tree/0.3.0) (2015-08-05)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.2.2...0.3.0)

**Implemented enhancements:**

- automagically upload releases to pypi from travis [\#6](https://github.com/duecredit/duecredit/issues/6)

**Fixed bugs:**

- while "dump"ing -- references shouldn't be duplicated even if used in multiple modules [\#23](https://github.com/duecredit/duecredit/issues/23)

**Closed issues:**

- Syntax error in test\_utils.py with python 2.7.6 [\#26](https://github.com/duecredit/duecredit/issues/26)
- Travis skips tests [\#25](https://github.com/duecredit/duecredit/issues/25)

**Merged pull requests:**

- RF: cite-on-import -\> cite-module  since we might be dealing with other languages etc [\#37](https://github.com/duecredit/duecredit/pull/37) ([yarikoptic](https://github.com/yarikoptic))
- Few tune ups to injection and more to its testing [\#35](https://github.com/duecredit/duecredit/pull/35) ([yarikoptic](https://github.com/yarikoptic))
- RF: Donate -\> Url [\#34](https://github.com/duecredit/duecredit/pull/34) ([yarikoptic](https://github.com/yarikoptic))
- TST: check reference numbers are consistent [\#29](https://github.com/duecredit/duecredit/pull/29) ([mvdoc](https://github.com/mvdoc))
- PY3+make vcr optional: more concise use of six, it might take a while for vcr to come to debian [\#28](https://github.com/duecredit/duecredit/pull/28) ([yarikoptic](https://github.com/yarikoptic))
- BF: give correct ref numbers for citations [\#24](https://github.com/duecredit/duecredit/pull/24) ([mvdoc](https://github.com/mvdoc))
- Fix typo in README.md [\#21](https://github.com/duecredit/duecredit/pull/21) ([lesteve](https://github.com/lesteve))

# [0.2.2](https://github.com/duecredit/duecredit/tree/0.2.2) (2015-07-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.2.1...0.2.2)

# [0.2.1](https://github.com/duecredit/duecredit/tree/0.2.1) (2015-07-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.2.0...0.2.1)

# [0.2.0](https://github.com/duecredit/duecredit/tree/0.2.0) (2015-07-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.1.1...0.2.0)

**Closed issues:**

- RFC: either rename "kind" and "level" into some thing more descriptive [\#8](https://github.com/duecredit/duecredit/issues/8)
- add "classes" \(or tags?\) to citations on what citation is about [\#5](https://github.com/duecredit/duecredit/issues/5)
- version for modules still doesn't work [\#2](https://github.com/duecredit/duecredit/issues/2)

**Merged pull requests:**

- BF: circular import of injector and duecredit [\#17](https://github.com/duecredit/duecredit/pull/17) ([mvdoc](https://github.com/mvdoc))
- Add six to the requirements [\#15](https://github.com/duecredit/duecredit/pull/15) ([mvdoc](https://github.com/mvdoc))
- ENH: conditions kwarg for dcite to condition when to trigger the citation given arguments to the function call [\#14](https://github.com/duecredit/duecredit/pull/14) ([yarikoptic](https://github.com/yarikoptic))
- \[WIP\] Start adding more injections [\#13](https://github.com/duecredit/duecredit/pull/13) ([mvdoc](https://github.com/mvdoc))
- RF arguments for cite:  kind -\> tags, level -\> path, use -\> desc [\#12](https://github.com/duecredit/duecredit/pull/12) ([yarikoptic](https://github.com/yarikoptic))
- ENH: try to use new container based Travis infrastructure [\#11](https://github.com/duecredit/duecredit/pull/11) ([yarikoptic](https://github.com/yarikoptic))
- WiP NF: core to implement "injection" of duecredit entries into other modules [\#10](https://github.com/duecredit/duecredit/pull/10) ([yarikoptic](https://github.com/yarikoptic))
- coveralls call should be without any args, also test installation now [\#9](https://github.com/duecredit/duecredit/pull/9) ([yarikoptic](https://github.com/yarikoptic))

# [0.1.1](https://github.com/duecredit/duecredit/tree/0.1.1) (2015-06-26)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.1.0...0.1.1)

# [0.1.0](https://github.com/duecredit/duecredit/tree/0.1.0) (2015-06-21)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.0.0...0.1.0)

**Closed issues:**

- fix badges in README.md \(it is not ,rst ;\)\) [\#4](https://github.com/duecredit/duecredit/issues/4)

**Merged pull requests:**

- Stub tests pass [\#1](https://github.com/duecredit/duecredit/pull/1) ([mvdoc](https://github.com/mvdoc))

# [0.0.0](https://github.com/duecredit/duecredit/tree/0.0.0) (2013-12-06)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
