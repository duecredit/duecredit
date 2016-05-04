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
Python modules and even registering citations (we call this approach "injections")
for modules which do not (yet) use duecredit.  duecredit will remain an optional
dependency, i.e. your software will work correctly even without duecredit installed.

"Native" use of duecredit (recommended)
---------------------------------------

For using duecredit in your software

1. copy `duecredit/stub.py` to your codebase, e.g.

        wget -q -O /path/tomodule/yourmodule/due.py \
          https://raw.githubusercontent.com/duecredit/duecredit/master/duecredit/stub.py


    **Note** that it might be better to avoid naming it duecredit.py to avoid shadowing
    installed duecredit.

2. Then use `duecredit` import due and necessary entries in your code as

        from .due import due, Doi, BibTeX

     to provide reference for the entire module just use e.g.

         due.cite(Doi("1.2.3/x.y.z"), description="Solves all your problems", path="magicpy")

     To provide a reference for a function or a method, use dcite decorator

         @due.dcite(Doi("1.2.3/x.y.z"), description="Resolves constipation issue")
         def pushit():
             ...

References can also be entered as BibTeX entries

        due.cite(BibTeX("""
                @article{mynicearticle,
                title={A very cool paper},
                author={Happy, Author and Lucky, Author},
                journal={The Journal of Serendipitous Discoveries}
                }
                """), 
                description="Solves all your problems", path="magicpy")
        
        
Add injections for other existing modules
-----------------------------------------

We hope that eventually this somewhat cruel approach will not be necessary.  But
until other packages support duecredit "natively" we have provided a way to "inject"
citations for modules and/or functions and methods via injections:  citations will be
added to the corresponding functionality upon those modules import.

All injections are collected under
[duecredit/injections](https://github.com/duecredit/duecredit/tree/master/duecredit/injections).
See any file there with `mod_` prefix for a complete example.  But
overall it is just a regular Python module defining a function
`inject(injector)` which will then add new entries to the injector,
which will in turn add those entries to the duecredit whenever the
corresponding module gets imported.


User-view
---------

By default `duecredit` does exactly nothing -- all decorators do not
decorate, all `cite` functions just return, so there should be no fear
that it would break anything. Then whenever anyone runs their analysis
which uses your code and sets `DUECREDIT_ENABLE=yes` environment
variable or uses `python -m duecredit`, and invokes any of the cited
function/methods, at the end of the run all collected bibliography
will be presented to the screen and pickled into `.duecredit.p` file
in current directory:

    $> python -m duecredit examples/example_scipy.py
    I: Simulating 4 blobs
    I: Done clustering 4 blobs
    DueCredit Report:
    - scipy (v 0.14.1) [1]
      - scipy.cluster.hierarchy:linkage (Single linkage hierarchical clustering) [2]
    - numpy (v 1.8.2) [3]

    2 modules cited
    1 functions cited

    References
    ----------

    [1] Jones, E. et al., 2001. SciPy: Open source scientific tools for Python.
    [2] Sibson, R., 1973. SLINK: an optimally efficient algorithm for the single-link
        cluster method. The Computer Journal, 16(1), pp.30–34.
    [3] Van Der Walt, S., Colbert, S.C. & Varoquaux, G., 2011. The
        NumPy array: a structure for efficient numerical
        computation. Computing in Science & Engineering, 13(2), pp.22–30.

Incremental runs of various software would keep enriching that file.
Then you can use `duecredit summary` command to show that information
again (stored in `.duecredit.p` file) or export it as a BibTeX file
ready for reuse, e.g.:

    $> venv/bin/duecredit summary --format=bibtex
    @book{sokal1958statistical,
            author = {Sokal, R R and Michener, C D and {University of Kansas}},
            title = {{A Statistical Method for Evaluating Systematic Relationships}},
            publisher = {University of Kansas},
            year = {1958},
            series = {University of Kansas science bulletin}
        }
    @book{jain1988algorithms,
            title={Algorithms for clustering data},
            author={Jain, Anil K and Dubes, Richard C},
            year={1988},
            publisher={Prentice-Hall, Inc.}
        }
    ...


and if by default only references for "implementation" are listed, we
can enable listing of references for other tags as well (e.g. "edu"
depicting instructional materials -- textbooks etc on the topic):

    $> DUECREDIT_REPORT_TAGS=* duecredit summary
    DueCredit Report:
    - scipy (v 0.14.1) [1, 2, 3, 4, 5, 6, 7, 8]
      - scipy.cluster.hierarchy:linkage (Single linkage hierarchical clustering) [9]
    - numpy (v 1.8.2) [10]

    2 modules cited
    1 functions cited

    References
    ----------

    [1] Sokal, R.R., Michener, C.D. & University of Kansas, 1958. A Statistical Method for Evaluating Systematic Relationships, University of Kansas.
    [2] Jain, A.K. & Dubes, R.C., 1988. Algorithms for clustering data, Prentice-Hall, Inc..
    [3] Johnson, S.C., 1967. Hierarchical clustering schemes. Psychometrika, 32(3), pp.241–254.
    ...


Ultimate goals
==============

Reduce demand for prima ballerina projects
------------------------------------------

**Problem**: Scientific software is often developed to gain citations for
original publication through the use of the software implementing it.
Unfortunately such established procedure discourages contributions
to existing projects and fosters new projects to be developed from
scratch.

**Solution**: With easy ways to provide all-and-only relevant references
for used functionality within a large(r) framework, scientific
developers will prefer to contribute to already existing projects.

**Benefits**: As a result, scientific developers will immediately benefit
from adhering to proper development procedures (codebase structuring,
testing, etc) and already established delivery and deployment channels
existing projects already have.  This will increase efficiency and
standardization of scientific software development, thus addressing
many (if not all) core problems with scientific software development
everyone likes to bash about (reproducibility, longevity, etc.).

Adequately reference core libraries
-----------------------------------

**Problem**: Scientific software often, if not always, uses 3rd party
libraries (e.g., NumPy, SciPy, atlas) which might not even be visible
at the user level.  Therefore they are rarely referenced in the
publications despite providing the fundamental core for solving a
scientific problem at hands.

**Solution**: With automated bibliography compilation for all used
libraries, such projects and their authors would get a chance to
receive adequate citability.

**Benefits**: Adequate appreciation of the scientific software
developments.  Coupled with a solution for "prima ballerina" problem,
more contributions will flow into the core/foundational projects
making new methodological developments readily available to even wider
audiences without proliferation of the low quality scientific software.


Similar/related projects
========================

[sempervirens](https://github.com/njsmith/sempervirens) -- *an
experimental prototype for gathering anonymous, opt-in usage data for
open scientific software*.  Eventually in duecredit we aim either to
provide similar functionality (since we are collecting such
information as well) or just interface/report to sempervirens.
