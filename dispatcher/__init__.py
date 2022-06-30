#!/usr/bin/env python3

import argparse
import logging
import configparser
import os

TESTING_FARM_ENDPOINT = "https://api.dev.testing-farm.io/v0.1/requests"

ARTIFACT_BASE_URL = "http://artifacts.osci.redhat.com/testing-farm"

ARTIFACT_MAPPING = {"brew": "redhat-brew-build", "copr": "fedora-copr-build"}
PACKAGE_MAPPING = {"c2r": "convert2rhel", "leapp": "leapp"}

COMPOSE_MAPPING = {
    "cos8": {
        "compose": "CentOS-8-latest",
        "distro": "centos-8",
        "chroot": "epel-8-x86_64",
    },
    "ol8": {
        "compose": "Oracle-Linux-8.5",
        "distro": "oraclelinux-8",
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


def get_config():
    getconfig = configparser.ConfigParser()
    getconfig.read(os.path.expanduser("~/.config/tesar"))
    testing_farm_api_key = getconfig.get("testing-farm", "API_KEY")
    copr_config = {
        "copr_url": getconfig.get("copr-cli", "COPR_URL"),
        "login": getconfig.get("copr-cli", "COPR_LOGIN"),
        "token": getconfig.get("copr-cli", "COPR_TOKEN"),
        "username": getconfig.get("copr-cli", "COPR_USERNAME"),
    }

    return testing_farm_api_key, copr_config


def get_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(console_handler)
    return logger


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Send requests to testing farm conveniently.",
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
        required=True,
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
    To run whole set of plans use /plans/ or /plans/tier*/""",
    )

    parser.add_argument(
        "-c",
        "--compose",
        nargs="+",
        default=COMPOSE_MAPPING.keys(),
        choices=COMPOSE_MAPPING.keys(),
        help="""Choose composes to run tests on. 
        Default: '%(default)s'.""",
    )

    # TODO tesar file path
    # parser.add_argument(
    #     "-cfg",
    #     "--config_file",
    #     default=os.path.expanduser('~/.tesar/tesar'),
    #     help="""Change path to tesar file.
    #     Default: '%(default)s'.""",
    # )

    args = parser.parse_args()
    return args
