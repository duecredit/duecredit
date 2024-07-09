# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Automatic injection of bibliography entries for nibabel module
"""


from ..entries import Doi

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('nibabel', None,
                 Doi('10.5281/zenodo.60847'),
                 cite_module=True,
                 description="I/O library to access to common neuroimaging file formats",
                 tags=['implementation'])
