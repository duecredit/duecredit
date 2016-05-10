#!/usr/bin/env python
"""
duecredit -- publications (donations, etc) tracer
"""

import re
import os
import sys
import re

from datetime import datetime
from setuptools import setup
from pkgutil import walk_packages
from subprocess import Popen, PIPE
from os.path import exists

# Adopted from citeproc-py
#  License: BSD-2
#  Copyright 2011-2013 Brecht Machiels

PACKAGE = 'duecredit'
PACKAGE_ABSPATH = os.path.abspath(PACKAGE)
VERSION_FILE = PACKAGE + '/version.py'

# retrieve the version number from git or VERSION_FILE
# inspired by http://dcreager.net/2010/02/10/setuptools-git-version-numbers/

try:
    if exists('debian/copyright'):
        print('Generating version.py out of debian/copyright information')
        # building debian package. Deduce version from debian/copyright
        with open('debian/changelog', 'r') as f:
            lines = f.readlines()
        __version__ = re.sub('(.*)-(.*?)$', r'\1.debian\2',
                             lines[0].split()[1].strip('()')
                             ).replace('-', '.')
        # TODO: unify format whenever really bored ;)
        __release_date__ = re.sub('^ -- .*>\s*(.*)', r'\1',
                                  list(filter(lambda x: x.startswith(' -- '), lines))[0].rstrip())
    else:
        print('Attempting to get version number from git...')
        git = Popen(['git', 'describe', '--abbrev=4', '--dirty'],
                    stdout=PIPE, stderr=sys.stderr)
        if git.wait() != 0:
            raise OSError
        line = git.stdout.readlines()[0].strip().decode('ascii')
        if line.count('-') >= 2:
            # we should parse it to make version compatible with PEP440
            # unfortunately we wouldn't be able to include git treeish
            # into the version, and thus can have collisions. So let's
            # release from master only
            line = '.dev'.join(line.split('-')[:2])
        __version__ = line
        __release_date__ = datetime.now().strftime('%b %d %Y, %H:%M:%S')
    with open(VERSION_FILE, 'w') as version_file:
        version_file.write("__version__ = '{0}'\n".format(__version__))
        version_file.write("__release_date__ = '{0}'\n".format(__release_date__))
except OSError as e:
    print('Assume we are running from a source distribution.')
    # read version from VERSION_FILE
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE) as version_file:
            code = compile(version_file.read(), VERSION_FILE, 'exec')
            exec(code, {}, {})
    else:
        __version__ = '0.0.0.dev'

with open('README.md') as file:
    README = file.read()

def find_packages(path, prefix):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


setup(
    name=PACKAGE,
    version=__version__,
    packages=list(find_packages([PACKAGE_ABSPATH], PACKAGE)),
    scripts=[],
    install_requires=['requests', 'citeproc-py', 'six'],
    extras_require={
        'tests': [
            'mock',
            'nose>=1.3.4',
            'vcrpy', 'contextlib2'
        ]
    },
    include_package_data=True,
    provides=[PACKAGE],
    #test_suite='nose.collector',
    entry_points={
        'console_scripts': [
             'duecredit=duecredit.cmdline.main:main',
        ],
    },
    author='Yaroslav Halchenko, Matteo Visconti di Oleggio Castello',
    author_email='yoh@onerussian.com',
    description='Publications (and donations) tracer',
    long_description="""\
duecredit is being conceived to address the problem of inadequate
citation of scientific software and methods, and limited visibility of
donation requests for open-source software.

It provides a simple framework (at the moment for Python only) to
embed publication or other references in the original code so they are
automatically collected and reported to the user at the necessary
level of reference detail, i.e. only references for actually used
functionality will be presented back if software provides multiple
citeable implementations.

To get a sense of what duecredit is about, run for example shipped along
example script, or your analysis script with `-m duecredit`, e.g.

    python -m duecredit examples/example_scipy.py

""",
    url='https://github.com/duecredit/duecredit',
    # Download URL will point to the latest release, thus suffixes removed
    download_url='https://github.com/duecredit/duecredit/releases/tag/%s'
        % re.sub('-.*$', '', __version__),
    keywords=['citation tracing'],
    license='2-clause BSD License',
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
