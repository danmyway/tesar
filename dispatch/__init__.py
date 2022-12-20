#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime
import logging
import configparser
import os

TESTING_FARM_ENDPOINT = "https://api.dev.testing-farm.io/v0.1/requests"

ARTIFACT_BASE_URL = "http://artifacts.osci.redhat.com/testing-farm"

ARTIFACT_MAPPING = {"brew": "redhat-brew-build", "copr": "fedora-copr-build"}
PACKAGE_MAPPING = {"c2r": "convert2rhel", "lp": "leapp", "lpr": "leapp-repository"}

COPR_CONFIG = {"copr_url": "https://copr.fedorainfracloud.org"}

COMPOSE_MAPPING = {
    "cos8": {
        "compose": "CentOS-8-latest",
        "distro": "centos-8-latest",
        "chroot": "epel-8-x86_64",
    },
    "ol8": {
        "compose": "Oracle-Linux-8.6",
        "distro": "oraclelinux-8.6",
        "chroot": "epel-8-x86_64",
    },
    "cos7": {
        "compose": "CentOS-7-latest",
        "distro": "centos-7",
        "chroot": "epel-7-x86_64",
    },
    "ol7": {
        "compose": "Oracle-Linux-7.9",
        "distro": "oraclelinux-7",
        "chroot": "epel-7-x86_64",
    },
    "cos84": {
        "compose": "CentOS-8.4",
        "distro": "centos-8.4",
        "chroot": "epel-8-x86_64",
    },
    "ol84": {
        "compose": "Oracle-Linux-8.4",
        "distro": "oraclelinux-8.4",
        "chroot": "epel-8-x86_64",
    },
}

LEAPP_TARGET_MAPPING = {
    "lpr": {
        "el7": {"name": "epel7", "arch": ["x86_64"]},
        "el8": {"name": "epel8", "arch": ["x86_64"]},
    },
    "lp": {
        "el7": {"name": "epel7", "arch": ["ppc64le", "x86_64"]},
        "el8": {"name": "epel8", "arch": ["x86_64"]},
        "f35": {"name": "fedora-35", "arch": ["aarch64", "x86_64"]},
        "f36": {"name": "fedora-36", "arch": ["aarch64", "x86_64"]},
        "f37": {"name": "fedora-37", "arch": ["aarch64", "x86_64"]},
        "fraw": {"name": "fedora-rawhide", "arch": ["aarch64", "x86_64"]},
    },
}


class FormatText:
    purple = "\033[95m"
    cyan = "\033[96m"
    darkcyan = "\033[36m"
    blue = "\033[94m"
    green = "\033[92m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold = "\033[1m"
    end = "\033[0m"


def get_datetime():
    datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return datetime_str


def get_config():
    getconfig = configparser.ConfigParser()
    try:
        if get_arguments().dry_run or get_arguments().dry_run_cli:
            testing_farm_api_key = "{TESTING_FARM_API_KEY}"
            return testing_farm_api_key
        else:
            getconfig.read(os.path.expanduser("~/.config/tesar"))
            testing_farm_api_key = getconfig.get("testing-farm", "API_KEY")

            return testing_farm_api_key
    except configparser.NoSectionError as no_config_err:
        get_logging().critical(
            "There is probably no config file in the default path ~/.config/tesar."
        )
        get_logging().critical(no_config_err)
        sys.exit(99)
    except configparser.NoOptionError as no_opt_err:
        get_logging().critical("Config file might be tainted.")
        get_logging().critical(no_opt_err)
        sys.exit(99)


def get_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(console_handler)
    return logger


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Send requests to testing farm conveniently.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "artifact_type",
        metavar="artifact_type",
        choices=list(ARTIFACT_MAPPING.keys()),
        help="Choose which type of artefact to test e.g. %(choices)s.",
    )

    parser.add_argument(
        "package",
        metavar="package",
        choices=list(PACKAGE_MAPPING.keys()),
        help="Choose package to test e.g. %(choices)s.",
    )

    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        help="Log test links or dry run output to a file.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print out just the payload that would be sent to the testing farm.\nDo not actually send any request.",
    )

    parser.add_argument(
        "--dry-run-cli",
        action="store_true",
        help="Print out https shell command with requested payload.\nDo not actually send any request.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print out additional information for each request.",
    )

    subparsers = parser.add_subparsers(
        title="Select an action to perform.", required=True, dest="command"
    )

    parser_get_id = subparsers.add_parser("get-id", help="prints out build ID")

    parser_get_id.add_argument(
        "-t",
        "--target",
        nargs="+",
        required=True,
        choices=["el7", "el8", "f35", "f36", "f37", "fraw"],
        help="Select a target for the build.",
    )
    parser_get_id.add_argument(
        "-ref",
        "--reference",
        required=True,
        nargs=1,
        help=f"""For copr: Specify the pull request reference to find the correct artifact (e.g. pr123, main, master, ...).\n
    {FormatText.bold}For leapp/leapp-repository, the reference is case sensitive.\n
    Packages built by packit are referenced in lower-case, built by oamgbot are referenced in upper-case letters.\n{FormatText.end}    
    For brew: {FormatText.bold} FEATURE IS NOT YET IMPLEMENTED {FormatText.end}
    """,
    )

    parser_get_id.add_argument(
        "-a",
        "--architecture",
        required=True,
        nargs="+",
        choices=["aarch64", "ppc64le", "x86_64"],
        help="""Choose suitable architecture.\n""",
    )

    parser_dispatch = subparsers.add_parser("dispatch", help="dispatch jobs")

    reference = parser_dispatch.add_mutually_exclusive_group(required=True)

    parser_dispatch.add_argument(
        "-a",
        "--architecture",
        default="x86_64",
        help="""Choose suitable architecture.\nDefault: '%(default)s'.""",
    )

    reference.add_argument(
        "-ref",
        "--reference",
        nargs="+",
        help=f"""{FormatText.bold}Mutually exclusive with respect to --task-id.{FormatText.end}
For brew: Specify the reference version to find the correct artifact (e.g. 0.1-2, 0.1.2).
For copr: Specify the pull request reference to find the correct artifact (e.g. pr123, main, master, ...).""",
    )

    reference.add_argument(
        "-id",
        "--task-id",
        nargs="+",
        help=f"""{FormatText.bold}Mutually exclusive with respect to --reference.{FormatText.end}
For brew: Specify the TASK ID for required brew build.
{FormatText.bold}NOTE: Double check, that you are passing TASK ID for copr builds, not BUILD ID otherwise testing farm will not install the package.{FormatText.end}
For copr: Specify the BUILD ID for required copr build.""",
    )

    parser_dispatch.add_argument(
        "-g",
        "--git",
        nargs="+",
        default=["github", "oamg", "main"],
        help="""Provide repository base (github, gitlab, gitlab.cee.redhat)\nowner of the repository\nand a branch containing the tests you want to run.
Default: '%(default)s'""",
    )

    parser_dispatch.add_argument(
        "-gp",
        "--git-path",
        default=".",
        help="""Path to the metadata tree root.
Should be relative to the git repository root provided in the url parameter.
Default: '%(default)s'""",
    )

    parser_dispatch.add_argument(
        "-p",
        "--plans",
        required=True,
        nargs="+",
        default="/plans/",
        help="""Specify a test plan or multiple plans to request at testing farm.
To run whole set of tiers use /plans/tier*/
Default: '%(default)s'""",
    )

    parser_dispatch.add_argument(
        "-c",
        "--compose",
        nargs="+",
        default=list(COMPOSE_MAPPING.keys()),
        choices=list(COMPOSE_MAPPING.keys()),
        help="""Choose composes to run tests on.\nDefault: '%(default)s'.""",
    )

    # TODO tesar file path
    # parser.add_argument(
    #     "-cfg",
    #     "--config_file",
    #     default=os.path.expanduser('~/.config/tesar'),
    #     help="""Change path to the tesar config file.
    #     Default: '%(default)s'.""",
    # )

    args = parser.parse_args()

    return args
