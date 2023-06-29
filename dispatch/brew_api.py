#!/usr/bin/env python3
import koji

from dispatch.__init__ import COMPOSE_MAPPING, get_arguments, get_logging

LOGGER = get_logging()
ARGS = get_arguments()

SESSION = koji.ClientSession("https://brewhub.engineering.redhat.com/brewhub")
SESSION.gssapi_login()

EPEL_COMPOSES = {
    "rhel-8": [
        COMPOSE_MAPPING.get(i).get("compose")
        for i in COMPOSE_MAPPING
        if "epel-8" in COMPOSE_MAPPING.get(i).get("chroot")
    ],
    "rhel-7": [
        COMPOSE_MAPPING.get(i).get("compose")
        for i in COMPOSE_MAPPING
        if "epel-7" in COMPOSE_MAPPING.get(i).get("chroot")
    ],
}

BREWBUILD_BASEURL = "https://brewweb.engineering.redhat.com/brew/taskinfo?taskID="


def get_brew_task_and_compose(package, reference):
    query = SESSION.listBuilds(prefix=package)
    if ARGS.reference:
        LOGGER.info(f"Getting brew build info for {package} version/s {reference}.")
        # Append the list of TaskID's collected from the listBuilds query
        tasks = [
            build_info.get("task_id")
            for build_info in query
            for ref in reference
            if ref in build_info.get("nvr") and "el6" not in build_info.get("nvr")
        ]
        volume_names = [
            build_info.get("volume_name")
            for build_info in query
            for ref in reference
            if ref in build_info.get("nvr") and "el6" not in build_info.get("nvr")
        ]

    elif ARGS.task_id:
        LOGGER.info(f"Getting brew build info for {package} task ID {reference}.")
        tasks = reference
        volume_names = [
            build_info.get("volume_name")
            for task in tasks
            for build_info in query
            if int(task) == build_info.get("task_id")
        ]

    LOGGER.info("Checking for available builds.")
    for i in range(len(tasks)):
        LOGGER.info(
            f"Available build task ID {tasks[i]} for {volume_names[i]} assigned."
        )
        LOGGER.info(f"LINK: {BREWBUILD_BASEURL}{tasks[i]}")

    return {tasks[i]: volume_names[i] for i in range(len(tasks))}


def get_info(package, reference, composes):
    brew_dict = {}
    info = []
    compose_selection = []
    build_reference = None

    for compose in composes:
        compose_selection.append(COMPOSE_MAPPING.get(compose).get("compose"))

    for build_reference, volume_name in get_brew_task_and_compose(
        package, reference
    ).items():
        brew_dict[build_reference] = list(
            set(compose_selection).intersection(EPEL_COMPOSES.get(volume_name))
        )

    for build_reference in brew_dict:
        for compose in brew_dict[build_reference]:
            brew_info_dict = {
                "build_id": None,
                "compose": None,
                "chroot": None,
                "distro": None,
            }
            LOGGER.info(
                f"Assigning build id {build_reference} for testing on {compose} to test batch."
            )
            brew_info_dict["build_id"] = build_reference
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

    return info, build_reference
