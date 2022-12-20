#!/usr/bin/env python3

import requests
import sys
import importlib
from dispatch.tf_send_request import submit_test
from dispatch.__init__ import (
    get_logging,
    get_arguments,
    PACKAGE_MAPPING,
    ARTIFACT_MAPPING,
    COMPOSE_MAPPING,
)


LOGGER = get_logging()
ARGS = get_arguments()


def main():
    if ARGS.package in ["lp", "lpr"]:
        LOGGER.critical("The dispatch feature not yet properly implemented for leapp.")
        sys.exit(1)
    try:
        repo_base_url = "https://{}.com/{}/{}".format(
            ARGS.git[0], ARGS.git[1], PACKAGE_MAPPING.get(ARGS.package)
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
        elif ARGS.git[0] == "gitlab.cee.redhat":
            LOGGER.warning(f"Is the repository url/name correct?\n{repo_base_url}")
            repo_name = input(
                "If that is your required repository pres ENTER, otherwise pass the correct name: "
            )
            if repo_name == "":
                LOGGER.info(f"Continuing with selected repository: {repo_base_url}")
            else:
                repo_base_url = "https://{}.com/{}/{}".format(
                    ARGS.git[0], ARGS.git[1], repo_name
                )
                LOGGER.info(f"Continuing with selected repository: {repo_base_url}")

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

    for plan in ARGS.plans:

        if ARGS.compose:
            info, build_reference = artifact_module.get_info(
                PACKAGE_MAPPING[ARGS.package], reference, ARGS.compose
            )
        else:
            # Disable Oracle Linux 8.4 as default.
            # Keep it in the mapping in case needed.
            COMPOSE_MAPPING.pop("ol84")
            info, build_reference = artifact_module.get_info(
                PACKAGE_MAPPING[ARGS.package],
                reference,
                COMPOSE_MAPPING.keys(),
            )

        for build in info:
            if not (ARGS.dry_run or ARGS.dry_run_cli):
                LOGGER.info(
                    f"Scheduling test for "
                    + "\033[1;3m"
                    + plan.split("/")[-1]
                    + "\033[0m"
                    + f" on {ARGS.artifact_type} build {build_reference} for target {build['compose']} on the Testing Farm.\n"
                )
            submit_test(
                repo_base_url,
                ARGS.git[2],
                ARGS.git_path,
                plan,
                ARGS.architecture,
                build["compose"],
                str(build["build_id"]),
                ARTIFACT_MAPPING[ARGS.artifact_type],
                PACKAGE_MAPPING[ARGS.package],
                build["distro"],
                ARGS.architecture,
            )


if __name__ == "__main__":
    sys.exit(main())
