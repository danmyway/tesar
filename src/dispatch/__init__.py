#!/usr/bin/env python3

import argparse
import configparser
from datetime import datetime
import logging
import os
import sys


from . import dispatch_globals


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
    bg_red = "\033[41m"
    bg_green = "\033[42m"
    bg_yellow = "\033[43m"
    bg_blue = "\033[44m"
    bg_magenta = "\033[45m"
    bg_cyan = "\033[46m"
    bg_white = "\033[47m"
    bg_default = "\033[49m"
    bg_black = "\033[40m"
    bg_purple = "\033[45m"


def get_datetime():
    datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
    return datetime_str


def get_config():
    getconfig = configparser.ConfigParser()
    try:
        getconfig.read(os.path.expanduser("~/.config/tesar"))
        testing_farm_api_key = getconfig.get("testing-farm", "API_KEY")
        cloud_resources_tag = getconfig.get(
            "cloud-resources-tag", "CLOUD_RESOURCES_TAG"
        )

        if get_arguments().action == "test" and (
            get_arguments().dry_run or get_arguments().dry_run_cli
        ):
            testing_farm_api_key = "{testing_farm_api_key}"
            cloud_resources_tag = "{cloud_resources_tag}"

        return (
            cloud_resources_tag,
            testing_farm_api_key,
        )
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


def get_arguments(args=None):
    parser = argparse.ArgumentParser(
        description="Send requests to and get the results back from the Testing Farm conveniently.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="action")

    test = subparsers.add_parser(
        "test",
        help="Dispatch a job to the Testing Farm API endpoint.",
        description="Send requests to the Testing Farm conveniently.",
    )

    test.add_argument(
        "artifact_type",
        metavar="artifact_type",
        choices=list(dispatch_globals.ARTIFACT_MAPPING.keys()),
        help="Choose which type of artifact to test. Choices: %(choices)s",
    )

    test.add_argument(
        "package",
        metavar="package",
        choices=list(dispatch_globals.PACKAGE_MAPPING.keys()),
        help="Choose package to test. Choices: %(choices)s",
    )

    reference = test.add_mutually_exclusive_group(required=True)

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

    test.add_argument(
        "-g",
        "--git",
        nargs="+",
        default=["github", "oamg", "main"],
        help="""Provide repository base (github, gitlab, gitlab.cee.redhat)\nowner of the repository\nand a branch containing the tests you want to run.
Default: '%(default)s'""",
    )

    test.add_argument(
        "-gp",
        "--git-path",
        default=".",
        help="""Path to the metadata tree root.
Should be relative to the git repository root provided in the url parameter.
Default: '%(default)s'""",
    )

    test.add_argument(
        "-a",
        "--architecture",
        default="x86_64",
        help="""Choose suitable architecture.\nDefault: '%(default)s'.""",
    )

    fmf_reference = test.add_mutually_exclusive_group(required=True)

    fmf_reference.add_argument(
        "-p",
        "--plans",
        nargs="+",
        help="""Specify a test plan or multiple plans to request at testing farm.
To run whole set of tiers use /plans/tier*/
Accepts multiple space separated values, sends as a separate request.""",
    )

    fmf_reference.add_argument(
        "-pf",
        "--planfilter",
        nargs="+",
        help="""Filter plans.
The specified plan filter will be used in tmt plan ls --filter <YOUR-FILTER> command.
By default enabled: true filter is applied.
Accepts multiple space separated values, sends as a separate request.
""",
    )

    fmf_reference.add_argument(
        "-tf",
        "--testfilter",
        nargs="+",
        help="""Filter tests.
The specified plan filter will be used in tmt run discover plan test --filter <YOUR-FILTER> command.
Accepts multiple space separated values, sends as a separate request.""",
    )

    test.add_argument(
        "-t",
        "--target",
        nargs="+",
        help="""Choose targeted test run. For c2r targeted OS, for leapp targeted upgrade path.""",
    )

    test.add_argument(
        "-pw",
        "--pool-workaround",
        action="store_true",
        help="""Workarounds the AWS spot instances release.""",
    )

    test.add_argument(
        "-w",
        "--wait",
        type=int,
        default=20,
        help="""Provide number of seconds to wait for successful response.\nDefault: %(default)s seconds.""",
    )

    test.add_argument(
        "-nw",
        "--no-wait",
        action="store_true",
        help="""Don't wait for successful response and get the artifact link ASAP.""",
    )

    # TODO tesar file path
    # test.add_argument(
    #     "-cfg",
    #     "--config_file",
    #     default=os.path.expanduser('~/.config/tesar'),
    #     help="""Change path to the tesar config file.
    #     Default: '%(default)s'.""",
    # )

    test.add_argument(
        "-l",
        "--log",
        action="store_true",
        help="Log test links or dry run output to a file.",
    )

    test.add_argument(
        "--dry-run",
        action="store_true",
        help="Print out just the payload that would be sent to the testing farm.\nDo not actually send any request.",
    )

    test.add_argument(
        "--dry-run-cli",
        action="store_true",
        help="Print out https shell command with requested payload.\nDo not actually send any request.",
    )

    test.add_argument(
        "--debug",
        action="store_true",
        help="Print out additional information for each request.",
    )

    report = subparsers.add_parser(
        "report",
        help="Report results for requested tasks.",
        description="Parses task IDs, Testing Farm artifact URLs or Testing Farm API request URLs from multiple sources.",
    )

    report.add_argument(
        "-l2",
        "--level2",
        action="store_true",
        help="""Display test view detail. By default the report shows only plan view.""",
    )
    report.add_argument(
        "-s",
        "--short",
        action="store_true",
        help="Display short test and plan names.",
    )
    report.add_argument(
        "-stn",
        "--split-testname",
        type=int,
        help="""Specify an index from which will the test name be shown. Passed to testname.split('/')[index:]""",
    )
    report.add_argument(
        "-spn",
        "--split-planname",
        type=int,
        help="""Specify an index from which will the plan name be shown. Passed to planname.split('/')[index:]""",
    )
    report.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Wait for the job to complete. Print the table afterwards",
    )
    report.add_argument(
        "-d",
        "--download-logs",
        action="store_true",
        help="""Download logs for requested run(s).""",
    )
    tasks_source = report.add_mutually_exclusive_group()
    tasks_source.add_argument(
        "-lt",
        "--latest",
        action="store_true",
        help=f"""{FormatText.bold}Mutually exclusive with respect to --file and --cmd.{FormatText.end}
        Report latest jobs from {dispatch_globals.LATEST_TASKS_FILE}.""",
    )
    tasks_source.add_argument(
        "-f",
        "--file",
        help=f"""{FormatText.bold}Mutually exclusive with respect to --latest and --cmd.{FormatText.end}
        Specify a different location than the default {dispatch_globals.DEFAULT_TASKS_FILE} of the file containing request_id's, artifact URLs or request URLs.""",
    )
    tasks_source.add_argument(
        "-c",
        "--cmd",
        action="append",
        help=f"""{FormatText.bold}Mutually exclusive with respect to --file and --latest.{FormatText.end}
        Parse request_ids, artifact URLs or request URLs from the command line.""",
    )

    args = parser.parse_args(args=args or sys.argv[1:])
    return args


def get_compose_mapping(args=None):
    """Dynamically provide proper compose mapping depending on cli args"""
    args = get_arguments(args=args or sys.argv[1:])

    compose_mapping = {('test', 'c2r'): dispatch_globals.C2R_COMPOSE_MAPPING,
                       ('test', 'leapp-repository'): dispatch_globals.LP_COMPOSE_MAPPING}
    return compose_mapping.get((args.action, args.package), {})
