TESAR
=
### Testing farm API requests dispatcher
#### Send requests to the Testing farm API through command line interface
Posting requests to Testing farm requires some json payload manipulation, which is inconvenient and might be time consuming.<br>
For example to be able to send request to test on three different composes you would need to edit 'compose', 'id' and 'distro' in the example payload below twice!<br>
To be able to send request for testing just two individual test plans on three composes, you would even need to change the 'name' three times as well.<br>
That is six changes and six `https POST` commands sent to command line.<br>
That is IMHO **exactly six times more**, than it should be. 

> Payload: {"api_key": "foo", "test": {"fmf": {"url": "https://github.com/oamg/convert2rhel", "ref": "main", "path": ".", "name": "/plans/tier0/basic_sanity_checks"}, "script": null, "sti": null}, "state": "new", "environments": [{"arch": "x86_64", "os": {"compose": "CentOS-8.4"}, "pool": null, "variables": null, "secrets": null, "artifacts": [{"id": "4533523:epel-8-x86_64", "type": "fedora-copr-build", "packages": ["convert2rhel"]}], "settings": null, "tmt": {"context": {"distro": "centos-8.4", "arch": "x86_64"}}, "hardware": null}], "notification": null, "settings": null, "created": "None", "updated": "None"}

With this script, you will be able to do all of the above with just one command!

```shell
$ python tesar.py copr --package c2r -ref pr123 -git https://github.com/oamg/convert2rhel -b main -p /plans/tier0/basic_sanity_checks /plans/tier1/rhsm -c cos84 cos7 ol8
```


## Examples

```shell 
# Test copr build for PR#123 with plan basic_sanity_check on CentOS 8.4 
$ python tesar.py copr --package c2r -ref pr123 -git https://github.com/oamg/convert2rhel -b main -p /plans/tier0/basic_sanity_checks -c cos84

# Specify which composes you want to run test plan (in this case tier0)
$ python tesar.py copr --package c2r -ref pr123 -git https://gitlab.cee.redhat.com/xyz/tmt-plans -b testing -p /plans/tier0/ -c ol7 cos8
 
# Run every test plan for brew build 0.12-3 on all composes
$ python tesar.py brew --package c2r -ref 0.12-3 -git https://github.com/oamg/convert2rhel -b main -p /plans/ 

# Specify more individual test plans
$ python tesar.py brew --package c2r -ref 0.12-3 -git https://github.com/oamg/convert2rhel -b main -p /plans/tier0/basic_sanity_checks /plans/tier1/rhsm 

```

## Currently used payload
Link to the testing farm payload documentation:

https://testing-farm.gitlab.io/api/

```json lines
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
```

# Prerequisites

### API configuration

#### Testing farm API key

To be able to send requests to Testing Farm API you need to obtain the API key.
Please, kindly refer to [testing farm onboarding](https://docs.testing-farm.io/general/0.1/onboarding.html)
to request the API key.

#### Copr API token

To be able to obtain build information for copr builds you need to obtain the [API token here](https://copr.fedorainfracloud.org/api/).<br>
Please note, that you will need to log in with your Fedora Account to be able to see the API config information.<br>
**The copr API token is valid for 180 days.**

### Packages

To be able to get information for brew-builds and copr-builds this script uses the `brew-koji` and
`python-copr` packages. <br>
It is also recommended to install `python-copr-docs` for code documentation for the python-copr package.<br>
Documentation then will be available at `/usr/share/doc/python-copr/html/ClientV3.html`
```shell
$ dnf install brew-koji
$ dnf install python-copr, python-copr-docs
```

# Run 

WIP

## Currently mapped composes
```
CentOS-8-latest
Oracle-Linux-8.5
CentOS-7-latest
Oracle-Linux-7.9
CentOS-8.4
Oracle-Linux-8.4
```

### List globaly available composes

#### Public ranch

https://api.dev.testing-farm.io/v0.1/composes

`https GET https://api.dev.testing-farm.io/v0.1/composes`

#### Private ranch

`curl -s https://gitlab.cee.redhat.com/baseos-qe/citool-config/-/raw/production/variables-composes.yaml | grep 'compose:' | tr -s ' '`

