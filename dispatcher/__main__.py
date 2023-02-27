#!/usr/bin/env python3

import requests
import sys
import importlib
from dispatcher.tf_send_request import submit_test
from dispatcher.__init__ import (
    get_logging,
    get_arguments,
    PACKAGE_MAPPING,
    ARTIFACT_MAPPING,
    COMPOSE_MAPPING,
)


logger = get_logging()
args = get_arguments()


def main():

    try:
        repo_base_url = "https://{}.com/{}/{}".format(
            args.git[0], args.git[1], PACKAGE_MAPPING.get(args.package)
        )
        git_response = requests.get(repo_base_url)
        if (
            args.git[0] != "gitlab"
            and args.git[0] != "github"
            and args.git[0] != "gitlab.cee.redhat"
        ):
            logger.critical(
                "Bad git base reference, please provide correct values.\ngithub / gitlab"
            )
            sys.exit(99)
        elif git_response.status_code == 404:
            logger.critical(
                "There is an issue with reaching the url. Please check correct order of values."
            )
            logger.critical(
                f"Reaching {repo_base_url} returned status code of {git_response.status_code}."
            )
            logger.critical(
                "Values for git option should be passed in order {repo_base owner branch}"
            )
            sys.exit(99)
        elif args.git[0] == "gitlab.cee.redhat":
            logger.warning(f"Is the repository url/name correct?\n{repo_base_url}")
            repo_name = input(
                "If that is your required repository pres ENTER, otherwise pass the correct name: "
            )
            if repo_name == "":
                logger.info(f"Continuing with selected repository: {repo_base_url}")
            else:
                repo_base_url = "https://{}.com/{}/{}".format(
                    args.git[0], args.git[1], repo_name
                )
                logger.info(f"Continuing with selected repository: {repo_base_url}")

    except IndexError as index_err:
        logger.critical(
            "Bad git reference, please provide both repository base and repository owner."
        )
        logger.critical(index_err)
        sys.exit(99)
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
        logger.critical("There is something wrong with reference/build_id!")
        sys.exit(99)

    for plan in args.plans:
        # Usually the best approach is to let Testing Farm to choose the most suitable pool.
        # Recently the AWS pools are releasing the guests during test execution.
        # If the pool-workaround option is passed, use the baseosci-openstack pool
        pool = ""
        if args.pool_workaround:
            pool = "baseosci-openstack"
            logger.warning("Pool workaround option detected, requesting 'baseosci-openstack' pool for this run.")

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
            if not (args.dry_run or args.dry_run_cli):
                logger.info(
                    f"Sending test plan "
                    + "\033[1;3m"
                    + plan.split("/")[-1]
                    + "\033[0m"
                    + f" for {args.artifact_type} build {build_reference} for {build['compose']} to the testing farm.\n"
                )
            submit_test(
                repo_base_url,
                args.git[2],
                args.git_path,
                plan,
                args.architecture,
                build["compose"],
                pool,
                str(build["build_id"]),
                ARTIFACT_MAPPING[args.artifact_type],
                PACKAGE_MAPPING[args.package],
                build["distro"],
                args.architecture,
            )


if __name__ == "__main__":
    sys.exit(main())
