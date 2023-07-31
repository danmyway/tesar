#!/usr/bin/env python3
from datetime import datetime

from copr.v3 import BuildProxy

from dispatch import dispatch_globals
from dispatch import get_arguments, get_compose_mapping, get_logging

SESSION = BuildProxy(dispatch_globals.COPR_CONFIG)
LOGGER = get_logging()
ARGS = get_arguments()
COMPOSE_MAPPING = get_compose_mapping()


def get_info(package, repository, reference, composes):
    owner = "@oamg"
    info = []
    build_reference = None
    pr_baseurl = f"https://github.com/oamg/{package}/pull/"

    if ARGS.reference:
        query = SESSION.get_list(owner, repository)

        for build_reference in reference:
            if build_reference == "master" or build_reference == "main":
                LOGGER.info(
                    f"Getting copr build info for referenced {build_reference}."
                )
            else:
                LOGGER.info(
                    f"Getting copr build info for referenced {str.upper(build_reference)}."
                )
                LOGGER.info(f"LINK: {pr_baseurl}{build_reference[2:]}")

            for build in query:
                # Parse only correct packages
                if build.source_package["name"] == package:
                    build = build
                else:
                    continue

                # Get build with pull request number
                if (
                    build.source_package["version"] is None
                    or build.state == "failed"
                    or build_reference not in build.source_package["version"]
                ):
                    continue
                for build_info in get_build_dictionary(
                    build, repository, package, composes
                ):
                    info.append(build_info)
                break

    elif ARGS.task_id:
        for build_reference in reference:
            LOGGER.info(f"Getting copr build info for referenced ID {build_reference}.")
            build = SESSION.get(build_reference)
            for build_info in get_build_dictionary(
                build, repository, package, composes
            ):
                info.append(build_info)

    return info, build_reference


def get_build_dictionary(
    build, repository, package, composes, source_release=None, target_release=None
):
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
    release_var_iter = 0
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
            release_vars = ARGS.target[release_var_iter]
            source_release_raw = str(release_vars.split("to")[0])
            target_release_raw = str(release_vars.split("to")[1])
            source_release = f"{source_release_raw[0]}.{source_release_raw[1]}"
            target_release = f"{target_release_raw[0]}.{target_release_raw[1]}"
        copr_info_dict["compose"] = COMPOSE_MAPPING.get(distro).get("compose")
        copr_info_dict["distro"] = COMPOSE_MAPPING.get(distro).get("distro")
        copr_info_dict["source_release"] = source_release
        copr_info_dict["target_release"] = target_release
        release_var_iter += 1
        for chroot in build.chroots:
            if COMPOSE_MAPPING.get(distro).get("chroot") == chroot:
                copr_info_dict["chroot"] = COMPOSE_MAPPING.get(distro).get("chroot")
                copr_info_dict["build_id"] = f"{build.id}:{chroot}"
                LOGGER.info(
                    f"Assigning copr build id {build.id} for testing on {copr_info_dict['compose']} to test batch."
                )

                build_info.append(copr_info_dict)

    return build_info
