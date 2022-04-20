# !/bin/python3
import koji

session = koji.ClientSession('https://brewhub.engineering.redhat.com/brewhub')
session.gssapi_login()


def get_task_id():
    query = session.listBuilds(prefix='convert2rhel')
    version = '0.25-4'
    # Append the list of TaskID's collected from the listBuilds query
    tasks = [build_info.get('task_id') for build_info in query if version in build_info.get('nvr')]
    return tasks
