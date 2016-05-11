# Change Log

## [0.5.0](https://github.com/duecredit/duecredit/tree/0.5.0) (2016-05-11)
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

## [0.4.8](https://github.com/duecredit/duecredit/tree/0.4.8) (2016-05-04)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.7...0.4.8)

**Closed issues:**

- Referencing articles with no DOI [\#74](https://github.com/duecredit/duecredit/issues/74)
- doi importer doesn't work with zenodo dois [\#73](https://github.com/duecredit/duecredit/issues/73)

**Merged pull requests:**

- BF: change request command to make it work with zenodo too [\#76](https://github.com/duecredit/duecredit/pull/76) ([mvdoc](https://github.com/mvdoc))
- DOC: Show that user can also enter BibTeX entries [\#75](https://github.com/duecredit/duecredit/pull/75) ([mvdoc](https://github.com/mvdoc))

## [0.4.7](https://github.com/duecredit/duecredit/tree/0.4.7) (2016-04-21)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.6...0.4.7)

## [0.4.6](https://github.com/duecredit/duecredit/tree/0.4.6) (2016-04-19)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.5...0.4.6)

**Fixed bugs:**

- In PyMVPA, fail to handle failures if lxml, types not available [\#64](https://github.com/duecredit/duecredit/issues/64)

**Merged pull requests:**

- Primarily PEP8 for stub.py  \(the rest needs more work\) [\#69](https://github.com/duecredit/duecredit/pull/69) ([yarikoptic](https://github.com/yarikoptic))
- Use HTTPS for GitHub URL [\#67](https://github.com/duecredit/duecredit/pull/67) ([jwilk](https://github.com/jwilk))
- Fix typos [\#66](https://github.com/duecredit/duecredit/pull/66) ([jwilk](https://github.com/jwilk))

## [0.4.5](https://github.com/duecredit/duecredit/tree/0.4.5) (2015-12-03)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.4...0.4.5)

**Merged pull requests:**

- Make duecredit import and stub more robust to failures with e.g. import of lxml [\#65](https://github.com/duecredit/duecredit/pull/65) ([yarikoptic](https://github.com/yarikoptic))

## [0.4.4](https://github.com/duecredit/duecredit/tree/0.4.4) (2015-11-08)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.3...0.4.4)

## [0.4.3](https://github.com/duecredit/duecredit/tree/0.4.3) (2015-09-28)
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

## [0.4.2](https://github.com/duecredit/duecredit/tree/0.4.2) (2015-09-03)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.1...0.4.2)

**Closed issues:**

- we should output description \(not just path\) in the listing [\#49](https://github.com/duecredit/duecredit/issues/49)

**Merged pull requests:**

- BF: print description, not just path. Closes \#49 [\#52](https://github.com/duecredit/duecredit/pull/52) ([yarikoptic](https://github.com/yarikoptic))
- Overhaul conditions -- "and" logic \(all must be met\) + allow to access attributes of the arguments [\#50](https://github.com/duecredit/duecredit/pull/50) ([yarikoptic](https://github.com/yarikoptic))
- BF: Fix get\_text\_rendering when Citation is passed with Doi [\#46](https://github.com/duecredit/duecredit/pull/46) ([mvdoc](https://github.com/mvdoc))

## [0.4.1](https://github.com/duecredit/duecredit/tree/0.4.1) (2015-08-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.4.0...0.4.1)

## [0.4.0](https://github.com/duecredit/duecredit/tree/0.4.0) (2015-08-21)
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

## [0.3.0](https://github.com/duecredit/duecredit/tree/0.3.0) (2015-08-05)
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

## [0.2.2](https://github.com/duecredit/duecredit/tree/0.2.2) (2015-07-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.2.1...0.2.2)

## [0.2.1](https://github.com/duecredit/duecredit/tree/0.2.1) (2015-07-27)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.2.0...0.2.1)

## [0.2.0](https://github.com/duecredit/duecredit/tree/0.2.0) (2015-07-27)
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

## [0.1.1](https://github.com/duecredit/duecredit/tree/0.1.1) (2015-06-26)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.1.0...0.1.1)

## [0.1.0](https://github.com/duecredit/duecredit/tree/0.1.0) (2015-06-21)
[Full Changelog](https://github.com/duecredit/duecredit/compare/0.0.0...0.1.0)

**Closed issues:**

- fix badges in README.md \(it is not ,rst ;\)\) [\#4](https://github.com/duecredit/duecredit/issues/4)

**Merged pull requests:**

- Stub tests pass [\#1](https://github.com/duecredit/duecredit/pull/1) ([mvdoc](https://github.com/mvdoc))

## [0.0.0](https://github.com/duecredit/duecredit/tree/0.0.0) (2013-12-06)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*