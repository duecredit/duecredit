# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
Automatic injection of bibliography entries for matplotlib module
"""

from ..entries import Doi, BibTeX


# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None

bib_str = """
@Article{Hunter:2007,
  Author    = {Hunter, J. D.},
  Title     = {Matplotlib: A 2D graphics environment},
  Journal   = {Computing in Science \\& Engineering},
  Volume    = {9},
  Number    = {3},
  Pages     = {90--95},
  abstract  = {Matplotlib is a 2D graphics package used for Python for
  application development, interactive scripting, and publication-quality
  image generation across user interfaces and operating systems.},
  publisher = {IEEE COMPUTER SOC},
  doi       = {10.1109/MCSE.2007.55},
  year      = 2007
}
""".strip()


def inject(injector):
    injector.add("matplotlib", None, BibTeX(bib_str), description="Plotting with Python", tags=["implementation"])

    doi_prefix = "10.5281/zenodo."

    # latest version
    injector.add(
        "matplotlib", None, Doi(doi_prefix + "2893252"),
        description="Plotting with Python", tags=["implementation"]
    )

