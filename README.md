# duecredit


[![Build Status](https://travis-ci.org/duecredit/duecredit.svg?branch=master)](https://travis-ci.org/duecredit/duecredit)
[![Coverage Status](https://coveralls.io/repos/duecredit/duecredit/badge.svg)](https://coveralls.io/r/duecredit/duecredit)
[![DOI](https://zenodo.org/badge/DOI/110.5281/zenodo.3376260.svg)](https://doi.org/10.5281/zenodo.3376260)
[![PyPI version fury.io](https://badge.fury.io/py/duecredit.svg)](https://pypi.python.org/pypi/duecredit/)

duecredit is being conceived to address the problem of inadequate
citation of scientific software and methods, and limited visibility of
donation requests for open-source software.

It provides a simple framework (at the moment for Python only) to
embed publication or other references in the original code so they are
automatically collected and reported to the user at the necessary
level of reference detail, i.e. only references for actually used
functionality will be presented back if software provides multiple
citeable implementations.

## Installation

Duecredit is easy to install via pip, simply type:
 
 `pip install duecredit`

## Examples

### To cite the modules and methods you are using 

You can already start "registering" citations using duecredit in your
Python modules and even registering citations (we call this approach "injections")
for modules which do not (yet) use duecredit.  duecredit will remain an optional
dependency, i.e. your software will work correctly even without duecredit installed.

For example, list citations of the modules and methods `yourproject` uses with few simple commands:
```bash
cd /path/to/yourmodule # for ~/yourproject
cd yourproject # change directory into where the main code base is
python -m duecredit yourproject.py
```
Or you can also display them in BibTex format, using:
```bash
duecredit summary --format=bibtex
```
See this gif animation for better illustration:
![Example](examples/duecredit_example.gif)


### To let others cite your software


For using duecredit in your software

1. Copy `duecredit/stub.py` to your codebase, e.g.

        wget -q -O /path/tomodule/yourmodule/due.py \
          https://raw.githubusercontent.com/duecredit/duecredit/master/duecredit/stub.py


    **Note** that it might be better to avoid naming it duecredit.py to avoid shadowing
    installed duecredit.

2. Then use `duecredit` import due and necessary entries in your code as

        from .due import due, Doi, BibTeX

     To provide reference for the entire module just use e.g.

         due.cite(Doi("1.2.3/x.y.z"), description="Solves all your problems", path="magicpy")

     To provide a reference for a function or a method, use `dcite` decorator

         @due.dcite(Doi("1.2.3/x.y.z"), description="Resolves constipation issue")
         def pushit():
             ...

    You can easily obtain DOI for your software using Zenodo.org and few other DOI providers.

References can also be entered as BibTeX entries

        due.cite(BibTeX("""
                @article{mynicearticle,
                title={A very cool paper},
                author={Happy, Author and Lucky, Author},
                journal={The Journal of Serendipitous Discoveries}
                }
                """), 
                description="Solves all your problems", path="magicpy")
        
## Now what
        
### Do the due

Once you obtained the references in the duecredit output, include them in in the references section of your paper or software, which used the cited software.
        
### Add injections for other existing modules

We hope that eventually this somewhat cruel approach will not be necessary. But
until other packages support duecredit "natively" we have provided a way to "inject"
citations for modules and/or functions and methods via injections: citations will be
added to the corresponding functionality upon those modules import.

All injections are collected under
[duecredit/injections](https://github.com/duecredit/duecredit/tree/master/duecredit/injections).
See any file there with `mod_` prefix for a complete example. But
overall it is just a regular Python module defining a function
`inject(injector)` which will then add new entries to the injector,
which will in turn add those entries to the duecredit whenever the
corresponding module gets imported.


## User-view


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
    - Scientific tools library / numpy (v 1.10.4) [1]
    - Scientific tools library / scipy (v 0.14) [2]
      - Single linkage hierarchical clustering / scipy.cluster.hierarchy:linkage (v 0.14) [3]

    2 packages cited
    0 modules cited
    1 function cited

    References
    ----------

    [1] Van Der Walt, S., Colbert, S.C. & Varoquaux, G., 2011. The NumPy array: a structure for efficient numerical computation. Computing in Science & Engineering, 13(2), pp.22–30.
    [2] Jones, E. et al., 2001. SciPy: Open source scientific tools for Python.
    [3] Sibson, R., 1973. SLINK: an optimally efficient algorithm for the single-link cluster method. The Computer Journal, 16(1), pp.30–34.


Incremental runs of various software would keep enriching that file.
Then you can use `duecredit summary` command to show that information
again (stored in `.duecredit.p` file) or export it as a BibTeX file
ready for reuse, e.g.:

    $> duecredit summary --format=bibtex
    @article{van2011numpy,
            title={The NumPy array: a structure for efficient numerical computation},
            author={Van Der Walt, Stefan and Colbert, S Chris and Varoquaux, Gael},
            journal={Computing in Science \& Engineering},
            volume={13},
            number={2},
            pages={22--30},
            year={2011},
            publisher={AIP Publishing}
            }
    @Misc{JOP+01,
          author =    {Eric Jones and Travis Oliphant and Pearu Peterson and others},
          title =     {{SciPy}: Open source scientific tools for {Python}},
          year =      {2001--},
          url = "http://www.scipy.org/",
          note = {[Online; accessed 2015-07-13]}
        }
    @article{sibson1973slink,
            title={SLINK: an optimally efficient algorithm for the single-link cluster method},
            author={Sibson, Robin},
            journal={The Computer Journal},
            volume={16},
            number={1},
            pages={30--34},
            year={1973},
            publisher={Br Computer Soc}
        }


and if by default only references for "implementation" are listed, we
can enable listing of references for other tags as well (e.g. "edu"
depicting instructional materials -- textbooks etc. on the topic):

    $> DUECREDIT_REPORT_TAGS=* duecredit summary
    
    DueCredit Report:
    - Scientific tools library / numpy (v 1.10.4) [1]
    - Scientific tools library / scipy (v 0.14) [2]
      - Hierarchical clustering / scipy.cluster.hierarchy (v 0.14) [3, 4, 5, 6, 7, 8, 9]
      - Single linkage hierarchical clustering / scipy.cluster.hierarchy:linkage (v 0.14) [10, 11]

    2 packages cited
    1 module cited
    1 function cited

    References
    ----------

    [1] Van Der Walt, S., Colbert, S.C. & Varoquaux, G., 2011. The NumPy array: a structure for efficient numerical computation. Computing in Science & Engineering, 13(2), pp.22–30.
    [2] Jones, E. et al., 2001. SciPy: Open source scientific tools for Python.
    [3] Sneath, P.H. & Sokal, R.R., 1962. Numerical taxonomy. Nature, 193(4818), pp.855–860.
    [4] Batagelj, V. & Bren, M., 1995. Comparing resemblance measures. Journal of classification, 12(1), pp.73–90.
    [5] Sokal, R.R., Michener, C.D. & University of Kansas, 1958. A Statistical Method for Evaluating Systematic Relationships, University of Kansas.
    [6] Jain, A.K. & Dubes, R.C., 1988. Algorithms for clustering data, Prentice-Hall, Inc..
    [7] Johnson, S.C., 1967. Hierarchical clustering schemes. Psychometrika, 32(3), pp.241–254.
    [8] Edelbrock, C., 1979. Mixture model tests of hierarchical clustering algorithms: the problem of classifying everybody. Multivariate Behavioral Research, 14(3), pp.367–384.
    [9] Fisher, R.A., 1936. The use of multiple measurements in taxonomic problems. Annals of eugenics, 7(2), pp.179–188.
    [10] Gower, J.C. & Ross, G., 1969. Minimum spanning trees and single linkage cluster analysis. Applied statistics, pp.54–64.
    [11] Sibson, R., 1973. SLINK: an optimally efficient algorithm for the single-link cluster method. The Computer Journal, 16(1), pp.30–34.
    
The `DUECREDIT_REPORT_ALL` flag allows one to output all the references
for the modules that lack objects or functions with citations.
Compared to the previous example, the following output additionally 
shows a reference for scikit-learn since `example_scipy.py` uses 
an uncited function from that package.

    $> DUECREDIT_REPORT_TAGS=* DUECREDIT_REPORT_ALL=1 duecredit summary

    DueCredit Report:
    - Scientific tools library / numpy (v 1.10.4) [1]
    - Scientific tools library / scipy (v 0.14) [2]
      - Hierarchical clustering / scipy.cluster.hierarchy (v 0.14) [3, 4, 5, 6, 7, 8, 9]
      - Single linkage hierarchical clustering / scipy.cluster.hierarchy:linkage (v 0.14) [10, 11]
    - Machine Learning library / sklearn (v 0.15.2) [12]

    3 packages cited
    1 module cited
    1 function cited

    References
    ----------

    [1] Van Der Walt, S., Colbert, S.C. & Varoquaux, G., 2011. The NumPy array: a structure for efficient numerical computation. Computing in Science & Engineering, 13(2), pp.22–30.
    [2] Jones, E. et al., 2001. SciPy: Open source scientific tools for Python.
    [3] Sneath, P.H. & Sokal, R.R., 1962. Numerical taxonomy. Nature, 193(4818), pp.855–860.
    ...

## Tags


You are welcome to introduce new tags specific for your citations but we hope
that for consistency across projects, you would use following tags

- `implementation` (default) — an implementation of the cited method
- `reference-implementation` — the original implementation (ideally by
  the authors of the paper) of the cited method
- `another-implementation` — some other implementation of
   the method, e.g. if you would like to provide citation for another
   implementation of the method you have implemented in your code and for
   which you have already provided `implementation` or
   `reference-implementation` tag
- `use` — publications demonstrating a worthwhile noting use of the
  method
- `edu` — tutorials, textbooks and other materials useful to learn
  more about cited functionality
- `donate` — should be commonly used with Url entries to point to the
  websites  describing how to contribute some funds to the referenced
  project
- `funding` — to point to the sources of funding which provided support
  for a given functionality implementation and/or method development
- `dataset` - for datasets

## Ultimate goals


### Reduce demand for prima ballerina projects

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

### Adequately reference core libraries

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


## Similar/related projects

[sempervirens](https://github.com/njsmith/sempervirens) -- *an
experimental prototype for gathering anonymous, opt-in usage data for
open scientific software*.  Eventually in duecredit we aim either to
provide similar functionality (since we are collecting such
information as well) or just interface/report to sempervirens.

[citepy](https://github.com/clbarnes/citepy) -- Easily cite software libraries using information from automatically gathered from their package repository.

## Currently used by

This is a running list of projects that use DueCredit natively. If you
are using DueCredit, or plan to use it, please consider sending a pull
request and add your project to this list. Thanks to
[@fedorov](https://github.com/fedorov) for the idea.

- [PyMVPA](http://www.pymvpa.org)
- [fatiando](https://github.com/fatiando/fatiando)
- [Nipype](https://github.com/nipy/nipype)
- [QInfer](https://github.com/QInfer/python-qinfer)
- [shablona](https://github.com/uwescience/shablona)
- [gfusion](https://github.com/mvdoc/gfusion)
- [pybids](https://github.com/INCF/pybids)
- [Quickshear](https://github.com/nipy/quickshear)
- [meqc](https://github.com/emdupre/meqc)
- [MDAnalysis](https://www.mdanalysis.org)
- [bctpy](https://github.com/aestrivex/bctpy)
- [TorchIO](https://github.com/fepegar/torchio)

Last updated 2020-04-07.
