# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.   Originates from datalad package distributed
#   under MIT license
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

import glob
import os
import logging
import sys
import platform
import tempfile

from six import binary_type
from os.path import exists, join as opj, isabs, expandvars, expanduser, abspath

from os.path import realpath
from functools import wraps

#
# Some useful variables
#
on_windows = platform.system() == 'Windows'
on_osx = platform.system() == 'Darwin'
on_linux = platform.system() == 'Linux'
try:
    on_debian_wheezy = platform.system() == 'Linux' \
                and platform.linux_distribution()[0] == 'debian' \
                and platform.linux_distribution()[1].startswith('7.')
except:  # pragma: no cover
    on_debian_wheezy = False


lgr = logging.getLogger("duecredit.utils")

#
# Little helpers
#


def is_interactive():
    """Return True if all in/outs are tty"""
    if any(not hasattr(inout, 'isatty') for inout in (sys.stdin, sys.stdout, sys.stderr)):
        lgr.warning("Assuming non interactive session since isatty found missing")
        return False
    # TODO: check on windows if hasattr check would work correctly and add value:
    #
    return sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()


def expandpath(path, force_absolute=True):
    """Expand all variables and user handles in a path.

    By default return an absolute path
    """
    path = expandvars(expanduser(path))
    if force_absolute:
        path = abspath(path)
    return path


def is_explicit_path(path):
    """Return whether a path explicitly points to a location

    Any absolute path, or relative path starting with either '../' or
    './' is assumed to indicate a location on the filesystem. Any other
    path format is not considered explicit."""
    path = expandpath(path, force_absolute=False)
    return isabs(path) \
        or path.startswith(os.curdir + os.sep) \
        or path.startswith(os.pardir + os.sep)

def rotree(path, ro=True, chmod_files=True):
    """To make tree read-only or writable

    Parameters
    ----------
    path : string
      Path to the tree/directory to chmod
    ro : bool, optional
      Either to make it R/O (default) or RW
    chmod_files : bool, optional
      Either to operate also on files (not just directories)
    """
    if ro:
        chmod = lambda f: os.chmod(f, os.stat(f).st_mode & ~stat.S_IWRITE)
    else:
        chmod = lambda f: os.chmod(f, os.stat(f).st_mode | stat.S_IWRITE | stat.S_IREAD)

    for root, dirs, files in os.walk(path, followlinks=False):
        if chmod_files:
            for f in files:
                fullf = opj(root, f)
                # might be the "broken" symlink which would fail to stat etc
                if exists(fullf):
                    chmod(fullf)
        chmod(root)


def rmtree(path, chmod_files='auto', *args, **kwargs):
    """To remove git-annex .git it is needed to make all files and directories writable again first

    Parameters
    ----------
    chmod_files : string or bool, optional
       Either to make files writable also before removal.  Usually it is just
       a matter of directories to have write permissions.
       If 'auto' it would chmod files on windows by default
    `*args` :
    `**kwargs` :
       Passed into shutil.rmtree call
    """
    # Give W permissions back only to directories, no need to bother with files
    if chmod_files == 'auto':
        chmod_files = on_windows

    if not os.path.islink(path):
        rotree(path, ro=False, chmod_files=chmod_files)
        shutil.rmtree(path, *args, **kwargs)
    else:
        # just remove the symlink
        os.unlink(path)


def rmtemp(f, *args, **kwargs):
    """Wrapper to centralize removing of temp files so we could keep them around

    It will not remove the temporary file/directory if DATALAD_TESTS_KEEPTEMP
    environment variable is defined
    """
    if not os.environ.get('DATALAD_TESTS_KEEPTEMP'):
        if not os.path.lexists(f):
            lgr.debug("Path %s does not exist, so can't be removed" % f)
            return
        lgr.log(5, "Removing temp file: %s" % f)
        # Can also be a directory
        if os.path.isdir(f):
            rmtree(f, *args, **kwargs)
        else:
            for i in range(10):
                try:
                    os.unlink(f)
                except OSError as e:
                    if i < 9:
                        sleep(0.1)
                        continue
                    else:
                        raise
                break
    else:
        lgr.info("Keeping temp file: %s" % f)

#
# Decorators
#

# Borrowed from pandas
# Copyright: 2011-2014, Lambda Foundry, Inc. and PyData Development Team
# License: BSD-3
def optional_args(decorator):
    """allows a decorator to take optional positional and keyword arguments.
        Assumes that taking a single, callable, positional argument means that
        it is decorating a function, i.e. something like this::

            @my_decorator
            def function(): pass

        Calls decorator with decorator(f, *args, **kwargs)"""

    @wraps(decorator)
    def wrapper(*args, **kwargs):
        def dec(f):
            return decorator(f, *args, **kwargs)

        is_decorating = not kwargs and len(args) == 1 and callable(args[0])
        if is_decorating:
            f = args[0]
            args = []
            return dec(f)
        else:
            return dec

    return wrapper


def never_fail(f):
    """Assure that function never fails -- all exceptions are caught"""
    @wraps(f)
    def wrapped_func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            lgr.warning("DueCredit internal failure while running %s: %r. "
                        "Please report to developers at https://github.com/duecredit/duecredit/issues"
                        % (f, e))

    if os.environ.get('DUECREDIT_ALLOW_FAIL', False):
        return f
    else:
        return wrapped_func


def borrowdoc(cls, methodname=None, replace=None):
    """Return a decorator to borrow docstring from another `cls`.`methodname`

    Common use is to borrow a docstring from the class's method for an
    adapter function (e.g. sphere_searchlight borrows from Searchlight)

    Examples
    --------
    To borrow `__repr__` docstring from parent class `Mapper`, do::

       @borrowdoc(Mapper)
       def __repr__(self):
           ...

    Parameters
    ----------
    cls
      Usually a parent class
    methodname : None or str
      Name of the method from which to borrow.  If None, would use
      the same name as of the decorated method
    replace : None or str, optional
      If not None, then not entire docstring gets replaced but only the
      matching to "replace" value string
    """

    def _borrowdoc(method):
        """Decorator which assigns to the `method` docstring from another
        """
        if methodname is None:
            other_method = getattr(cls, method.__name__)
        else:
            other_method = getattr(cls, methodname)
        if hasattr(other_method, '__doc__'):
            if not replace:
                method.__doc__ = other_method.__doc__
            else:
                method.__doc__ = method.__doc__.replace(replace, other_method.__doc__)
        return method
    return _borrowdoc

# TODO: just provide decorators for tempfile.mk* functions. This is ugly!
def get_tempfile_kwargs(tkwargs={}, prefix="", wrapped=None):
    """Updates kwargs to be passed to tempfile. calls depending on env vars
    """
    # operate on a copy of tkwargs to avoid any side-effects
    tkwargs_ = tkwargs.copy()

    # TODO: don't remember why I had this one originally
    # if len(targs)<2 and \
    if not 'prefix' in tkwargs_:
        tkwargs_['prefix'] = '_'.join(
            ['duecredit_temp'] +
            ([prefix] if prefix else []) +
            ([''] if (on_windows or not wrapped)
                  else [wrapped.__name__]))

    directory = os.environ.get('DUECREDIT_TESTS_TEMPDIR')
    if directory and 'dir' not in tkwargs_:
        tkwargs_['dir'] = directory

    return tkwargs_


@optional_args
def with_tempfile(t, content=None, **tkwargs):
    """Decorator function to provide a temporary file name and remove it at the end

    Parameters
    ----------
    mkdir : bool, optional (default: False)
        If True, temporary directory created using tempfile.mkdtemp()
    content : str or bytes, optional
        Content to be stored in the file created
    `**tkwargs`:
        All other arguments are passed into the call to tempfile.mk{,d}temp(),
        and resultant temporary filename is passed as the first argument into
        the function t.  If no 'prefix' argument is provided, it will be
        constructed using module and function names ('.' replaced with
        '_').

    To change the used directory without providing keyword argument 'dir' set
    DUECREDIT_TESTS_TEMPDIR.

    Examples
    --------

        @with_tempfile
        def test_write(tfile):
            open(tfile, 'w').write('silly test')
    """

    @wraps(t)
    def newfunc(*arg, **kw):

        tkwargs_ = get_tempfile_kwargs(tkwargs, wrapped=t)

        # if DUECREDIT_TESTS_TEMPDIR is set, use that as directory,
        # let mktemp handle it otherwise. However, an explicitly provided
        # dir=... will override this.
        mkdir = tkwargs_.pop('mkdir', False)

        filename = {False: tempfile.mktemp,
                    True: tempfile.mkdtemp}[mkdir](**tkwargs_)
        filename = realpath(filename)

        if content:
            with open(filename, 'w' + ('b' if isinstance(content, binary_type) else '')) as f:
                f.write(content)
        if __debug__:
            lgr.debug('Running %s with temporary filename %s',
                      t.__name__, filename)
        try:
            return t(*(arg + (filename,)), **kw)
        finally:
            # glob here for all files with the same name (-suffix)
            # would be useful whenever we requested .img filename,
            # and function creates .hdr as well
            lsuffix = len(tkwargs_.get('suffix', ''))
            filename_ = lsuffix and filename[:-lsuffix] or filename
            filenames = glob.glob(filename_ + '*')
            if len(filename_) < 3 or len(filenames) > 5:
                # For paranoid yoh who stepped into this already ones ;-)
                lgr.warning("It is unlikely that it was intended to remove all"
                            " files matching %r. Skipping" % filename_)
                return
            for f in filenames:
                try:
                    rmtemp(f)
                except OSError:
                    pass

    if tkwargs.get('mkdir', None) and content is not None:
        raise ValueError("mkdir=True while providing content makes no sense")

    return newfunc


#
# Context Managers
#


#
# Additional handlers
#
_sys_excepthook = sys.excepthook # Just in case we ever need original one

def setup_exceptionhook():
    """Overloads default sys.excepthook with our exceptionhook handler.

       If interactive, our exceptionhook handler will invoke
       pdb.post_mortem; if not interactive, then invokes default handler.
    """

    def _duecredit_pdb_excepthook(type, value, tb):

        if is_interactive():
            import traceback, pdb
            traceback.print_exception(type, value, tb)
            print
            pdb.post_mortem(tb)
        else:
            lgr.warn("We cannot setup exception hook since not in interactive mode")
            # we are in interactive mode or we don't have a tty-like
            # device, so we call the default hook
            #sys.__excepthook__(type, value, tb)
            _sys_excepthook(type, value, tb)

    sys.excepthook = _duecredit_pdb_excepthook

