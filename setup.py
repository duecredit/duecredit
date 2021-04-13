#!/usr/bin/env python
"""
duecredit -- publications (donations, etc) tracer
"""

import os.path
import re
import sys

from datetime import datetime
from subprocess import Popen, PIPE

from setuptools import find_packages, setup

# Adopted from citeproc-py
#  License: BSD-2
#  Copyright 2011-2013 Brecht Machiels

PACKAGE = 'duecredit'
VERSION_FILE = PACKAGE + '/version.py'

# retrieve the version number from git or VERSION_FILE
# inspired by http://dcreager.net/2010/02/10/setuptools-git-version-numbers/

try:
    if os.path.exists('debian/copyright'):
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
            exec(code, locals(), globals())
    else:
        __version__ = '0.0.0.dev'
print("Version: %s" % __version__)

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()

setup(
    name=PACKAGE,
    version=__version__,
    packages=find_packages(),
    scripts=[],
    install_requires=['requests', 'citeproc-py>=0.4', 'six'],
    extras_require={
        'tests': [
            'pytest',
            'vcrpy', 'contextlib2'
        ]
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
             'duecredit=duecredit.cmdline.main:main',
        ],
    },
    author='Yaroslav Halchenko, Matteo Visconti di Oleggio Castello',
    author_email='yoh@onerussian.com',
    description='Publications (and donations) tracer',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/duecredit/duecredit',
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
