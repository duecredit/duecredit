# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Automatic injection of bibliography entries for nipy module
"""

from ..entries import Doi

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('nipy', None, Doi('10.1016/S1053-8119(09)72223-2'),
                 description="Library fMRI data analysis",
                 tags=['implementation'])

    for f, d in [('spectral_decomposition', 'PCA decomposition of symbolic HRF shifted over time'),
                 ('taylor_approx', 'A Taylor series approximation of an HRF shifted over time')]:
        injector.add('nipy.modalities.fmri.fmristat.hrf', f, Doi('10.1006/nimg.2002.1096'),
            description=d, tags=['implementation'])