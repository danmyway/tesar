#!/usr/bin/env python3

from copr.v3 import BuildProxy
from dispatch.__init__ import (
    COMPOSE_MAPPING,
    COPR_CONFIG,
    PACKAGE_MAPPING,
    get_logging,
    get_config,
    get_arguments,
    FormatText,
)

TESTING_FARM_API_KEY = get_config()
SESSION = BuildProxy(COPR_CONFIG)
LOGGER = get_logging()
ARGS = get_arguments()


def get_build_id(package, reference):
    owner = "@oamg"
    package_name = PACKAGE_MAPPING.get(ARGS.package)
    query = SESSION.get_list(owner, package)
    for build_reference in reference:
        for build in query:
            # Get build with pull request number
            if build_reference != 'latest':
                if build_reference not in build.source_package["version"]:
                    continue
            if (
                build.source_package["version"] is None
                or build.state == "failed"
            ):
                continue
            elif build.source_package["name"] == package_name:
                return build.id


def get_info(package, reference, composes):
    owner = "@oamg"
    info = []
    build_reference = None
    pr_baseurl = f"https://github.com/oamg/{package}/pull/"

    if ARGS.reference:
        query = SESSION.get_list(owner, package)
        for build_reference in reference:
            if ARGS.package == "c2r":
                build_reference = str.lower(build_reference)
            if build_reference == "master" or build_reference == "main":
                LOGGER.info(
                    f"Getting copr build info for referenced {FormatText.bold}{build_reference}{FormatText.end}."
                )
            else:
                LOGGER.info(
                    f"Getting copr build info for referenced {FormatText.bold}{str.upper(build_reference)}{FormatText.end}."
                )
                LOGGER.info(f"LINK: {pr_baseurl}{build_reference[2:]}")

            for build in query:
                # Get build with pull request number
                if (
                    build.source_package["version"] is None
                    or build.state == "failed"
                    or build_reference not in build.source_package["version"]
                ):
                    continue
                for build_info in get_build_dictionary(build, package, composes):
                    info.append(build_info)
                break

    elif ARGS.task_id:
        for build_reference in reference:
            LOGGER.info(f"Getting copr build info for referenced ID {build_reference}.")
            build = SESSION.get(build_reference)
            for build_info in get_build_dictionary(build, package, composes):
                info.append(build_info)
    return info, build_reference


def get_build_dictionary(build, package, composes):
    build_info = []
    build_baseurl = f"https://copr.fedorainfracloud.org/coprs/g/oamg/{package}/build/"
    # In case of a race condition occurs and referenced build is in a running state,
    # thus uninstallable, raise a warning
    if build.state == "running":
        LOGGER.warning(
            f"There is currently {build.state} build task, consider waiting for completion."
        )
        LOGGER.info(f"{build_baseurl[:-1]}" + "s/")
    LOGGER.info(
        "Getting build ID for %s version %s.",
        build.projectname,
        build.source_package["version"],
    )
    build_time = build.source_package["version"].split(".")[2]
    LOGGER.info(
        f"Built at {build_time[0:4]}-{build_time[4:6]}-{build_time[6:8]} {build_time[8:10]}:{build_time[10:12]}"
    )
    LOGGER.info(f"LINK: {build_baseurl}{build.id}")

    for distro in composes:
        copr_info_dict = {
            "build_id": None,
            "compose": None,
            "chroot": None,
            "distro": None,
        }
        copr_info_dict["compose"] = COMPOSE_MAPPING.get(distro).get("compose")
        copr_info_dict["distro"] = COMPOSE_MAPPING.get(distro).get("distro")
        for chroot in build.chroots:
            if COMPOSE_MAPPING.get(distro).get("chroot") == chroot:
                copr_info_dict["chroot"] = COMPOSE_MAPPING.get(distro).get("chroot")
                copr_info_dict["build_id"] = f"{build.id}:{chroot}"
                LOGGER.info(
                    f"Assigning copr build id {build.id} for testing on {copr_info_dict['compose']} to test batch."
                )

                build_info.append(copr_info_dict)

    return build_info
