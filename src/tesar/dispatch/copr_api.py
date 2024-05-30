#!/usr/bin/env python3
import sys
from datetime import datetime

from copr.v3 import BuildProxy

from . import dispatch_globals
from .__init__ import get_arguments, get_compose_mapping, get_logging

SESSION = BuildProxy(dispatch_globals.COPR_CONFIG)
LOGGER = get_logging()
ARGS = get_arguments()
COMPOSE_MAPPING = get_compose_mapping()


def get_info(package, repository, reference, composes):
    """
    Get information about a COPR build for a specific package and reference.

    Args:
        package (str): The name of the package for which to get information.
        repository (str): The name of the Copr repository containing the package build.
        reference (str, int): The reference for the package build. This can be either a commit reference
                         (e.g., "master", "main") or a pull request ID (e.g., "pull/123").
        composes (list): A list of strings representing the target distributions for the COPR build.

    Returns:
        tuple: A tuple containing two elements:
            - A list of dictionaries containing build information for each target distribution.
            - The build reference used for selecting the COPR build.
    """
    owner = "@oamg"
    info = []
    build_reference = reference[0]
    pr_baseurl = f"https://github.com/oamg/{package}/pull/"

    if ARGS.reference:

        def _get_correct_build_list():
            """
            Get a clean list of COPR builds that match the specified reference.

            Returns:
                list: A list of COPR builds that match the specified reference.
            """
            clean_build_list = []
            query = SESSION.get_list(owner, repository)

            if build_reference in ["master", "main"]:
                LOGGER.info(
                    f"Getting copr build info for referenced {build_reference}."
                )
            else:
                LOGGER.info(
                    f"Getting copr build info for referenced {str.upper(build_reference)}."
                )
                LOGGER.info(f"LINK: {pr_baseurl}{build_reference[2:]}")
            for build_munch in query:
                if (
                    build_munch.state != "failed"
                    and build_munch.source_package["name"] == package
                    and build_munch.source_package["version"] is not None
                    and build_reference in build_munch.source_package["version"]
                ):
                    clean_build_list.append(build_munch)

            if not clean_build_list:
                LOGGER.warning(
                    f"{FormatText.yellow+FormatText.bold}No build with given {build_reference} found!{FormatText.end}"
                )

            return clean_build_list

        for build_munch in _get_correct_build_list():
            build = build_munch
            for build_info in get_build_dictionary(
                build, repository, package, composes
            ):
                info.append(build_info)
            # Break so just the latest is selected
            break

    elif ARGS.task_id:
        build = None
        LOGGER.info(f"Getting copr build info for referenced ID {build_reference}.")
        build_munch = SESSION.get(build_reference)
        if build_munch.source_package["name"] != package:
            LOGGER.critical(f"There seems to be some mismatch with the build ID!")
            LOGGER.critical(
                f"The ID points to owner: {build_munch.ownername}, project: {build_munch.projectname}"
            )
            LOGGER.critical(f"Exiting.")
            sys.exit(99)
        elif build_munch.state == "failed":
            LOGGER.critical(
                f"{FormatText.red+FormatText.bold}The build with the given ID failed!{FormatText.end}"
            )
            LOGGER.critical(
                f"{FormatText.red+FormatText.bold}Please provide valid build ID.{FormatText.end}"
            )
            LOGGER.critical(f"{FormatText.red+FormatText.bold}Exiting.{FormatText.end}")
        else:
            build = build_munch
        for build_info in get_build_dictionary(build, repository, package, composes):
            info.append(build_info)

    return info, build_reference


def get_build_dictionary(
    build, repository, package, composes, source_release=None, target_release=None
):
    """
    Get the dictionary containing build information for each target distribution.

    Args:
        build: The COPR build object.
        repository (str): The COPR repository name.
        package (str): The name of the package.
        composes (list): A list of strings representing the target distributions for the COPR build.
        source_release (str, optional): The source release version. Defaults to None.
        target_release (str, optional): The target release version. Defaults to None.

    Returns:
        list: A list of dictionaries containing build information for each target distribution.
    """
    build_info = []
    build_baseurl = (
        f"https://copr.fedorainfracloud.org/coprs/g/oamg/{repository}/build/"
    )
    # In case of a race condition occurs and referenced build is in a running state,
    # thus uninstallable, raise a warning
    if build.state == "running":
        LOGGER.warning(
            f"There is currently {build.state} build task, consider waiting for completion."
        )
        LOGGER.info(f"{build_baseurl[:-1]}" + "s/")
    LOGGER.info(
        "Getting build ID for %s version %s.",
        build.source_package["name"],
        build.source_package["version"],
    )
    timestamp_str = build.source_package["version"].split(".")[3]
    timestamp_format = "%Y%m%d%H%M%S"
    build_time = datetime.strptime(timestamp_str[0:13], timestamp_format)

    LOGGER.info(f"Built at {build_time}")
    LOGGER.info(f"LINK: {build_baseurl}{build.id}")
    for distro in composes:
        copr_info_dict = {
            "build_id": None,
            "compose": None,
            "chroot": None,
            "distro": None,
            "source_release": None,
            "target_release": None,
        }
        # Assign correct SOURCE_RELEASE and TARGET_RELEASE
        if ARGS.package == "leapp-repository":
            source_release_raw = str(distro.split("to")[0])
            target_release_raw = str(distro.split("to")[1])
            source_release = f"{source_release_raw[0]}.{source_release_raw[1]}"
            target_release = f"{target_release_raw[0]}.{target_release_raw[1]}"
        copr_info_dict["compose"] = COMPOSE_MAPPING.get(distro).get("compose")
        copr_info_dict["distro"] = COMPOSE_MAPPING.get(distro).get("distro")
        copr_info_dict["source_release"] = source_release
        copr_info_dict["target_release"] = target_release
        for chroot in build.chroots:
            if COMPOSE_MAPPING.get(distro).get("chroot") == chroot:
                copr_info_dict["chroot"] = COMPOSE_MAPPING.get(distro).get("chroot")
                copr_info_dict["build_id"] = f"{build.id}:{chroot}"
                LOGGER.info(
                    f"Assigning copr build id {build.id} for testing on {copr_info_dict['compose']} to test batch."
                )

                build_info.append(copr_info_dict)

    return build_info
