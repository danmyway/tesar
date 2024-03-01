import argparse

from .dispatch.command import DispatchCommand

def main_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    DispatchCommand.add_command(subparsers)
    return parser

def main(in_args):
    args = main_parser().parse_args(in_args)
    command = args.command_class(args)
    return command()
