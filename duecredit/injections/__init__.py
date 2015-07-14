# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Facility to automagically decorate with references other modules
"""

__docformat__ = 'restructuredtext'

from .injector import *
from ..entries import Doi, BibTeX

injector = DueCreditInjector()

# TODO: if collection grows we might need to delay definitions of those, e.g. to defer to instantiation of them per each module etc
injector.add('scipy', None, BibTeX("""
@Misc{JOP+01,
  author =    {Eric Jones and Travis Oliphant and Pearu Peterson and others},
  title =     {{SciPy}: Open source scientific tools for {Python}},
  year =      {2001--},
  url = "http://www.scipy.org/",
  note = {[Online; accessed 2015-07-13]}
}"""), use="Scientific tools library")
