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

2. Then use in your code as

    from .due import due, Doi

   1. To provide reference for the entire module just use e.g.

       due.cite(Doi("1.2.3/x.y.z"), use="Solves all your problems", level="module xyz")

   2. To provide a reference for a function or a method, use dcite decorator

       @due.dcite(Doi("1.2.3/x.y.z"), use="Resolves constipation issue")
       def pushit():
           ...

3. Then whenever anyone runs their analysis which uses your code and sets `DUECREDIT_ENABLE=yes`
   environment variable, and invokes any of the cited function/methods, at the end of the run
   all collected bibliography will appear.  Moreover you can use `duecredit summary` command
   to show that information again (stored in `.duecredit.p` file) or export it as a BibTeX file
   ready for reuse


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


HOWTO
=====

Interaction
-----------

By default, duecredit should not have any notable impact on any
computation, but with easy switch (e.g. via exporting environment
variable DUECREDIT_ENABLE=1) upon exit (or via an explicit call) it
should collect any related references at runtime and export such a
list of references.

Interface
---------

Interface should be minimalistic, so it should be possible to provide
a small stub for projects to add to their code in case when the full
mighty duecredit is N/A.


# TODO -- actually think it would be benefitial/feasible
#
# May be we should just retrospect all classes and extract from the
# embedded fields/documentation?
#
# Or follow py.test approach and provide tiny encoded beastie people
# could carry along?

try:
  import duecredit
except ImportError:
  # oopsy daisy
  class duecredit(object):
    def add(*args, **kwargs):  pass
    # TODO: would not work as a decorator
	def cite(*args, **kwargs): pass
    load = add


Specification
-------------


Module level
~~~~~~~~~~~~

>>> from duecredit import due, BibTeX, Donate
>>>
>>> # Add XXX00 reference
>>> due.add(BibTeX("""{XXX00, ...}"""), use="module blah")
>>>
>>> # and/or load multiple from a file
>>> due.load('/home/soul/deep/good_intentions.bib')
>>>
>>> # Reference XXX00 entry.  If not pre-loaded
>>> # a complete BibTeX or some other entry could be
>>> # provided in place of the key
>>> due(Donate(url="http://alimony.money/kid#1"))


Function/Method level
~~~~~~~~~~~~~~~~~~~~~

# Could provide additional description for the particular
# functionality

@due.dec('XXX00', use="Provides an answer for meaningless existence")
def purpose_of_life():
    return None

class Children(object):
     # Conception is usually way too easy and is just for pleasure,
     # thus not worth referencing
     def __init__(self):
         pass

     @due.dec(Donate("http://social.support"))
     def birth(self, gender):
         pass

   @due.dec(BibTeX("""{YYY00, title='Memoir of ...', ...}"""))
     def tough_life(self, reincarnations=1, ...):
         pass


Output
------



