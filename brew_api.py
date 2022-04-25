# !/bin/python3
import koji


session = koji.ClientSession("https://brewhub.engineering.redhat.com/brewhub")
session.gssapi_login()

package_prefix = "convert2rhel"
version = "0.25-4"

el8_composes = ["CentOS-8-latest", "Oracle-Linux-8.5"]
el7_composes = ["CentOS-7-latest", "Oracle-Linux-7.9"]


def get_brew_task_and_compose():
    query = session.listBuilds(prefix=package_prefix)
    # Append the list of TaskID's collected from the listBuilds query
    tasks = [
        build_info.get("task_id")
        for build_info in query
        if version in build_info.get("nvr") and "el6" not in build_info.get("nvr")
    ]
    volume_names = [
        build_info.get("volume_name")
        for build_info in query
        if version in build_info.get("nvr") and "el6" not in build_info.get("nvr")
    ]

    return {tasks[i]: volume_names[i] for i in range(len(tasks))}


def get_brew_info():
    brew_info = {}
    for task_id, volume_name in get_brew_task_and_compose().items():
        if volume_name == "rhel-8":
            brew_info[task_id] = el8_composes
        if volume_name == "rhel-7":
            brew_info[task_id] = el7_composes

    return brew_info
