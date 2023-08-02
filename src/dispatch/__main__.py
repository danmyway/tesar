#!/usr/bin/env python3

import importlib
import sys

import requests

from dispatch import (
    get_arguments,
    get_compose_mapping,
    get_logging,
)
from dispatch.dispatch_globals import ARTIFACT_MAPPING, PACKAGE_MAPPING
from dispatch.tf_send_request import submit_test

LOGGER = get_logging()
ARGS = get_arguments()
COMPOSE_MAPPING = get_compose_mapping()


def main():
    copr_repo = PACKAGE_MAPPING[ARGS.package]
    copr_package = PACKAGE_MAPPING[ARGS.package]
    git_repo = PACKAGE_MAPPING.get(ARGS.package)
    source_release = ""
    target_release = ""
    if ARGS.package == "leapp-repository":
        git_repo = "leapp-tests"
        copr_repo = "leapp"

    try:
        repo_base_url = "https://{}.com/{}/{}".format(
            ARGS.git[0], ARGS.git[1], git_repo
        )
        git_response = requests.get(repo_base_url)
        if (
            ARGS.git[0] != "gitlab"
            and ARGS.git[0] != "github"
            and ARGS.git[0] != "gitlab.cee.redhat"
        ):
            LOGGER.critical(
                "Bad git base reference, please provide correct values.\ngithub / gitlab"
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
        artifact_module = importlib.import_module(
            "dispatch." + ARGS.artifact_type + "_api"
        )
    except ImportError:
        LOGGER.error("Artifact_module could not be loaded!")
        return 99

    if ARGS.reference:
        reference = ARGS.reference
    elif ARGS.task_id:
        reference = ARGS.task_id
    else:
        LOGGER.critical("There is something wrong with reference/build_id!")
        sys.exit(99)

    iterate_over = None

    if ARGS.plans:
        iterate_over = ARGS.plans
    elif ARGS.planfilter:
        iterate_over = ARGS.planfilter
    elif ARGS.testfilter:
        iterate_over = ARGS.testfilter

    for item in iterate_over:
        plan = None
        planfilter = None
        testfilter = None
        item = item.rstrip("/")
        # Usually the best approach is to let Testing Farm to choose the most suitable pool.
        # Recently the AWS pools are releasing the guests during test execution.
        # If the pool-workaround option is passed, use the baseosci-openstack pool
        pool = ""
        if ARGS.pool_workaround:
            pool = "baseosci-openstack"
            LOGGER.warning(
                "Pool workaround option detected, requesting 'baseosci-openstack' pool for this run."
            )

        if ARGS.plans:
            plan = item
            planfilter = ""
            testfilter = ""
        elif ARGS.planfilter:
            plan = ""
            planfilter = item
            testfilter = ""
        elif ARGS.testfilter:
            plan = ""
            planfilter = ""
            testfilter = item

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
                ARGS.git[2],
                ARGS.git_path,
                plan,
                planfilter,
                testfilter,
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
            )


if __name__ == "__main__":
    sys.exit(main())
