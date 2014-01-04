========
duecredit
========

duecredit is being conceived to address the problem of inadequate
citation of scientific software and methods.

It provides a simple framework (at the moment for Python only) to
embed references in the original code so they would be automatically
collected and reported to the user at the necessary level of reference
detail, i.e. only references for actually used functionality will be
presented back if software provides multiple citeable implementations.


Ultimate vision(s)
=================

No need for prima ballerina projects
------------------------------------

Problem: Scientific software is developed often to gain citations for
original publication through the use of the software implementing it.
Unfortunately such established procedure discourages contributions to
the existing projects and favors establishing new projects developed
from scratch.

Solution: With easy ways to provide all-and-only relevant references
for used functionality within a large(r) framework scientific
developers would prefer to contribute to already existing projects.

Benefits: As a result, they would immediately benefit from adhering to
proper development procedures (codebase and data structuring, testing,
etc) and already established delivery and deployment channels those
projects already have.  This will increase efficiency and
standardization of scientific software development, thus addressing
many (if not all) of the core problems with scientific software
everyone likes to bash about (reproducibility, longevity, etc).

Core libraries adequately referenced
------------------------------------

Problem: Scientific software often if not always uses 3rd party
libraries (e.g. NumPy, SciPy, atlas) which might not even be visible
at the user level.  Therefore they are rarely referenced in the
publications despite providing fundamental core for solving a
scientific problem at hands.

Solution: With automated bibliography compilation for all used
libraries, such core libraries would get a chance to receive adequate
citability.

Benefits: Adequate appreciation of the scientific software
developments.  Coupled with a solution for "prima ballerina" problem,
more contributions would flow into the core/foundational projects
making new methodological developments readily available to even wider
audiences.


HOWTO
=====

Interaction
-----------

In default duecredit should not impact any running computation, but
with easy switch (e.g. via exporting environment variable
DUECREDIT_ENABLE=1) upon exit (or via an explicit call) it would
provide a list of references collected for the runtime.


Interface
---------

Interface should be minimalistic, so it should be possible to provide
a tiny stub for people to add to their code in case when the full
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
import duecredit

# Add reference
duecredit.add(bib="""{XXX00, ...}""")

# and/or load multiple from a file
duecredit.load('/home/soul/deep/good_intentions.bib')

duecredit.cite('XXX00', use="") # Cite entire module


Function/Method level
~~~~~~~~~~~~~~~~~~~~~

# Could provide additional description for the particular
# functionality

@duecredit.dcite('XXX00', use="Provides an answer for meaningless existence")
def purpose_of_life():
    return None

class Children(object):
     # Conception is usually way too easy to be referenced
     def __init__(self):
	     pass

     @duecredit.dcite('BirthCertificate')
     def birth(self, gender):
	     pass


Output
------



