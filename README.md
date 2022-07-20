# Table of contents
1. [Introduction](#tesar)
2. [Prerequisites](#prerequisites)
    1. [API configuration](#api-configuration)
        1. [Testing farm API key](#testing-farm-api-key)
        2. [Copr API token](#copr-api-token)
    2. [Package dependencies](#package-dependencies)
3. [Setup](#setup)
    1. [Installation](#installation)
        1. [Clone](#clone)
        2. [Install](#install)
        3. [Set up configuration file](#set-up-configuration-file)
            1. [Config file template](#config-file-template)
    2. [Run](#run)
        1. [Examples](#examples)
4. [Currently used variables](#currently-used-variables)
    1. [Payload](#payload)
    2. [Mapped composes](#mapped-composes)
        1. [List globally available composes](#list-globally-available-composes)
            1. [Public ranch](#public-ranch)
            2. [Private ranch](#private-ranch)
    


TESAR
=
### Testing farm API requests dispatcher
#### Send requests to the Testing farm API through command line interface
Posting requests to the Testing farm requires some json payload manipulation, which is inconvenient and might be time-consuming.<br><br>
For example, to be able to send a request to test on three different composes you would need to edit 'compose', 'id' and 'distro' in the example payload below twice!<br>
To be able to send request for testing just two individual test plans on three composes, you would even need to change the 'name' three times as well.<br><br>
That is six changes and six `https POST` commands sent to command line.<br>
That is IMHO **exactly six times more**, than it should be. 

> Payload: {"api_key": "foo", "test": {"fmf": {"url": "https://github.com/oamg/convert2rhel", "ref": "main", "path": ".", "name": "/plans/tier0/basic_sanity_checks"}, "script": null, "sti": null}, "state": "new", "environments": [{"arch": "x86_64", "os": {"compose": "CentOS-8.4"}, "pool": null, "variables": null, "secrets": null, "artifacts": [{"id": "4533523:epel-8-x86_64", "type": "fedora-copr-build", "packages": ["convert2rhel"]}], "settings": null, "tmt": {"context": {"distro": "centos-8.4", "arch": "x86_64"}}, "hardware": null}], "notification": null, "settings": null, "created": "None", "updated": "None"}

With this script, you will be able to do all of the above with just one command!

```shell
python tesar.py copr --package c2r -ref pr123 -git https://github.com/oamg/convert2rhel -b main -p /plans/tier0/basic_sanity_checks /plans/tier1/rhsm -c cos84 cos7 ol8
```

# Prerequisites

### API configuration

#### Testing farm API key

To be able to send requests to Testing Farm API, you need to obtain the API key.
Please, kindly refer to [testing farm onboarding](https://docs.testing-farm.io/general/0.1/onboarding.html)
to request the API key.<br>
Add the obtained api_key to the config file as instructed below.

#### Copr API token

To be able to obtain build information for copr builds, you need to obtain the [API token here](https://copr.fedorainfracloud.org/api/).<br>
Please note, that you will need to log in with your Fedora Account to be able to see the API config information.<br>
Add the obtained API credentials to the config file `~/.config/tesar`<br>
**The copr API token is valid for 180 days.**

### Package dependencies

To be able to get information for brew-builds and copr-builds this script uses the `brewkoji` and
`python-copr` packages. <br>
If needed, install `python-copr-doc` for code documentation for the python-copr package.<br>
Documentation then will be available at `/usr/share/doc/python-copr/html/ClientV3.html`
It is also recommended to install `python-kerberos`, `python-requests`, `python-requests-kerberos`, `make`, `krb5-devel`, `gcc`, `python3-devel`, `redhat-rpm-config` to be able to run the script.

Before installing the packages, it is advised to download the `rcm-tools-fedora.repo` to be able to install `brewkoji`

```shell
sudo su 
curl -L https://download.devel.redhat.com/rel-eng/RCMTOOLS/rcm-tools-fedora.repo -o /etc/yum.repos.d/rcm-tools-fedora.repo
```

Installing the packages

```shell
dnf install brewkoji python-copr python-copr-doc python-kerberos python-requests python-requests-kerberos make krb5-devel gcc python3-devel redhat-rpm-config
```

# Setup

### Installation

#### Clone
Clone repository to your local machine.
```shell
# ssh
git clone git@gitlab.cee.redhat.com:ddiblik/tesar.git
# https
git clone https://gitlab.cee.redhat.com/ddiblik/tesar.git
```
#### Install
Change directory to the cloned folder, run virtual environment and install the package.
```shell
cd ~/tesar
pipenv --site-packages shell
pip install .
```
#### Set up configuration file
Set up config file with obtained testing farm API key and copr API credentials replacing {values} with correct credentials
```shell
touch ~/.config/tesar && printf "[copr-cli]\nCOPR_LOGIN={your copr login}\nCOPR_USERNAME={your copr username}\nCOPR_TOKEN={your copr api token}\nCOPR_URL=https://copr.fedorainfracloud.org\n[testing-farm]\nAPI_KEY={your testing farm api key}" > ~/.config/tesar
```
or copy provided file and edit with your favourite editor, e.g.
```shell
cp ./dispatcher/tesar ~/.config/tesar 
vim ~/.config/tesar
```
Config file template <a name="config-file-template"></a>
```
[copr-cli]
COPR_LOGIN=
COPR_USERNAME=
COPR_TOKEN=
COPR_URL=https://copr.fedorainfracloud.org
[testing-farm]
API_KEY=
```
### Run
If you installed the script via `pip install .` you should be able to run the script by running `tesar` command.<br>
Otherwise run with `python tesar.py`.
#### Examples

```shell 
# Test copr build for PR#123 with plan basic_sanity_check on CentOS 8.4 
$ tesar copr c2r -ref pr123 -git https://github.com/oamg/convert2rhel -b main -p /plans/tier0/basic_sanity_checks -c cos84

# Specify which composes you want to run test plan (in this case tier0)
$ tesar copr c2r -ref pr123 -git https://gitlab.cee.redhat.com/xyz/tmt-plans -b testing -p /plans/tier0/ -c ol7 cos8
 
# Run every test plan for brew build 0.12-3 on all composes
$ tesar brew c2r -ref 0.12-3 -git https://github.com/oamg/convert2rhel -b main -p /plans/ 

# Specify more individual test plans
$ tesar brew c2r -ref 0.12-3 -git https://github.com/oamg/convert2rhel -b main -p /plans/tier0/basic_sanity_checks /plans/tier1/rhsm 

```


# Currently used variables

## Payload

Link to the testing farm payload documentation:<br>
https://testing-farm.gitlab.io/api/ <br>
For convert2RHEL testing we are currently using this form of payload:
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


## Mapped composes
```
CentOS-8-latest
Oracle-Linux-8.6
CentOS-7-latest
Oracle-Linux-7.9
CentOS-8.4
Oracle-Linux-8.4
```

### List globally available composes
Testing farm has many available composes on both public and private ranch.<br>
To list them use commands bellow.
#### Public ranch

https://api.dev.testing-farm.io/v0.1/composes

`https GET https://api.dev.testing-farm.io/v0.1/composes`

#### Private ranch

`curl -s https://gitlab.cee.redhat.com/baseos-qe/citool-config/-/raw/production/variables-composes.yaml | grep 'compose:' | tr -s ' '`
