#!/usr/bin/env python3

import sys
import importlib
import argparse
from tf_send_request import submit_test
import logging


# def get_log():
#     logger = logging.getLogger(__name__)
#     logger.setLevel(logging.INFO)
#     if not logger.hasHandlers():
#         console_handler = logging.StreamHandler()
#         console_handler.setLevel(logging.INFO)
#         console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
#         logger.addHandler(console_handler)
#     return logger
#
#
# logger = get_log()


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(console_handler)
    # return logger

    ARTIFACT_MAPPING = {"brew": "redhat-brew-build", "copr": "fedora-copr-build"}
    PACKAGE_MAPPING = {"c2r": "convert2rhel", "leapp": "leapp"}

    parser = argparse.ArgumentParser(
        description="Send requests to testing farm.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "artifact_type",
        metavar="artifact_type",
        choices=ARTIFACT_MAPPING.keys(),
        help="Choose which type of artefact to test e.g. %(choices)s.",
    )

    parser.add_argument(
        "--package",
        required=True,
        choices=PACKAGE_MAPPING.keys(),
        default=next(iter(PACKAGE_MAPPING.keys())),
        help="""Choose package to test e.g. %(choices)s.
Default: '%(default)s'.""",
    )

    parser.add_argument(
        "-ref",
        "--reference",
        help="""For brew: Specify the reference version to find the correct artifact (e.g. 0.1-2, 0.1.2).
For copr: Specify the pull request reference to find the correct artifact (e.g. pr123, main, master, ...).""",
    )

    parser.add_argument(
        "-git",
        "--git_url",
        help="""Provide reference to git repository containing the plans metadata tree. 
Use any format acceptable by the git clone command.""",
    )

    parser.add_argument(
        "-b",
        "--branch",
        default="master",
        help="""Branch, tag or commit specifying the desired git revision. 
This is used to perform a git checkout in the repository. 
Default: '%(default)s'""",
    )
    parser.add_argument(
        "-gp",
        "--git_path",
        default=".",
        help="""Path to the metadata tree root. 
Should be relative to the git repository root provided in the url parameter. 
Default: '%(default)s'""",
    )

    parser.add_argument(
        "-a",
        "--architecture",
        default="x86_64",
        help="""Choose suitable architecture. 
Default: '%(default)s'.""",
    )

    parser.add_argument(
        "-p",
        "--plans",
        required=True,
        nargs="+",
        help="""Specify a test plan or multiple plans to request at testing farm. 
To run whole set of plans use /plans or /plans/tier""",
    )

    args = parser.parse_args()

    try:
        artifact_module = importlib.import_module(args.artifact_type + "_api")
    except ImportError:
        logger.error("Artifact_module could not be loaded!")
        return 99

    for plan in args.plans:
        info = artifact_module.get_info(PACKAGE_MAPPING[args.package], str.lower(args.reference))
        for build in info:
            logger.info(
                f"Sending tests for {args.artifact_type} build for {build['compose']} to the testing farm."
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
                build["chroot"],
                args.architecture,
            )


if __name__ == "__main__":
    sys.exit(main())
