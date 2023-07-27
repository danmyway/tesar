#!/usr/bin/env python3
import json
import os
import time
from pprint import pprint

import requests

from dispatch.__init__ import (
    ARTIFACT_BASE_URL,
    LATEST_TASKS_FILE,
    TESTING_FARM_ENDPOINT,
    FormatText,
    get_arguments,
    get_config,
    get_datetime,
)

CLOUD_RESOURCES_TAG, TESTING_FARM_API_KEY = get_config()
ARGS = get_arguments()
OUTPUT_DIVIDER = 20 * "="

# For some images (Alma, Rocky) we need to use post-install-script to enable root login.
POST_INSTALL_SCRIPT = (
    "#!/bin/bash\nsudo sed -i 's/^.*ssh-rsa/ssh-rsa/' /root/.ssh/authorized_keys"
)

if os.path.exists(LATEST_TASKS_FILE):
    os.unlink(LATEST_TASKS_FILE)

DATETIME_STAMP = get_datetime()

LATEST_TASKS_ARCHIVE = f"./tesar_latest_jobs_{DATETIME_STAMP}"


def submit_test(
    git_url,
    git_branch,
    git_path,
    plan,
    planfilter,
    testfilter,
    architecture,
    compose,
    pool,
    source_release,
    target_release,
    artifact_id,
    artifact_type,
    package,
    tmt_distro,
    tmt_architecture,
    api_key=TESTING_FARM_API_KEY,
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
                "plan_filter": planfilter,
                "test_filter": testfilter,
            }
        },
        "environments": [
            {
                "arch": architecture,
                "os": {"compose": compose},
                "pool": pool,
                "variables": {
                    "SOURCE_RELEASE": source_release,
                    "TARGET_RELEASE": target_release,
                },
                "artifacts": [
                    {
                        "id": artifact_id,
                        "type": artifact_type,
                        "packages": [package],
                    }
                ],
                "settings": {
                    "provisioning": {
                        "post_install_script": POST_INSTALL_SCRIPT,
                        "tags": {"BusinessUnit": CLOUD_RESOURCES_TAG},
                    }
                },
                "tmt": {
                    "context": {
                        "distro": tmt_distro,
                        "arch": tmt_architecture,
                    }
                },
            }
        ],
    }

    if not (ARGS.dry_run or ARGS.dry_run_cli):

        response = requests.post(TESTING_FARM_ENDPOINT, json=payload_raw)
        tf_url = TESTING_FARM_ENDPOINT
        task_id = response.json()["id"]
        latest_jobs_file = open(LATEST_TASKS_FILE, "a")
        latest_jobs_archive = open(LATEST_TASKS_ARCHIVE, "a")
        artifact_url = f"{ARTIFACT_BASE_URL}/{task_id}"
        compose = compose
        plan = plan
        err_message = json.dumps(response.json(), indent=2, sort_keys=True)
        request_status = response.status_code

        def _response_watcher(printout):
            """
            Wait for default 20 seconds for an OK response from the artifact URL.
            If the response is not successful notify user.
            """
            if ARGS.no_wait:
                print(printout)
                return
            response_timeout = ARGS.wait
            clear_line = "\x1b[2K"
            while True:
                artifact_url_response = requests.get(artifact_url)
                artifact_url_status = artifact_url_response.status_code
                artifact_url_message = artifact_url_response.reason
                print(end=clear_line)
                print(
                    f"{FormatText.bold}Waiting for a successful response for {response_timeout} seconds. "
                    f"Current response is: {artifact_url_status} {artifact_url_message}",
                    end="\r",
                    flush=True,
                )
                time.sleep(1)
                response_timeout -= 1
                if artifact_url_status > 200 and response_timeout == 0:
                    print(end=clear_line)
                    print(
                        f"{FormatText.bold}Processing the request takes longer this time.\n"
                        f"The request response is still {artifact_url_status} {artifact_url_message}\n"
                        f"Here is the link for the requested job, try refreshing the website after a couple of minutes.\n",
                        flush=True,
                    )
                    print(printout)
                    break
                elif artifact_url_status == 200:
                    print(f"\nResponse successful!\n")
                    print(printout)
                    break

        print_test_info = (
            f"{OUTPUT_DIVIDER}{FormatText.bold}{FormatText.blue}\n{compose}\n"
            f"   {plan}\n{FormatText.end}"
            f"      Test info: {tf_url}/{task_id}\n{OUTPUT_DIVIDER}"
        )

        print_test_results = (
            f"{OUTPUT_DIVIDER}{FormatText.bold}{FormatText.blue}\n{compose}\n"
            f"   {plan}\n{FormatText.end}"
            f"      Test results: {artifact_url}\n{OUTPUT_DIVIDER}"
        )

        print_key_error = (
            f"{OUTPUT_DIVIDER}{FormatText.bold}{FormatText.blue}\n{compose}\n"
            f"   {plan}\n{FormatText.end}"
            f"      Status: {request_status}, Message: {err_message}\n{OUTPUT_DIVIDER}"
        )

    print_payload_cli = "DRY RUN | Printing out https command for required {} {} on {}:\nhttps POST {} api_key={} " "test:='{}' environments: '{}'\n".format(
        artifact_type,
        artifact_id.split(":")[0],
        compose,
        TESTING_FARM_ENDPOINT,
        api_key,
        str(payload_raw.get("test")).replace("'", '"'),
        str(payload_raw.get("environments")).replace("'", '"'),
    )

    print_payload_dryrun_msg = f"\nDRY RUN | Printing out requested payload:"

    payload_formatted = json.dumps(payload_raw, indent=4)
    from pygments import highlight, lexers, formatters

    colorful_json = highlight(
        payload_formatted, lexers.JsonLexer(), formatters.TerminalFormatter()
    )

    try:
        if ARGS.dry_run:
            print(print_payload_dryrun_msg)
            print(colorful_json)
        elif ARGS.dry_run_cli:
            print(print_payload_cli)
        elif ARGS.debug:
            _response_watcher(print_test_info)
            print("Printing payload information:")
            pprint(payload_raw)
            print(print_test_results)
        else:
            _response_watcher(print_test_results)

        if not (ARGS.dry_run or ARGS.dry_run_cli):
            latest_jobs_file.write(f"{task_id}\n")
            latest_jobs_archive.write(f"{task_id}\n")

    except KeyError:
        print(print_key_error)
