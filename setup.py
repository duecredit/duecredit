#!/usr/bin/env python
"""
pubtrace -- trace software for the publications
"""

import os
import sys

from datetime import datetime
from distutils.core import setup
from pkgutil import walk_packages
from subprocess import Popen, PIPE

# Adopted from citeproc-py
#  License: BSD-2
#  Copyright 2011-2013 Brecht Machiels

PACKAGE = 'pubtrace'
PACKAGE_ABSPATH = os.path.abspath(PACKAGE)
VERSION_FILE = PACKAGE + '/version.py'

# retrieve the version number from git or VERSION_FILE
# inspired by http://dcreager.net/2010/02/10/setuptools-git-version-numbers/

try:
    print('Attempting to get version number from git...')
    git = Popen(['git', 'describe', '--abbrev=4', '--dirty'],
                stdout=PIPE, stderr=sys.stderr)
    if git.wait() != 0:
        raise OSError
    line = git.stdout.readlines()[0]
    __version__ = line.strip()[1:].decode('ascii')
    __release_date__ = datetime.now().strftime('%b %d %Y, %H:%M:%S')
    with open(VERSION_FILE, 'w') as version_file:
        version_file.write("__version__ = '{}'\n".format(__version__))
        version_file.write("__release_date__ = '{}'\n".format(__release_date__))
except OSError as e:
    print('Assume we are running from a source distribution.')
    # read version from VERSION_FILE
    with open(VERSION_FILE) as version_file:
        code = compile(version_file.read(), VERSION_FILE, 'exec')
        exec(code)

with open('README.rst') as file:
    README = file.read()


def find_packages(path, prefix):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


setup(
    name='pubtrace',
    version=__version__,
    packages=list(find_packages([PACKAGE_ABSPATH], PACKAGE)),
    package_data={PACKAGE: []},
    scripts=[],
    requires=[],
    provides=[PACKAGE],
    #test_suite='nose.collector',

    author='Yaroslav Halchenko',
    author_email='yoh@onerussian.com',
    description='Publications tracer',
    long_description=README,
    url='https://github.com/yarikoptic/pubtrace',
    keywords='citation tracing', 
    license='2-clause BSD License',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Printing',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
