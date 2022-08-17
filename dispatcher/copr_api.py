#!/usr/bin/env python3

from copr.v3 import BuildProxy
from dispatcher.__init__ import COMPOSE_MAPPING, get_logging, get_config, get_arguments

testing_farm_api_key, copr_config = get_config()
session = BuildProxy(copr_config)
logger = get_logging()
args = get_arguments()


def get_info(package, reference, composes):
    owner = "@oamg"
    info = []
    build_reference = None
    pr_baseurl = f"https://github.com/oamg/{package}/pull/"

    if args.reference:
        query = session.get_list(owner, package)
        for build_reference in reference:
            if build_reference == "master" or build_reference == "main":
                logger.info(
                    f"Getting copr build info for referenced {build_reference}."
                )
            else:
                logger.info(
                    f"Getting copr build info for referenced {str.upper(build_reference)}."
                )
                logger.info(f"LINK: {pr_baseurl}{build_reference[2:]}")

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

    elif args.task_id:
        for build_reference in reference:
            logger.info(f"Getting copr build info for referenced ID {build_reference}.")
            build = session.get(build_reference)
            for build_info in get_build_dictionary(build, package, composes):
                info.append(build_info)

    return info, build_reference


def get_build_dictionary(build, package, composes):
    build_info = []
    build_baseurl = f"https://copr.fedorainfracloud.org/coprs/g/oamg/{package}/build/"
    # In case of a race condition occurs and referenced build is in a running state,
    # thus uninstallable, raise a warning
    if build.state == "running":
        logger.warning(
            f"There is currently {build.state} build task, consider waiting for completion."
        )
        logger.info(f"{build_baseurl[:-1]}" + "s/")
    logger.info(
        "Getting build ID for %s version %s.",
        build.projectname,
        build.source_package["version"],
    )
    build_time = build.source_package["version"].split(".")[2]
    logger.info(
        f"Built at {build_time[0:4]}-{build_time[4:6]}-{build_time[6:8]} {build_time[8:10]}:{build_time[10:12]}"
    )
    logger.info(f"LINK: {build_baseurl}{build.id}")

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
                logger.info(
                    f"Assigning copr build id {build.id} for testing on {copr_info_dict['compose']} to test batch."
                )

                build_info.append(copr_info_dict)

    return build_info
