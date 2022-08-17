#!/usr/bin/env python3
import sys

from copr.v3 import BuildProxy
from dispatcher.__init__ import COMPOSE_MAPPING, get_logging, get_config, get_arguments

testing_farm_api_key, copr_config = get_config()
session = BuildProxy(copr_config)
logger = get_logging()
args = get_arguments()


def get_info(package, reference, composes):
    owner = "@oamg"
    build_baseurl = f"https://copr.fedorainfracloud.org/coprs/g/oamg/{package}/build/"
    pr_baseurl = f"https://github.com/oamg/{package}/pull/"
    info = []
    if args.reference:
        logger.critical("This is WIP.")
        sys.exit(99)
    elif args.task_id:
        for build_id in reference:
            print(build_id)
            build = session.get(build_id)
            if build.state == "running":
                logger.warning(
                    f"There is currently {build.state} build task, consider waiting for completion."
                )
                logger.info(f"{build_baseurl[:-1]}" + "s/")
            elif package == "convert2rhel":
                # Exclude epel-6 chroot
                build.chroots.remove("epel-6-x86_64")
                # Print out the commit hash for tested copr build
                logger.info(
                    "Getting build ID for "
                    + build.projectname
                    + " version "
                    + build.source_package["version"]
                )
                build_time = build.source_package["version"].split(".")[2]
                logger.info(
                    f"Built at {build_time[0:4]}-{build_time[4:6]}-{build_time[6:8]} {build_time[8:10]}:{build_time[10:12]}"
                )
                logger.info(f"LINK: {build_baseurl}{build.id}")
                # Get string to use as artifact id

                copr_info_dict = {
                    "build_id": None,
                    "compose": None,
                    "chroot": None,
                    "distro": None,
                }
                for distro in composes:
                    copr_info_dict["compose"] = COMPOSE_MAPPING.get(distro).get(
                        "compose"
                    )
                    copr_info_dict["distro"] = COMPOSE_MAPPING.get(distro).get("distro")
                    for chroot in build.chroots:
                        if COMPOSE_MAPPING.get(distro).get("chroot") == chroot:
                            copr_info_dict["chroot"] = COMPOSE_MAPPING.get(distro).get(
                                "chroot"
                            )
                            copr_info_dict["build_id"] = f"{build.id}:{chroot}"
                            logger.info(
                                f"Assigning copr build id {build.id} for testing on {copr_info_dict['compose']} to test batch."
                            )

                info.append(copr_info_dict.copy())

    # return info
    print(info)
