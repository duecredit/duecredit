#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 09-23-2015
Purpose: Automatic injection of bibliography entries for skimage module
#----------------------------------------------------------------
"""


from ..entries import Doi, BibTeX

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    #http://scikit-image.org
    injector.add('skimage', None, Doi('10.7717/peerj.453'),
                    description='scikit-image: Image processing in Python.',
                    tags=['implementation'])
