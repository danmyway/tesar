#!/usr/bin/env python3

import sys
import contextlib
from dispatcher.__main__ import main
from dispatcher.__init__ import get_arguments, get_datetime

args = get_arguments()

if args.log:
    datetime_str = get_datetime()
    with open(f"./artifactlog_{datetime_str}", "a") as log:
        with contextlib.redirect_stdout(log):
            sys.exit(main())
else:
    sys.exit(main())
