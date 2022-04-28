# !/bin/python3
import koji
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("[%(levelname)s] - %(message)s"))
logger.addHandler(console_handler)

session = koji.ClientSession("https://brewhub.engineering.redhat.com/brewhub")
session.gssapi_login()

el8_composes = ["CentOS-8-latest", "Oracle-Linux-8.5"]
el7_composes = ["CentOS-7-latest", "Oracle-Linux-7.9"]

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
        logger.info(f"Available build task ID {tasks[i]} for {volume_names[i]} assigned.")
        logger.info(f"LINK: {brewbuild_baseurl}{tasks[i]}")

    return {tasks[i]: volume_names[i] for i in range(len(tasks))}


def get_brew_info(package, reference):
    brew_info = {}
    for task_id, volume_name in get_brew_task_and_compose(package, reference).items():
        if volume_name == "rhel-8":
            brew_info[task_id] = el8_composes
        if volume_name == "rhel-7":
            brew_info[task_id] = el7_composes

    for task_id in brew_info:
        for compose in brew_info[task_id]:
            logger.info(f"Assigning build id {task_id} for testing on {compose} to test batch.")


    return brew_info


if __name__ == "__main__":
    print(get_brew_info())
