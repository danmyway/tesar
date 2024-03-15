import argparse
import logging

from .dispatch.command import DispatchCommand
from .raw_dispatch.command import RawDispatchCommand

def main_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    DispatchCommand.add_command(subparsers)
    RawDispatchCommand.add_command(subparsers)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        '-d', '--debug',
        action="store_true",
        help="Turn on debugging.",
    )
    verbosity.add_argument(
        '-q', '--quiet',
        action="store_true",
        help="Run in quiet mode: show errors and failures only.",
    )
    return parser

def main(in_args):
    args = main_parser().parse_args(in_args)
    loglevel = logging.INFO
    logformat = "%(levelname)-8s: %(message)s"
    if args.debug:
        loglevel = logging.DEBUG
        logformat = "%(name)s(%(levelname)s): %(message)s"
    elif args.quiet:
        loglevel = logging.ERROR
    logging.basicConfig(
        level=loglevel,
        format=logformat,
    )
    command = args.command_class(args)
    return command()
