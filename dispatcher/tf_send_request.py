#!/usr/bin/env python3

import json
import requests
from dispatcher.__init__ import TESTING_FARM_ENDPOINT, ARTIFACT_BASE_URL, get_config

testing_farm_api_key, copr_config = get_config()


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
    api_key=testing_farm_api_key,
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

    response = requests.post(TESTING_FARM_ENDPOINT, json=payload)

    # TODO DEBUG logger
    # print(
    #     "Status: {status}, Payload: {payload}\n".format(
    #         status=response.status_code,
    #         payload=json.dumps(response.json()),
    #     )
    # )
    # TODO DEBUG logger prettify
    # print(
    #     "Status: {status}, Payload: {payload}\n".format(
    #         status=response.status_code,
    #         payload=json.dumps(response.json(), indent=2, sort_keys=True),
    #     )
    # )
    try:
        print(
            "Test info: {url}/{id}".format(
                url=TESTING_FARM_ENDPOINT,
                id=response.json()["id"],
            )
        )
        print(
            "Test pipeline log: {url}/{id}/pipeline.log\n".format(
                url=ARTIFACT_BASE_URL, id=response.json()["id"]
            )
        )
        print(
            "Test results: {url}/{id}\n".format(
                url=ARTIFACT_BASE_URL, id=response.json()["id"]
            )
        )
    except KeyError:
        print(
            "Status: {status}, Message: {message}\n".format(
                status=response.status_code,
                message=json.dumps(response.json(), indent=2, sort_keys=True),
            )
        )
