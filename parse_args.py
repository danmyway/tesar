# !/bin/python3
import argparse
from copr_api import get_copr_info


def get_args():
    artifact_types = ("fedora-copr-build", "redhat-brew-build")
    artifact_types_abbrv = ("copr", "brew")
    packages = ("convert2rhel", "leapp")

    parser = argparse.ArgumentParser(description="Send requests to testing farm.")
    parser.add_argument(
        "package",
        metavar="package",
        type=str,
        choices=packages,
        default="convert2rhel",
        help=f"Choose package to test e.g. {packages}",
    )
    subparsers = parser.add_subparsers(
        metavar="artifact_type",
        help="NOTE: Reference (PR number or brew-build version) needed. Use artifact_type --help for more info.",
    )
    parser_brew = subparsers.add_parser(
        artifact_types_abbrv[0],
        description="Run tests for brew-builds.",
        help=f"Choose to run tests for brew-builds.",
    )
    parser_copr = subparsers.add_parser(
        artifact_types_abbrv[1],
        description="Run tests for copr-builds.",
        help=f"Choose to run tests for pull requests on copr-builds.",
    )
    parser_brew.add_argument(
        "version",
        type=str,
        help="Specify the reference version to find the correct artifact (e.g. 0.1-2).",
    )
    parser_copr.add_argument(
        "pr_reference",
        type=str,
        help="Specify the pull request reference to find the correct artifact (e.g. pr123).",
    )

    parser.add_argument("-a", "--architecture", default="x86_64", type=str)

    parser.add_argument(
        "-p",
        "--plans",
        type=str,
        nargs="*",
        help=f"Specify a test plan or multiple plans to request at testing farm. "
        f"To run whole set of plans use /plans or /plans/tier",
    )

    payload_values = parser.parse_args()
    print(payload_values.version)

