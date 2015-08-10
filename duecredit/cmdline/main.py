# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.   Originates from datalad package distributed
#   under MIT license
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""""""

__docformat__ = 'restructuredtext'


import argparse
import logging
import sys
import textwrap

from .. import __version__
from ..log import lgr

import duecredit.cmdline as duecmd
from . import helpers

from ..utils import setup_exceptionhook

def _license_info():
    return """\
Copyright (c) 2015 Yaroslav Halchenko, Matteo Visconti di Oleggio Castello.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the copyright holder.
"""

def get_commands():
    return sorted([c for c in dir(duecmd) if c.startswith('cmd_')])

def setup_parser():
    # setup cmdline args parser
    # main parser
    parser = argparse.ArgumentParser(
                    fromfile_prefix_chars='@',
                    # usage="%(prog)s ...",
                    description="""\
    DueCredit simplifies citation of papers describing methods, software and data used by any given analysis script/pipeline.

    """,
                    epilog='"Your Credit is Due"',
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    add_help=False
                )
    # common options
    helpers.parser_add_common_opt(parser, 'help')
    helpers.parser_add_common_opt(parser, 'log_level')
    helpers.parser_add_common_opt(parser,
                                  'version',
                                  version='duecredit %s\n\n%s' % (__version__,
                                                              _license_info()))
    if __debug__:
        parser.add_argument(
            '--dbg', action='store_true', dest='common_debug',
            help="do not catch exceptions and show exception traceback")

    # yoh: atm we only dump to console.  Might adopt the same separation later on
    #      and for consistency will call it --verbose-level as well for now
    # log-level is set via common_opts ATM
    # parser.add_argument('--log-level',
    #                     choices=('critical', 'error', 'warning', 'info', 'debug'),
    #                     dest='common_log_level',
    #                     help="""level of verbosity in log files. By default
    #                          everything, including debug messages is logged.""")
    #parser.add_argument('-l', '--verbose-level',
    #                    choices=('critical', 'error', 'warning', 'info', 'debug'),
    #                    dest='common_verbose_level',
    #                    help="""level of verbosity of console output. By default
    #                         only warnings and errors are printed.""")


    # subparsers
    subparsers = parser.add_subparsers()
    # for all subcommand modules it can find
    cmd_short_description = []
    for cmd in get_commands():
        cmd_name = cmd[4:]
        subcmdmod = getattr(__import__('duecredit.cmdline',
                                       globals(), locals(),
                                       [cmd], 0),
                            cmd)
        # deal with optional parser args
        if 'parser_args' in subcmdmod.__dict__:
            parser_args = subcmdmod.parser_args
        else:
            parser_args = dict()
        # use module description, if no explicit description is available
        if not 'description' in parser_args:
            parser_args['description'] = subcmdmod.__doc__
        # create subparser, use module suffix as cmd name
        subparser = subparsers.add_parser(cmd_name, add_help=False, **parser_args)
        # all subparser can report the version
        helpers.parser_add_common_opt(
                subparser, 'version',
                version='duecredit %s %s\n\n%s' % (cmd_name, __version__,
                                                 _license_info()))
        # our own custom help for all commands
        helpers.parser_add_common_opt(subparser, 'help')
        helpers.parser_add_common_opt(subparser, 'log_level')
        # let module configure the parser
        subcmdmod.setup_parser(subparser)
        # logger for command

        # configure 'run' function for this command
        subparser.set_defaults(func=subcmdmod.run,
                               logger=logging.getLogger('duecredit.%s' % cmd))
        # store short description for later
        sdescr = getattr(subcmdmod, 'short_description',
                         parser_args['description'].split('\n')[0])
        cmd_short_description.append((cmd_name, sdescr))

    # create command summary
    cmd_summary = []
    for cd in cmd_short_description:
        cmd_summary.append('%s\n%s\n\n' \
                           % (cd[0],
                              textwrap.fill(cd[1], 75,
                              initial_indent=' ' * 4,
                              subsequent_indent=' ' * 4)))
    parser.description = '%s\n%s\n\n%s' \
            % (parser.description,
               '\n'.join(cmd_summary),
               textwrap.fill("""\
    Detailed usage information for individual commands is
    available via command-specific help options, i.e.:
    %s <command> --help""" % sys.argv[0],
                                75, initial_indent='',
                                subsequent_indent=''))
    return parser

def main(args=None):
    parser = setup_parser()
    # parse cmd args
    args = parser.parse_args(args)

    # run the function associated with the selected command
    if args.common_debug:
        # So we could see/stop clearly at the point of failure
        setup_exceptionhook()
        args.func(args)
    else:
        # Otherwise - guard and only log the summary. Postmortem is not
        # as convenient if being caught in this ultimate except
        try:
            args.func(args)
        except Exception as exc:
            lgr.error('%s (%s)' % (str(exc), exc.__class__.__name__))
            sys.exit(1)
