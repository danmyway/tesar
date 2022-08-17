#!/usr/bin/env python3
import contextlib
import sys
import importlib
from dispatcher.tf_send_request import submit_test
from dispatcher.__init__ import (
    get_logging,
    get_arguments,
    PACKAGE_MAPPING,
    ARTIFACT_MAPPING,
    COMPOSE_MAPPING,
    get_datetime,
)


logger = get_logging()
args = get_arguments()


def main():
    try:
        artifact_module = importlib.import_module(
            "dispatcher." + args.artifact_type + "_api"
        )
    except ImportError:
        logger.error("Artifact_module could not be loaded!")
        return 99

    if args.reference:
        reference = args.reference
    elif args.task_id:
        reference = args.task_id
    else:
        reference = None
        logger.critical("There is something wrong with reference/build_id!")
        sys.exit(99)

    for plan in args.plans:

        if args.compose:
            info, build_reference = artifact_module.get_info(
                PACKAGE_MAPPING[args.package], reference, args.compose
            )
        else:
            info, build_reference = artifact_module.get_info(
                PACKAGE_MAPPING[args.package],
                reference,
                COMPOSE_MAPPING.keys(),
            )

        for build in info:
            logger.info(
                f"Sending test plan "
                + "\033[1;3m"
                + plan.split("/")[-1]
                + "\033[0m"
                + f" for {args.artifact_type} build {build_reference} for {build['compose']} to the testing farm."
            )
            submit_test(
                args.git_url,
                args.branch,
                args.git_path,
                plan,
                args.architecture,
                build["compose"],
                str(build["build_id"]),
                ARTIFACT_MAPPING[args.artifact_type],
                PACKAGE_MAPPING[args.package],
                build["distro"],
                args.architecture,
            )


if __name__ == "__main__":
    sys.exit(main())
