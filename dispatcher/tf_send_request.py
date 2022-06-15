#!/usr/bin/env python3

import json
import requests
from envparse import env
from pathlib import Path


env.read_envfile(str(Path(__file__) / ".env"))

TESTINGFARM_ENDPOINT = "https://api.dev.testing-farm.io/v0.1/requests"

ARTIFACT_BASE_URL = "http://artifacts.osci.redhat.com/testing-farm"

ARTIFACT_MAPPING = {"brew": "redhat-brew-build", "copr": "fedora-copr-build"}
PACKAGE_MAPPING = {"c2r": "convert2rhel", "leapp": "leapp"}

COMPOSE_MAPPING = {
    "cos8": {
        "compose": "CentOS-8-latest",
        "distro": "centos-8",
        "chroot": "epel-8-x86_64",
    },
    "ol8": {
        "compose": "Oracle-Linux-8.5",
        "distro": "oraclelinux-8",
        "chroot": "epel-8-x86_64",
    },
    "cos7": {
        "compose": "CentOS-7-latest",
        "distro": "centos-7",
        "chroot": "epel-7-x86_64",
    },
    "ol7": {
        "compose": "Oracle-Linux-7.9",
        "distro": "oraclelinux-7",
        "chroot": "epel-7-x86_64",
    },
    "cos84": {
        "compose": "CentOS-8.4",
        "distro": "centos-8.4",
        "chroot": "epel-8-x86_64",
    },
    "ol84": {
        "compose": "Oracle-Linux-8.4",
        "distro": "oraclelinux-8.4",
        "chroot": "epel-8-x86_64",
    },
}


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

    response = requests.post(TESTINGFARM_ENDPOINT, json=payload)

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
                url=TESTINGFARM_ENDPOINT,
                id=response.json()["id"],
            )
        )
        print(
            "Test status: {url}/{id}\n".format(
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
