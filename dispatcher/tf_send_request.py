#!/usr/bin/env python3

import json
import requests
from dispatcher.__init__ import (
    TESTING_FARM_ENDPOINT,
    ARTIFACT_BASE_URL,
    get_config,
    get_arguments,
    FormatText,
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
    tf_url = TESTING_FARM_ENDPOINT
    artifact_url = ARTIFACT_BASE_URL
    task_id = response.json()["id"]
    compose = response.json()["environments"][0]["os"]["compose"]
    plan = response.json()["test"]["fmf"]["name"]
    err_message = json.dumps(response.json(), indent=2, sort_keys=True)
    payload = json.dumps(response.json())
    payload_pretty = json.dumps(response.json(), indent=2, sort_keys=True)
    status = response.status_code

    print_test_info = (
        f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
        f"   {plan}\n{FormatText.end}"
        f"      Test info: {tf_url}/{task_id}\n{output_divider}"
    )

    print_test_pipeline_log = (
        f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
        f"   {plan}\n{FormatText.end}"
        f"      Test pipeline log: {artifact_url}/{task_id}/pipeline.log\n{output_divider}"
    )

    print_test_results = (
        f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
        f"   {plan}\n{FormatText.end}"
        f"      Test results: {tf_url}/{task_id}\n{output_divider}"
    )

    print_key_error = (
        f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
        f"   {plan}\n{FormatText.end}"
        f"      Status: {status}, Message: {err_message}\n{output_divider}"
    )

    print_payload = (
        f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
        f"   {plan}\n{FormatText.end}"
        f"      Status: {status}, Payload: {payload}\{output_divider}"
    )

    print_payload_prettify = (
        f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
        f"   {plan}\n{FormatText.end}"
        f"      Status: {status}, Payload: {payload_pretty}\n{output_divider}"
    )

    try:
        print(print_test_info)
        print(print_test_pipeline_log)
        print(print_test_results)
    except KeyError:
        print(print_key_error)
