# !/bin/python3
import os
import json
import requests
from envparse import env
from pathlib import Path

env.read_envfile(str(Path(__file__) / ".env"))

artifact_base_url = 'http://artifacts.osci.redhat.com/testing-farm'


def submit_test():
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
            "name": env.str("PLAN_NAME")
        }
      },
      "environments": [
        {
          "arch": env.str("ARCHITECTURE"),
          "os": {
            "compose": env.str("COMPOSE")
          },
          "artifacts": [
            {
              "id": env.str("ARTIFACT_ID"),
              "type": env.str("ARTIFACT_TYPE"),
              "packages": [
                env.str("PACKAGES")
              ]
            }
          ],
          "tmt": {
            "context": {
              "distro": env.str("TMT_DISTRO"),
              "arch": env.str("TMT_ARCHITECTURE")
            }
          }
        }
      ]
    }

    response = requests.post(env.str("ENDPOINT"), json=payload)
    print('Status: {status}, Payload: {payload}'.format(
        status=response.status_code, payload=json.dumps(response.json(), indent=2, sort_keys=True),
    ))
    print()
    print('Test info: {url}/{id}'.format(
        url=env.str("ENDPOINT"), id=response.json()['id'],
    ))
    print('Test status: {url}/{id}'.format(
        url=artifact_base_url, id=response.json()['id']
    ))


if __name__ == "__main__":
    submit_test()
