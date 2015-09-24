#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 09-23-2015
Purpose: Automatic injection of bibliography entries for dipy module
#----------------------------------------------------------------
"""


from ..entries import Doi, BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    #http://nipy.org/dipy/cite.html#a-note-on-citing-our-work
    injector.add('dipy', None, Doi('10.3389/fninf.2014.00008'),
                    description='Dipy, a library for the analysis of diffusion MRI data.',
                    tags=['implementation'])

