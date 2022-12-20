#!/usr/bin/env python3
import sys
from get_id.get_id import get_id
from dispatch.__init__ import get_arguments

ARGS = get_arguments()


def main():
    try:
        get_id()
    except Exception:
        raise


if __name__ == "__main__":
    sys.exit(main())
