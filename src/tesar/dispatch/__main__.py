#!/usr/bin/env python3

import importlib
import sys

import requests

from .__init__ import (
    get_arguments,
    get_compose_mapping,
    get_logging,
)
from .dispatch_globals import ARTIFACT_MAPPING, PACKAGE_MAPPING
from .tf_send_request import submit_test

LOGGER = get_logging()
ARGS = get_arguments()
COMPOSE_MAPPING = get_compose_mapping()


def main(
    git_base=None,
    git_owner=None,
    git_repo=None,
    git_ref=None,
    copr_repo=None,
    copr_package=PACKAGE_MAPPING[ARGS.package],
):
    if ARGS.package == "c2r":
        git_base = "github"
        git_owner = "oamg"
        git_repo = PACKAGE_MAPPING.get(ARGS.package)
        git_ref = "main"
        copr_repo = PACKAGE_MAPPING[ARGS.package]
    elif ARGS.package == "leapp-repository":
        git_base = "gitlab.cee.redhat"
        git_owner = "oamg"
        git_repo = "leapp-tests"
        git_ref = "master"
        copr_repo = "leapp"
    if ARGS.git:
        git_base = ARGS.git[0]
        if ".com" in git_base:
            git_base = git_base.strip(".com")
        git_owner = ARGS.git[1]
        git_repo = ARGS.git[2]
        git_ref = ARGS.git[3]
    try:
        repo_base_url = "https://{}.com/{}/{}".format(git_base, git_owner, git_repo)
        git_response = requests.get(repo_base_url)
        if git_base not in ["gitlab", "github", "gitlab.cee.redhat"]:
            LOGGER.critical(
                "Bad git base reference, please provide correct values.\ngithub / gitlab / gitlab.cee.redhat"
            )
            sys.exit(99)
        elif git_response.status_code == 404:
            LOGGER.critical(
                "There is an issue with reaching the url. Please check correct order of values."
            )
            LOGGER.critical(
                f"Reaching {repo_base_url} returned status code of {git_response.status_code}."
            )
            LOGGER.critical(
                "Values for git option should be passed in order {repo_base owner branch}"
            )
            sys.exit(99)

    except IndexError as index_err:
        LOGGER.critical(
            "Bad git reference, please provide both repository base and repository owner."
        )
        LOGGER.critical(index_err)
        sys.exit(99)
    try:
        artifact_module_name = ARGS.artifact_type + "_api"
        artifact_module = importlib.import_module(
            "tesar.dispatch." + artifact_module_name
        )
    except ImportError as ie:
        LOGGER.debug(ie)
        LOGGER.error("Artifact_module could not be loaded!")
        return 99

    if ARGS.reference:
        reference = ARGS.reference
    elif ARGS.task_id:
        reference = ARGS.task_id

    plans = ARGS.plans

    # Exit if multiple plans requested with additional filter(s)
    if len(plans) > 1 and (ARGS.planfilter or ARGS.testfilter):
        LOGGER.critical(
            "It is not advised to use testfilter or planfilter with multiple requested plans."
            " Please specify one plan with additional filters per request."
        )
        sys.exit(2)

    boot_method = "bios"
    if ARGS.uefi:
        boot_method = "uefi"

    for plan in plans:
        item = plan.rstrip("/")
        # Usually the best approach is to let Testing Farm to choose the most suitable pool.
        # Occasionally the AWS pools are releasing the guests during test execution.
        # If the pool-workaround option is passed, use the baseosci-openstack pool
        pool = ""
        if ARGS.pool_workaround:
            pool = "baseosci-openstack"
            LOGGER.warning(
                "Pool workaround option detected, requesting 'baseosci-openstack' pool for this run."
            )

        if ARGS.target:
            info, build_reference = artifact_module.get_info(
                copr_package, copr_repo, reference, ARGS.target
            )
        else:
            info, build_reference = artifact_module.get_info(
                copr_package,
                copr_repo,
                reference,
                COMPOSE_MAPPING.keys(),
            )

        for build in info:

            if not (ARGS.dry_run or ARGS.dry_run_cli):
                LOGGER.info(
                    f"Sending test plan "
                    + "\033[1;3m"
                    + item.split("/")[-1]
                    + "\033[0m"
                    + f" for {ARGS.artifact_type} build {build_reference} for {build['compose']} to the testing farm.\n"
                )
            submit_test(
                repo_base_url,
                git_ref,
                ARGS.git_path,
                plan,
                ARGS.planfilter,
                ARGS.testfilter,
                ARGS.architecture,
                build["compose"],
                pool,
                build["source_release"],
                build["target_release"],
                str(build["build_id"]),
                ARTIFACT_MAPPING[ARGS.artifact_type],
                PACKAGE_MAPPING[ARGS.package],
                build["distro"],
                ARGS.architecture,
                boot_method,
                parallel_limit=ARGS.parallel_limit,
            )


if __name__ == "__main__":
    sys.exit(main())
