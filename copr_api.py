#!/usr/bin/env python3

from copr.v3 import BuildProxy
from envparse import env
from pathlib import Path
import logging
from tf_send_request import COMPOSE_MAPPING


env.read_envfile(str(Path(__file__) / ".env"))

config = {
    "copr_url": env.str("COPR_URL"),
    "login": env.str("COPR_LOGIN"),
    "token": env.str("COPR_TOKEN"),
    "username": env.str("COPR_USERNAME"),
}

session = BuildProxy(config)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
logger.addHandler(console_handler)


def get_info(package, reference):
    owner = "@oamg"
    artifact_module = COMPOSE_MAPPING
    build_baseurl = f"https://copr.fedorainfracloud.org/coprs/g/oamg/{package}/build/"
    pr_baseurl = f"https://github.com/oamg/{package}/pull/"
    query = session.get_list(owner, package)
    info = []
    # Get **only the last** build for given pull request
    if reference == "master" or reference == "main":
        logger.info(f"Getting copr build info for referenced {reference}.")
    else:
        logger.info(f"Getting copr build info for referenced {str.upper(reference)}.")
        logger.info(f"LINK: {pr_baseurl}{reference[2:]}")

    for build in query:
        try:
            # Get build with pull request number
            if (
                build.source_package["url"] is not None
                and reference in build.source_package["url"]
            ):
                if build.state == "running":
                    logger.warning(
                        f"There is currently {build.state} build task, consider waiting for completion."
                    )
                    logger.info(f"{build_baseurl[:-1]}" + "s/")
                elif (
                    package == "convert2rhel"
                    and reference in build.source_package["url"]
                ):
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
                    for distro in COMPOSE_MAPPING:
                        for version in distro:
                            copr_info_dict = {
                                "build_id": None,
                                "compose": None,
                                "chroot": None,
                                "distro": None,
                            }
                            copr_info_dict["compose"] = version["compose"]
                            copr_info_dict["distro"] = version["distro"]
                            for chroot in build.chroots:
                                if version["chroot"] == chroot:
                                    copr_info_dict["chroot"] = version["chroot"]
                                    copr_info_dict["build_id"] = f"{build.id}:{chroot}"
                                    logger.info(
                                        f"Assigning copr build id {build.id} for testing on {copr_info_dict['compose']} to test batch."
                                    )

                            info.append(copr_info_dict)

                    return info
        except TypeError:
            logger.warning("The PR reference might not be correct. Please check again.")
            raise
