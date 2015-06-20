=========
duecredit
=========

[![Build Status](https://travis-ci.org/duecredit/duecredit.svg?branch=master)](https://travis-ci.org/duecredit/duecredit)
[![Coverage Status](https://coveralls.io/repos/duecredit/duecredit/badge.svg)](https://coveralls.io/r/duecredit/duecredit)


duecredit is being conceived to address the problem of inadequate
citation of scientific software and methods, and limited visibility of
donation requests for open-source software.

It provides a simple framework (at the moment for Python only) to
embed publication or other references in the original code so they are
automatically collected and reported to the user at the necessary
level of reference detail, i.e. only references for actually used
functionality will be presented back if software provides multiple
citeable implementations.

duecredit 101
=============

You can already start "registering" citations using duecredit in your
software.  duecredit will remain an optional dependency, i.e. your software
will work correctly even without duecredit installed.  For that

1. copy `duecredit/stub.py` to your codebase, e.g.

        wget -q -O /path/tomodule/yourmodule/due.py \
          https://raw.githubusercontent.com/duecredit/duecredit/master/duecredit/stub.py


    **Note** that it might be better to avoid naming it duecredit.py to avoid shadowing
    installed duecredit.

2. Then use `duecredit` import due and necessary entries in your code as

        from .due import due, Doi

     to provide reference for the entire module just use e.g.

         due.cite(Doi("1.2.3/x.y.z"), use="Solves all your problems", level="module xyz")

     To provide a reference for a function or a method, use dcite decorator

         @due.dcite(Doi("1.2.3/x.y.z"), use="Resolves constipation issue")
         def pushit():
             ...

3. By default `duecredit` does exactly nothing. Then whenever anyone
   runs their analysis which uses your code and sets
   `DUECREDIT_ENABLE=yes` environment variable, and invokes any of the
   cited function/methods, at the end of the run all collected
   bibliography will be presented to the screen and pickled into
   `.duecredit.p` file in current directory.  Incremental runs of
   various software would keep enriching that file.  Then you can use
   `duecredit summary` command to show that information again (stored
   in `.duecredit.p` file) or export it as a BibTeX file ready for
   reuse.


User-view
---------

Then upon running the code citing any papers, `.duecredit.p` file will get
assembled to be queried later, e.g.:

    $> duecredit summary --format=bibtex        
    @article{Hanke_2009, title={PyMVPA: a Python Toolbox for Multivariate Pattern Analysis of fMRI Data}, volume={7}, ISSN={1559-0089}, url={http://dx.doi.org/10.1007/s12021-008-9041-y}, DOI={10.1007/s12021-008-9041-y}, number={1}, journal={Neuroinform}, publisher={Springer Science + Business Media}, author={Hanke, Michael and Halchenko, Yaroslav O. and Sederberg, Per B. and Hanson, Stephen José and Haxby, James V. and Pollmann, Stefan}, year={2009}, month={Jan}, pages={37–53}}
    @INPROCEEDINGS{breiman2001,
        author = {Leo Breiman},
        title = {Random Forests},
        booktitle = {Machine Learning},
        year = {2001},
        pages = {5--32}
    }
    ...

    $> duecredit summary                
    DueCredit Report:
    - mvpa2 (v None) [1]
      - mvpa2.clfs.transerror._call (Bayesian hypothesis testing) [4]
    - sklearn (v None) [3]
      - sklearn.ensemble.forest.fit (None) [2]

    2 modules cited
    2 functions cited
    References
    ----------
    [1] Hanke, M. et al., 2009. PyMVPA: a Python Toolbox for Multivariate Pattern Analysis of fMRI Data. Neuroinform, 7(1), pp.37–53.
    [2] Breiman, L., 2001. Random Forests. In Machine Learning. pp. 5–32.
    ...




Ultimate goals
==============

Reduce demand for prima ballerina projects
------------------------------------------

Problem: Scientific software is often developed to gain citations for
original publication through the use of the software implementing it.
Unfortunately such an established procedure discourages contributions
to the existing projects and fosters new projects to be developed from
scratch.

Solution: With easy ways to provide all-and-only relevant references
for used functionality within a large(r) framework scientific
developers would prefer to contribute to already existing projects.

Benefits: As a result, scientific developers would immediately benefit
from adhering to proper development procedures (codebase structuring,
testing, etc) and already established delivery and deployment channels
existing projects already have.  This will increase efficiency and
standardization of scientific software development, thus addressing
many (if not all) core problems with scientific software development
everyone likes to bash about (reproducibility, longevity, etc.).

Adequately reference core libraries
-----------------------------------

Problem: Scientific software often if not always uses 3rd party
libraries (e.g., NumPy, SciPy, atlas) which might not even be visible
at the user level.  Therefore they are rarely referenced in the
publications despite providing the fundamental core for solving a
scientific problem at hands.

Solution: With automated bibliography compilation for all used
libraries, such projects and their authors would get a chance to
receive adequate citability.

Benefits: Adequate appreciation of the scientific software
developments.  Coupled with a solution for "prima ballerina" problem,
more contributions will flow into the core/foundational projects
making new methodological developments readily available to even wider
audiences without proliferation of the low quality scientific software.




