#!/usr/bin/env python3

import json
import sys

import requests
from dispatcher.__init__ import (
    TESTING_FARM_ENDPOINT,
    ARTIFACT_BASE_URL,
    get_config,
    get_arguments,
    get_datetime,
)

testing_farm_api_key, copr_config = get_config()
args = get_arguments()
output_divider = 20 * "="


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

    print_test_info = (
        output_divider
        + "\033[1m\033[92m\n{compose}\n   {plan}\033[0m\n      Test info: {url}/{id}\n".format(
            url=TESTING_FARM_ENDPOINT,
            id=response.json()["id"],
            compose=response.json()["environments"][0]["os"]["compose"],
            plan=response.json()["test"]["fmf"]["name"],
        )
        + output_divider
    )
    print_test_pipeline_log = (
        output_divider
        + "\033[1m\033[92m\n{compose}\n   {plan}\033[0m\n      Test pipeline log: {url}/{id}/pipeline.log\n".format(
            url=ARTIFACT_BASE_URL,
            id=response.json()["id"],
            compose=response.json()["environments"][0]["os"]["compose"],
            plan=response.json()["test"]["fmf"]["name"],
        )
        + output_divider
    )
    print_test_results = (
        output_divider
        + "\033[1m\033[92m\n{compose}\n   {plan}\033[0m\n      Test results: {url}/{id}\n".format(
            url=ARTIFACT_BASE_URL,
            id=response.json()["id"],
            compose=response.json()["environments"][0]["os"]["compose"],
            plan=response.json()["test"]["fmf"]["name"],
        )
        + output_divider
    )
    print_key_error = (
        output_divider
        + "\033[1m\033[92m\n{compose}\n   {plan}\033[0m\n      Status: {status}, Message: {message}\n".format(
            status=response.status_code,
            message=json.dumps(response.json(), indent=2, sort_keys=True),
            compose=response.json()["environments"][0]["os"]["compose"],
            plan=response.json()["test"]["fmf"]["name"],
        )
        + output_divider
    )
    print_payload = (
        output_divider
        + "\033[1m\033[92m\n{compose}\n   {plan}\033[0m\n      Status: {status}, Payload: {payload}\n".format(
            status=response.status_code,
            payload=json.dumps(response.json()),
            compose=response.json()["environments"][0]["os"]["compose"],
            plan=response.json()["test"]["fmf"]["name"],
        )
        + output_divider
    )
    print_payload_prettify = (
        output_divider
        + "\033[1m\033[92m\n{compose}\n   {plan}\033[0m\n      Status: {status}, Payload: {payload}\n".format(
            status=response.status_code,
            payload=json.dumps(response.json(), indent=2, sort_keys=True),
            compose=response.json()["environments"][0]["os"]["compose"],
            plan=response.json()["test"]["fmf"]["name"],
        )
        + output_divider
    )

    try:
        print(print_test_info)
        print(print_test_pipeline_log)
        print(print_test_results)
    except KeyError:
        print(print_key_error)
