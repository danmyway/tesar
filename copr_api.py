from copr.v3 import BuildProxy
from envparse import env
from pathlib import Path


env.read_envfile(str(Path(__file__) / ".env"))

config = {
    "copr_url": env.str("COPR_URL"),
    "login": env.str("COPR_LOGIN"),
    "token": env.str("COPR_TOKEN"),
    "username": env.str("COPR_USERNAME"),
}

session = BuildProxy(config)


def get_copr_info():
    owner = "@oamg"
    project = "convert2rhel"
    pr_hash = "pr451"
    query = session.get_list(owner, project)
    copr_info = []
    # Get *only* the last build for given pull request
    for item in range(1):
        for build in query:
            try:
                # Get build with pull request number
                if pr_hash in build.source_package["url"]:
                    # Exclude epel-6 chroot
                    build.chroots.remove("epel-6-x86_64")
                    # Get string to use as artifact id
                    for chroot in build.chroots:
                        copr_info.append(f"{build.id}:{chroot}")
                    return copr_info
            except TypeError:
                raise
