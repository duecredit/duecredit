#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 09-23-2015
Purpose: Automatic injection of bibliography entries for mne module
#----------------------------------------------------------------
"""


from ..entries import Doi, BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    #http://martinos.org/mne/stable/cite.html
    injector.add('mne', None, Doi('10.1016/j.neuroimage.2013.10.027'),
                    description='MNE software for processing MEG and EEG data.',
                    tags=['implementation'])
    injector.add('mne', None, Doi('10.3389/fnins.2013.00267'),
                    description='MEG and EEG data analysis with MNE-Python.',
                    tags=['implementation'])
