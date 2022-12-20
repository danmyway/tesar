#!/usr/bin/env python3
import sys
import contextlib
from dispatch.__init__ import get_arguments, get_datetime, get_logging


ARGS = get_arguments()
LOGGER = get_logging()

if ARGS.command == "get-id":
    from get_id.__main__ import main
elif ARGS.command == "dispatch":
    from dispatch.__main__ import main
if ARGS.log:
    datetime_str = get_datetime()
    with open(f"./artifactlog_{datetime_str}", "a") as log:
        with contextlib.redirect_stdout(log):
            sys.exit(main())
else:
    sys.exit(main())
