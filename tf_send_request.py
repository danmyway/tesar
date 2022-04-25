# !/bin/python3
import json
import requests
from envparse import env
from pathlib import Path
from brew_api import get_brew_info
from copr_api import get_copr_info
from parse_args import get_args

env.read_envfile(str(Path(__file__) / ".env"))

artifact_base_url = "http://artifacts.osci.redhat.com/testing-farm"

el7_distros = ["centos-7", "oraclelinux-7"]
el8_distros = ["centos-8", "oraclelinux-8"]

def submit_test(args):
    """
    Payload documentation > https://testing-farm.gitlab.io/api/#operation/requestsPost
    """

    payload = {
        "api_key": env.str("API_KEY"),
        "test": {
            "fmf": {
                "url": env.str("FMF_GIT_URL"),
                "ref": env.str("FMF_BRANCH_REFERENCE"),
                "path": env.str("GIT_PATH"),
                "name": env.str("PLAN_NAME"),
            }
        },
        "environments": [
            {
                "arch": env.str("ARCHITECTURE"),
                "os": {"compose": args.compose},
                "artifacts": [
                    {
                        "id": args.artifact_id,
                        "type": args.artifact_type,
                        "packages": [env.str("PACKAGES")],
                    }
                ],
                "tmt": {
                    "context": {
                        "distro": env.str("TMT_DISTRO"),
                        "arch": env.str("TMT_ARCHITECTURE"),
                    }
                },
            }
        ],
    }

    response = requests.post(env.str("ENDPOINT"), json=payload)
    print(
        "Status: {status}, Payload: {payload}\n".format(
            status=response.status_code,
            payload=json.dumps(response.json(), indent=2, sort_keys=True),
        )
    )
    print(
        "Test info: {url}/{id}".format(
            url=env.str("ENDPOINT"),
            id=response.json()["id"],
        )
    )
    print(
        "Test status: {url}/{id}\n".format(
            url=artifact_base_url, id=response.json()["id"]
        )
    )




