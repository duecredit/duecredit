#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 09-21-2015
Purpose:  Automatic injection of bibliography entries for psychopy module
#----------------------------------------------------------------
"""


from ..entries import Doi, BibTeX, Url

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('psychopy', None, Doi('doi:10.1016/j.jneumeth.2006.11.017'),
                 description="PsychoPy -- Psychophysics software in Python.",
                 tags=['implementation'])
    
    injector.add('psychopy', None, Doi('10.3389/neuro.11.010.2008'),
                 description="Generating stimuli for neuroscience using PsychoPy.",
                 tags=['implementation'])
