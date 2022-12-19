#!/usr/bin/env python3
import sys

from dispatch.__init__ import (
    get_logging,
    get_arguments,
    LEAPP_TARGET_MAPPING,
)
from dispatch.copr_api import get_build_id


LOGGER = get_logging()
ARGS = get_arguments()


def get_id():
    if ARGS.package in ["lp", "lpr"]:
        package = "leapp"
    else:
        LOGGER.critical("The get_id feature is not yet implemented for other packages.")
        sys.exit(1)

    list_chroot = []
    list_build_id = []
    list_build_reference = []
    try:
        for item in ARGS.target:
            short_target = LEAPP_TARGET_MAPPING[ARGS.package][item]
            target = short_target.get("name")
            for architecture in ARGS.architecture:
                if architecture in short_target.get("arch"):
                    chroot = f"{target}-{architecture}"
                    list_chroot.append(chroot)
                else:
                    LOGGER.warn(
                        f"Provided combination of target {target} and architecture {architecture} is not available."
                    )

        build_id = get_build_id(package, ARGS.reference)
        if build_id is None:
            LOGGER.critical(f"There is no build for referenced {item}!\n")
            sys.exit(1)
        list_build_id.append(build_id)

        for chroot in list_chroot:
            for build_id in list_build_id:
                list_build_reference.append(f"{build_id}-{chroot}")
                print(f"{build_id}-{chroot}")

    except KeyError:
        LOGGER.warn(
            f"Possible invalid combination for requested package {package} and target ({item})."
        )

