# !/bin/python3
import json
import requests
from envparse import env
from pathlib import Path


env.read_envfile(str(Path(__file__) / ".env"))

artifact_base_url = "http://artifacts.osci.redhat.com/testing-farm"


def submit_test(
    git_url,
    git_branch,
    git_path,
    plan,
    architecture,
    compose,
    artifact_id,
    artifact_type,
    package,
    tmt_distro,
    tmt_architecture,
    api_key=env.str("API_KEY"),
):
    """
    Payload documentation > https://testing-farm.gitlab.io/api/#operation/requestsPost
    """

    payload = {
        "api_key": api_key,
        "test": {
            "fmf": {
                "url": git_url,
                "ref": git_branch,
                "path": git_path,
                "name": plan,
            }
        },
        "environments": [
            {
                "arch": architecture,
                "os": {"compose": compose},
                "artifacts": [
                    {
                        "id": artifact_id,
                        "type": artifact_type,
                        "packages": [package],
                    }
                ],
                "tmt": {
                    "context": {
                        "distro": tmt_distro,
                        "arch": tmt_architecture,
                    }
                },
            }
        ],
    }

    response = requests.post(env.str("ENDPOINT"), json=payload)
    # print(
    #     "Status: {status}, Payload: {payload}\n".format(
    #         status=response.status_code,
    #         payload=json.dumps(response.json(), indent=2, sort_keys=True),
    #     )
    # )
    try:
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
    except KeyError:
        print(
            "Status: {status}, Message: {message}\n".format(
                status=response.status_code,
                message=json.dumps(response.json(), indent=2, sort_keys=True),
            )
        )
