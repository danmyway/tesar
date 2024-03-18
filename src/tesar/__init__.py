import contextlib
import sys

from .dispatch import get_arguments, get_datetime


def main():
    args = get_arguments()

    if args.action == "test":
        from .dispatch.__main__ import main as dispatch

        if args.log:
            datetime_str = get_datetime()
            with open(f"./artifactlog_{datetime_str}", "a") as log:
                with contextlib.redirect_stdout(log):
                    sys.exit(dispatch())
        else:
            sys.exit(dispatch())
    elif args.action == "report":
        from .report.__main__ import main as report

        sys.exit(report())
