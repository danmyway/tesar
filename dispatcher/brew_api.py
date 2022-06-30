#!/usr/bin/env python3
import koji
import logging
from dispatcher.tf_send_request import COMPOSE_MAPPING

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("[%(levelname)s] - %(message)s"))
logger.addHandler(console_handler)

session = koji.ClientSession("https://brewhub.engineering.redhat.com/brewhub")
session.gssapi_login()

epel_composes = {
    "rhel-8": ["CentOS-8-latest", "Oracle-Linux-8.5", "CentOS-8.4", "Oracle-Linux-8.4"],
    "rhel-7": ["CentOS-7-latest", "Oracle-Linux-7.9"],
}


brewbuild_baseurl = "https://brewweb.engineering.redhat.com/brew/taskinfo?taskID="


def get_brew_task_and_compose(package, reference):
    logger.info(f"Getting brew build info for {package} v{reference}.")
    query = session.listBuilds(prefix=package)
    # Append the list of TaskID's collected from the listBuilds query
    tasks = [
        build_info.get("task_id")
        for build_info in query
        if reference in build_info.get("nvr") and "el6" not in build_info.get("nvr")
    ]
    volume_names = [
        build_info.get("volume_name")
        for build_info in query
        if reference in build_info.get("nvr") and "el6" not in build_info.get("nvr")
    ]

    logger.info("Checking for available builds.")
    for i in range(len(tasks)):
        logger.info(
            f"Available build task ID {tasks[i]} for {volume_names[i]} assigned."
        )
        logger.info(f"LINK: {brewbuild_baseurl}{tasks[i]}")

    return {tasks[i]: volume_names[i] for i in range(len(tasks))}


def get_info(package, reference, composes):
    brew_dict = {}
    info = []
    compose_selection = []

    for compose in composes:
        compose_selection.append(COMPOSE_MAPPING.get(compose).get("compose"))

    for task_id, volume_name in get_brew_task_and_compose(package, reference).items():
        brew_dict[task_id] = list(
            set(compose_selection).intersection(epel_composes.get(volume_name))
        )

    for task_id in brew_dict:
        for compose in brew_dict[task_id]:
            brew_info_dict = {
                "build_id": None,
                "compose": None,
                "chroot": None,
                "distro": None,
            }
            logger.info(
                f"Assigning build id {task_id} for testing on {compose} to test batch."
            )
            brew_info_dict["build_id"] = task_id
            brew_info_dict["compose"] = compose
            for compose_choice in composes:
                if COMPOSE_MAPPING.get(compose_choice).get("compose") == compose:
                    brew_info_dict["chroot"] = COMPOSE_MAPPING.get(compose_choice).get(
                        "chroot"
                    )
                    brew_info_dict["distro"] = COMPOSE_MAPPING.get(compose_choice).get(
                        "distro"
                    )

            info.append(brew_info_dict.copy())

    return info
