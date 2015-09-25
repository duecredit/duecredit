# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
Automatic injection of bibliography entries for nipype module
"""


from ..entries import Doi, BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    #http://nipy.org/nipype/about.html
    injector.add('nipype', None, Doi('10.3389/fninf.2011.00013'),
                    description='Nipype: a flexible, lightweight and extensible neuroimaging data processing framework in Python',
                    tags=['implementation'])

    #http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/
    injector.add('nipype.interfaces', 'fsl', Doi('10.1016/j.neuroimage.2004.07.051'),
                    description='Advances in functional and structural MR image analysis and implementation as FSL',
                    tags=['implementation'])
    injector.add('nipype.interfaces', 'fsl', Doi('10.1016/j.neuroimage.2008.10.055'),
                    description='Bayesian analysis of neuroimaging data in FSL',
                    tags=['implementation'])
    injector.add('nipype.interfaces', 'fsl', Doi('10.1016/j.neuroimage.2011.09.015'),
                    description='FSL.',
                    tags=['implementation'])

    #http://www.fil.ion.ucl.ac.uk/spm
    injector.add('nipype.interfaces', 'spm', BibTeX("""
        @book{FrackowiakFristonFrithDolanMazziotta1997,
            author={R.S.J. Frackowiak, K.J. Friston, C.D. Frith, R.J. Dolan, and J.C. Mazziotta},
            title={Human Brain Function},
            publisher={Academic Press USA}
            year={1997},
            }
        """), description='The fundamental text on Statistical Parametric Mapping (SPM)',
        tags=['implementation'])

    #http://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferMethodsCitation
    # there are a bunch, not sure what is primary
    #injector.add('nipype.interfaces', 'freesurfer', Doi(''),
                    #description='',
                    #tags=['implementation'])

    #http://afni.nimh.nih.gov/afni/about/citations/
    # there are a bunch, not sure what is primary
    #injector.add('nipype.interfaces', 'afni', Doi(''),
                    #description='',
                    #tags=['implementation'])
