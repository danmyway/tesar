# !/bin/python3
import sys
import argparse
from brew_api import get_brew_info
from copr_api import get_copr_info
from tf_send_request import submit_test
import logging

COMPOSE_MAPPING = [
    [
        {"compose": "CentOS-8-latest", "distro": "centos-8", "chroot": "epel-8"},
        {
            "compose": "Oracle-Linux-8.5",
            "distro": "oraclelinux-8",
            "chroot": "oraclelinux-8",
        },
    ],
    [
        {"compose": "CentOS-7-latest", "distro": "centos-7", "chroot": "epel-7"},
        {
            "compose": "Oracle-Linux-7.9",
            "distro": "oraclelinux-7",
            "chroot": "oraclelinux-7",
        },
    ],
]


def get_log():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] - %(message)s"))
    logger.addHandler(console_handler)


def main():
    ARTIFACT_MAPPING = {"brew": "redhat-brew-build", "copr": "fedora-copr-build"}
    PACKAGE_MAPPING = {"c2r": "convert2rhel", "leapp": "leapp"}

    parser = argparse.ArgumentParser(description="Send requests to testing farm.", formatter_class=argparse.RawTextHelpFormatter)
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
        help=
        """For brew: Specify the reference version to find the correct artifact (e.g. 0.1-2, 0.1.2).
For copr: Specify the pull request reference to find the correct artifact (e.g. pr123, main, master, ...).""",
    )

    parser.add_argument(
        "-git",
        "--git_url",
        help=
        """Provide reference to git repository containing the plans metadata tree. 
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
        # action="append",
        nargs="+",
        help="""Specify a test plan or multiple plans to request at testing farm. 
To run whole set of plans use /plans or /plans/tier""",
    )

    args = parser.parse_args()

    if args.artifact_type == list(ARTIFACT_MAPPING.keys())[0]:
        for plan in args.plans:
            brew_info = get_brew_info(PACKAGE_MAPPING[args.package], args.reference)
            for task_id in brew_info:
                for compose in brew_info[task_id]:
                    for i in range(len(COMPOSE_MAPPING)):
                        for it in range(len(COMPOSE_MAPPING[i])):
                            if compose == COMPOSE_MAPPING[i][it]["compose"]:
                                tmt_distro = COMPOSE_MAPPING[i][it]["distro"]
                                submit_test(
                                    args.git_url,
                                    args.branch,
                                    args.git_path,
                                    plan,
                                    args.architecture,
                                    compose,
                                    str(task_id),
                                    ARTIFACT_MAPPING[args.artifact_type],
                                    PACKAGE_MAPPING[args.package],
                                    tmt_distro,
                                    args.architecture,
                                )

    elif args.artifact_type == list(ARTIFACT_MAPPING.keys())[1]:
        for plan in args.plans:
            copr_info = get_copr_info(PACKAGE_MAPPING[args.package], args.reference)
            for task_id in copr_info:
                for i in range(len(COMPOSE_MAPPING)):
                    for it in range(len(COMPOSE_MAPPING[i])):
                        if task_id.split(":")[-1].startswith(
                            COMPOSE_MAPPING[i][it]["chroot"]
                        ):
                            compose = COMPOSE_MAPPING[i][it]["compose"]
                            tmt_distro = COMPOSE_MAPPING[i][it]["distro"]
                            submit_test(
                                args.git_url,
                                args.branch,
                                args.git_path,
                                plan,
                                args.architecture,
                                compose,
                                task_id,
                                ARTIFACT_MAPPING[args.artifact_type],
                                PACKAGE_MAPPING[args.package],
                                tmt_distro,
                                args.architecture,
                            )


if __name__ == "__main__":
    sys.exit(main())
