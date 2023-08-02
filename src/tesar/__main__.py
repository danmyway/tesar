#!/usr/bin/env python3

import contextlib
import sys

from dispatch import get_arguments, get_datetime

ARGS = get_arguments()


def main():
    if ARGS.action == "test":
        from dispatch.__main__ import main as dispatch

        if ARGS.log:
            datetime_str = get_datetime()
            with open(f"./artifactlog_{datetime_str}", "a") as log:
                with contextlib.redirect_stdout(log):
                    sys.exit(dispatch())
        else:
            sys.exit(dispatch())
    elif ARGS.action == "report":
        from report.__main__ import main as report

        sys.exit(report())
