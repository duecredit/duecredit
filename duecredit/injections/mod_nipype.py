#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 09-23-2015
Purpose: Automatic injection of bibliography entries for nipype module
#----------------------------------------------------------------
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

    #http://www.fil.ion.ucl.ac.uk/spm/
    # not sure what primary spm citation is...couldn't find on website. 
    #injector.add('nipype.interfaces', 'spm', Doi(''),
                    #description='',
                    #tags=['implementation'])

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
