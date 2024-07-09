# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
"""
from __future__ import annotations

__docformat__ = "restructuredtext"

import argparse
import re
import sys
from typing import Any, Pattern

from ..utils import is_interactive


class HelpAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,  # noqa: U100
        values,  # noqa: U100
        option_string: str | None = None,
    ) -> None:
        # import pydb; pydb.debugger()

        if is_interactive() and option_string == "--help":
            # lets use the manpage on mature systems ...
            try:
                import subprocess

                subprocess.check_call(
                    "man %s 2> /dev/null" % parser.prog.replace(" ", "-"),
                    shell=True,
                )
                sys.exit(0)
            except (subprocess.CalledProcessError, OSError):
                # ...but silently fall back if it doesn't work
                pass
        if option_string == "-h":
            helpstr = "%s\n%s" % (
                parser.format_usage(),
                "Use '--help' to get more comprehensive information.",
            )
        else:
            helpstr = parser.format_help()
        # better for help2man
        helpstr = re.sub(r"optional arguments:", "options:", helpstr)
        # yoh: TODO for duecredit + help2man
        # helpstr = re.sub(r'positional arguments:\n.*\n', '', helpstr)
        # convert all heading to have the first character uppercase
        headpat = re.compile(r"^([a-z])(.*):$", re.MULTILINE)
        helpstr = re.sub(
            headpat, lambda match: rf"{match[1].upper()}{match[2]}:", helpstr
        )
        # usage is on the same line
        helpstr = re.sub(r"^usage:", "Usage:", helpstr)
        if option_string == "--help-np":
            usagestr = re.split(r"\n\n[A-Z]+", helpstr, maxsplit=1)[0]
            usage_length = len(usagestr)
            usagestr = re.subn(r"\s+", " ", usagestr.replace("\n", " "))[0]
            helpstr = "{}\n{}".format(usagestr, helpstr[usage_length:])
        print(helpstr)
        sys.exit(0)


class LogLevelAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,  # noqa: U100
        namespace: argparse.Namespace,  # noqa: U100
        values,
        option_string: str | None = None,  # noqa: U100
    ) -> None:
        from ..log import LoggerHelper

        LoggerHelper().set_level(level=values)


def parser_add_common_args(
    parser: argparse.ArgumentParser, pos=None, opt=None, **kwargs: Any
) -> None:
    from . import common_args

    for i, args in enumerate((pos, opt)):
        if args is None:
            continue
        for arg in args:
            arg_tmpl = getattr(common_args, arg)
            arg_kwargs = arg_tmpl[2].copy()
            arg_kwargs.update(kwargs)
            if i:
                parser.add_argument(*arg_tmpl[i], **arg_kwargs)
            else:
                parser.add_argument(arg_tmpl[i], **arg_kwargs)


def parser_add_common_opt(
    parser: argparse.ArgumentParser, opt, names=None, **kwargs
) -> None:
    from . import common_args

    opt_tmpl = getattr(common_args, opt)
    opt_kwargs = opt_tmpl[2].copy()
    opt_kwargs.update(kwargs)
    if names is None:
        parser.add_argument(*opt_tmpl[1], **opt_kwargs)
    else:
        parser.add_argument(*names, **opt_kwargs)


class RegexpType:
    """Factory for creating regular expression types for argparse

    DEPRECATED AFAIK -- now things are in the config file...
    but we might provide a mode where we operate solely from cmdline
    """

    def __call__(self, string: str | None) -> Pattern[str] | None:
        if string:
            return re.compile(string)
        else:
            return None
