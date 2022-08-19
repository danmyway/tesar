#!/usr/bin/env python3

import json
from pprint import pprint
import requests
from dispatcher.__init__ import (
    TESTING_FARM_ENDPOINT,
    ARTIFACT_BASE_URL,
    get_config,
    get_arguments,
    FormatText,
)

testing_farm_api_key = get_config()
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

    payload_raw = {
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

    if not (args.dry_run or args.dry_run_cli):
        response = requests.post(TESTING_FARM_ENDPOINT, json=payload_raw)
        tf_url = TESTING_FARM_ENDPOINT
        artifact_url = ARTIFACT_BASE_URL
        task_id = response.json()["id"]
        compose = compose
        plan = plan
        err_message = json.dumps(response.json(), indent=2, sort_keys=True)
        status = response.status_code

        print_test_info = (
            f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
            f"   {plan}\n{FormatText.end}"
            f"      Test info: {tf_url}/{task_id}\n{output_divider}"
        )

        print_test_results = (
            f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
            f"   {plan}\n{FormatText.end}"
            f"      Test results: {artifact_url}/{task_id}\n{output_divider}"
        )

        print_key_error = (
            f"{output_divider}{FormatText.bold}{FormatText.blue}\n{compose}\n"
            f"   {plan}\n{FormatText.end}"
            f"      Status: {status}, Message: {err_message}\n{output_divider}"
        )

    print_payload_cli = (
        "DRY RUN | Printing out https command for required {} {} on {}:\nhttps POST {} api_key={} "
        "test:='{}' environments: '{}'\n".format(
            artifact_type,
            artifact_id.split(":")[0],
            compose,
            TESTING_FARM_ENDPOINT,
            api_key,
            str(payload_raw.get("test")).replace("'", '"'),
            str(payload_raw.get("environments")).replace("'", '"'),
        )
    )

    print_payload_dryrun_msg = f"\nDRY RUN | Printing out requested payload:"

    try:
        if args.dry_run:
            print(print_payload_dryrun_msg)
            pprint(payload_raw)
        elif args.dry_run_cli:
            print(print_payload_cli)
        elif args.debug:
            print(print_test_info)
            print("Printing payload information:")
            pprint(payload_raw)
            print(print_test_results)
        else:
            print(print_test_results)

    except KeyError:
        print(print_key_error)
