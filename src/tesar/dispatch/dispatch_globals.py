"""Single place for all global variables of a dispatch module"""

LATEST_TASKS_FILE = "/tmp/tesar_latest_jobs"
DEFAULT_TASKS_FILE = "./report_jobs"
TESTING_FARM_ENDPOINT = "https://api.dev.testing-farm.io/v0.1/requests"
ARTIFACT_BASE_URL = "http://artifacts.osci.redhat.com/testing-farm"


ARTIFACT_MAPPING = {"brew": "redhat-brew-build", "copr": "fedora-copr-build"}
PACKAGE_MAPPING = {"c2r": "convert2rhel", "leapp-repository": "leapp-repository"}

COPR_CONFIG = {"copr_url": "https://copr.fedorainfracloud.org"}

LP_COMPOSE_MAPPING = {
    "79to84": {
        "compose": "RHEL-7.9-ZStream",
        "distro": "rhel-7.9",
        "chroot": "epel-7-x86_64",
    },
    "79to86": {
        "compose": "RHEL-7.9-ZStream",
        "distro": "rhel-7.9",
        "chroot": "epel-7-x86_64",
    },
    "79to88": {
        "compose": "RHEL-7.9-ZStream",
        "distro": "rhel-7.9",
        "chroot": "epel-7-x86_64",
    },
    "86to90": {
        "compose": "RHEL-8.6.0-Nightly",
        "distro": "rhel-8.6",
        "chroot": "epel-8-x86_64",
    },
    "87to90": {
        "compose": "RHEL-8.7.0-Nightly",
        "distro": "rhel-8.7",
        "chroot": "epel-8-x86_64",
    },
    "88to92": {
        "compose": "RHEL-8.8.0-Nightly",
        "distro": "rhel-8.8",
        "chroot": "epel-8-x86_64",
    },
}

C2R_COMPOSE_MAPPING = {
    "cos7": {
        "compose": "CentOS-7-latest",
        "distro": "centos-7",
        "chroot": "epel-7-x86_64",
    },
    "ol7": {
        "compose": "OL7.9-x86_64-HVM-2023-01-05",
        "distro": "oracle-7",
        "chroot": "epel-7-x86_64",
    },
    "cos8": {
        "compose": "CentOS-8-latest",
        "distro": "centos-8-latest",
        "chroot": "epel-8-x86_64",
    },
    "ol8": {
        "compose": "OL8.9-x86_64-HVM-2024-02-02",
        "distro": "oracle-8-latest",
        "chroot": "epel-8-x86_64",
    },
    "al88": {
        "compose": "AlmaLinux OS 8.8.20230524 x86_64",
        "distro": "alma-8.8",
        "chroot": "epel-8-x86_64",
    },
    "al8": {
        "compose": "AlmaLinux OS 8.10.20240530 x86_64",
        "distro": "alma-8-latest",
        "chroot": "epel-8-x86_64",
    },
    "roc88": {
        "compose": "Rocky-8-EC2-Base-8.8-20230518.0.x86_64",
        "distro": "rocky-8.8",
        "chroot": "epel-8-x86_64",
    },
    "roc8": {
        "compose": "Rocky-8-EC2-Base-8.10-20240528.0.x86_64",
        "distro": "rocky-8-latest",
        "chroot": "epel-8-x86_64",
    },
    "str8": {
        "compose": "CentOS-Stream-8",
        "distro": "stream-8-latest",
        "chroot": "epel-8-x86_64",
    },
    "al9": {
        "compose": "AlmaLinux OS 9.4.20240509 x86_64",
        "distro": "alma-9-latest",
        "chroot": "epel-9-x86_64",
    },
    "ol9": {
        "compose": "OL9.3-x86_64-HVM-2024-02-02",
        "distro": "oracle-9-latest",
        "chroot": "epel-9-x86_64",
    },
    "roc9": {
        "compose": "Rocky-9-EC2-Base-9.4-20240509.0.x86_64",
        "distro": "rocky-9-latest",
        "chroot": "epel-9-x86_64",
    },
    "str9": {
        "compose": "CentOS-Stream-9",
        "distro": "stream-9-latest",
        "chroot": "epel-9-x86_64",
    },
}
