# Table of contents
1. [Introduction](#tesar)
2. [Prerequisites](#prerequisites)
   1. [API configuration](#api-configuration)
       1. [Testing farm API key](#testing-farm-api-key)
   2. [Cloud Resources Tag](#cloud-resources-tag)
   3. [Package dependencies](#package-dependencies)
3. [Setup](#setup)
   1. [Installation](#installation)
       1. [Clone](#clone)
       2. [Install](#install)
       3. [Set up configuration file](#set-up-configuration-file)
       4. [Config file template](#config-file-template)
   2. [Usage](#usage)
       1. [Commands](#commands)
          1. [Test](#test)
          2. [Report](#report)
       2. [Examples](#examples)
4. [Currently used variables](#currently-used-variables)
    1. [Payload](#payload)
    2. [Mapped composes](#mapped-composes)
        1. [List globally available composes](#list-globally-available-composes)
            1. [Public ranch](#public-ranch)
            2. [Private ranch](#private-ranch)



TESAR
=
### (TES)ting farm (A)PI (R)equests dispatcher
#### Send requests to the Testing Farm API through command line interface
Posting requests to the Testing farm requires some json payload manipulation, which is inconvenient and might be time-consuming.<br><br>
For example, to be able to send a request to test on three different composes you would need to edit 'compose', 'id' and 'distro' in the example payload below twice!<br>
To be able to send request for testing just two individual test plans on three composes, you would even need to change the 'name' three times as well.<br><br>
That is six changes and six `https POST` commands sent to command line.<br>
That is IMHO **exactly six times more**, than it should be.

> Payload: {"api_key": "foo", "test": {"fmf": {"url": "https://github.com/oamg/convert2rhel", "ref": "main", "path": ".", "name": "/plans/tier0/basic_sanity_checks"}, "script": null, "sti": null}, "state": "new", "environments": [{"arch": "x86_64", "os": {"compose": "CentOS-8.4"}, "pool": null, "variables": null, "secrets": null, "artifacts": [{"id": "4533523:epel-8-x86_64", "type": "fedora-copr-build", "packages": ["convert2rhel"]}], "settings": null, "tmt": {"context": {"distro": "centos-8.4", "arch": "x86_64"}}, "hardware": null}], "notification": null, "settings": null, "created": "None", "updated": "None"}

With this script, you will be able to do all of the above with just one command!

```shell
tesar test copr c2r -ref pr123 -g github oamg main -p /plans/tier0/basic_sanity_checks /plans/tier1/rhsm -c cos84 cos7 ol8
```

# Prerequisites

### API Configuration

#### Testing Farm API Key

To be able to send requests to Testing Farm API, you need to obtain the API key.
Please, kindly refer to [testing farm onboarding](https://docs.testing-farm.io/general/0.1/onboarding.html)
to request the API key.<br>
Add the obtained api_key to the config file as instructed below.

### Cloud Resources Tag

Each team using the Testing Farm to run test efforts has a BusinessUnit tag assigned.<br>
Those are important to use for correct reporting efforts of a cloud spend for each team.<br>
Ask peers in your team for the tag value.

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
git clone git@github.com:danmyway/tesar.git
# https
git clone https://github.com/danmyway/tesar.git
```
#### Install
Change directory to the cloned folder, run virtual environment and install the package.
```shell
cd ~/tesar
pipenv --site-packages shell
pip install .
```
#### Set up configuration file
Set up config file with obtained Testing Farm API key and Cloud Resources Tag that helps with tracking cloud spend.

```shell
touch ~/.config/tesar && printf "[testing-farm]\nAPI_KEY={your testing farm api key}\n[cloud-resources-tag]\nCLOUD_RESOURCES_TAG={tag}" > ~/.config/tesar
```
or copy provided file and edit with your favourite editor, e.g.
```shell
cp ./tesar.temp ~/.config/tesar
vim ~/.config/tesar
```

##### Config file template
```
[testing-farm]
API_KEY=
[cloud-resources-tag]
CLOUD_RESOURCES_TAG=
```
### Usage
If you installed the script via `pip install .` you should be able to run the script by running `tesar` command.<br>
Otherwise run with `python3 __main__.py` from the `tesar/tesar` directory.

#### Commands
As of now tesar is able to perform two tasks.
`test` feeds the request payload with provided arguments and dispatches a test job to the Testing Farm.
`report` feeds the test results back to the command line and downloads the log files.

##### Test
> **_NOTE:_** Even though there are some mentions of leapp and leapp-repository in the code. The Leapp project is not yet fully supported by tesar for test jobs dispatching.

The goal of tesar is to make requesting test jobs as easy as possible.<br>
Instead of looking for build IDs to pass to the payload, all you need to know is a `--reference` for a pull request number associated with the build you need to test. For brew builds you just need to know the release version.<br>
In case you have the Build ID handy, you can use that instead of the reference.<br>
Use `-g/--git` to point from where the test metadata and code should be run. Specify the repository base e.g. github, repository owner and the branch from which the tests should run.<br>
Multiple `--plans` can be specified and will be dispatched in separate jobs. The same applies to `--planfilter` and `--testfilter`.<br>
You can look for possible [targeted OS' below](#mapped-composes), multiple can be requested and will be dispatched in separate jobs.
Use `-w/--wait` to override the default 20 seconds waiting time for successful response from the endpoint, or `-nw/--no-wait` to skip the wait time.
If for any reason you would need the raw payload, use `--dry-run` to get it printed to the command line or use `--dry-run-cli` to print out the full usable `http POST` command.

```shell
❯ tesar test --help
usage: tesar test [-h] (-ref REFERENCE [REFERENCE ...] | -id TASK_ID [TASK_ID ...]) [-g GIT [GIT ...]] [-gp GIT_PATH] [-a ARCHITECTURE]
                  (-p PLANS [PLANS ...] | -pf PLANFILTER [PLANFILTER ...] | -tf TESTFILTER [TESTFILTER ...])
                  [-c {cos7,ol7,cos8,ol8,al86,al8,roc86,roc8} [{cos7,ol7,cos8,ol8,al86,al8,roc86,roc8} ...]] [-pw] [-w WAIT] [-nw] [-l] [--dry-run] [--dry-run-cli] [--debug]
                  artifact_type package

Send requests to the Testing Farm conveniently.

positional arguments:
  artifact_type         Choose which type of artifact to test. Choices: brew, copr
  package               Choose package to test. Choices: c2r, leapp

options:
  -h, --help            show this help message and exit
  -ref REFERENCE [REFERENCE ...], --reference REFERENCE [REFERENCE ...]
                        Mutually exclusive with respect to --task-id. For brew: Specify the reference version to find the correct artifact (e.g. 0.1-2, 0.1.2). For
                        copr: Specify the pull request reference to find the correct artifact (e.g. pr123, main, master, ...).
  -id TASK_ID [TASK_ID ...], --task-id TASK_ID [TASK_ID ...]
                        Mutually exclusive with respect to --reference. For brew: Specify the TASK ID for required brew build. NOTE: Double check, that you are
                        passing TASK ID for copr builds, not BUILD ID otherwise testing farm will not install the package. For copr: Specify the BUILD ID for required
                        copr build.
  -g GIT [GIT ...], --git GIT [GIT ...]
                        Provide repository base (github, gitlab, gitlab.cee.redhat) owner of the repository and a branch containing the tests you want to run. Default:
                        '['github', 'oamg', 'main']'
  -gp GIT_PATH, --git-path GIT_PATH
                        Path to the metadata tree root. Should be relative to the git repository root provided in the url parameter. Default: '.'
  -a ARCHITECTURE, --architecture ARCHITECTURE
                        Choose suitable architecture. Default: 'x86_64'.
  -p PLANS [PLANS ...], --plans PLANS [PLANS ...]
                        Specify a test plan or multiple plans to request at testing farm. To run whole set of tiers use /plans/tier*/ Accepts multiple space separated values,
                        sends as a separate request.
  -pf PLANFILTER [PLANFILTER ...], --planfilter PLANFILTER [PLANFILTER ...]
                        Filter plans. The specified plan filter will be used in tmt plan ls --filter <YOUR-FILTER> command. By default enabled: true filter is applied.
                        Accepts multiple space separated values, sends as a separate request.
  -tf TESTFILTER [TESTFILTER ...], --testfilter TESTFILTER [TESTFILTER ...]
                        Filter tests. The specified plan filter will be used in tmt run discover plan test --filter <YOUR-FILTER> command. Accepts multiple space separated
                        values, sends as a separate request.
  -c {cos7,ol7,cos8,ol8,al86,al8,roc86,roc8} [{cos7,ol7,cos8,ol8,al86,al8,roc86,roc8} ...], --compose {cos7,ol7,cos8,ol8,al86,al8,roc86,roc8} [{cos7,ol7,cos8,ol8,al86,al8,roc86,roc8} ...]
                        Choose composes to run tests on. Default: '['cos7', 'ol7', 'cos8', 'ol8', 'al86', 'al8', 'roc86', 'roc8']'.
  -pw, --pool-workaround
                        Workarounds the AWS spot instances release.
  -w WAIT, --wait WAIT  Provide number of seconds to wait for successful response. Default: 20 seconds.
  -nw, --no-wait        Don't wait for successful response and get the artifact link ASAP.
  -l, --log             Log test links or dry run output to a file.
  --dry-run             Print out just the payload that would be sent to the testing farm. Do not actually send any request.
  --dry-run-cli         Print out https shell command with requested payload. Do not actually send any request.
  --debug               Print out additional information for each request.
```

##### Report
With the report command you are able to get the results of the requested jobs straight to the command line.<br>
It works by parsing the xunit field in the request response.<br>
Default invocation `tesar report` parses the `./report_jobs` from the tesar directory.<br>
Results can be reported back in two levels - `l1` for plan overview and `l2` for tests overview.<br>
You can chain the report command with test command and use the `-lt/--latest` and `-w/--wait` argument to get the results back whenever the requests state is complete (or error in which case the job results cannot be and won't be reported due to the non-existent xunit field).<br>
`tesar test` automatically stores the request IDs from the latest dispatched job - the primary location to store and read the data from is `/tmp/latest_tesar_jobs` file. The file is also saved with a timestamp to the working directory just for a good measure.
You can specify a different path to the file with `-f/--file` or pass the jobs to get report for straight to the commandline with `-c/--cmd`.<br>
The tool is able to parse and report for multiple variants of values as long as they are separated by a new-line (in the files) or a `-c/--cmd` argument (on the commandline). Raw request_ids, artifact URLs (Testing Farm result page URLs) or request URLs are allowed.
In case you want to get the log files stored locally, use `-d/--download-logs`. Log files for pytest runs will be stored in `/var/tmp/tesar/logs/{request_id}_log/`. In case there are multiple plans in one pipeline, the logs should get divided in their respective plan directories.

```shell
❯ tesar report --help
usage: tesar report [-h] [-l2] [--short] [-stn SPLIT_TESTNAME] [-spn SPLIT_PLANNAME] [-w] [-d] [-lt | -f FILE | -c CMD [CMD ...]]

Parses task IDs, Testing Farm artifact URLs or Testing Farm API request URLs from multiple sources.

options:
  -h, --help            show this help message and exit
  -l2, --level2         Display test view detail. By default the report shows only plan view.
  --short               Display short test and plan names.
  -stn SPLIT_TESTNAME, --split-testname SPLIT_TESTNAME
                        Specify an index from which will the test name be shown. Passed to testname.split('/')[index:]
  -spn SPLIT_PLANNAME, --split-planname SPLIT_PLANNAME
                        Specify an index from which will the plan name be shown. Passed to planname.split('/')[index:]
  -w, --wait            Wait for the job to complete. Print the table afterwards
  -d, --download-logs   Download logs for requested run(s).
  -lt, --latest         Mutually exclusive with respect to --file and --cmd. Report latest jobs from /tmp/tesar_latest_jobs.
  -f FILE, --file FILE  Mutually exclusive with respect to --latest and --cmd. Specify a different location than the default ./report_jobs of the file containing request_id's, artifact URLs or request URLs.
  -c CMD [CMD ...], --cmd CMD [CMD ...]
                        Mutually exclusive with respect to --file and --latest. Parse request_ids, artifact URLs or request URLs from the command line.
```

#### Examples

```shell
# Test copr build for PR#123 with plan basic_sanity_check on CentOS 8.4
$ tesar test copr c2r -ref pr123 -g github oamg main -p /plans/tier0/basic_sanity_checks -c cos84

# Specify which composes you want to run test plan (in this case tier0)
$ tesar test copr c2r -ref pr123 -g gitlab.cee.redhat xyz testing -p /plans/tier0 -c ol7 cos8

# Run every test plan for brew build 0.12-3 on all composes
$ tesar test brew c2r -ref 0.12-3 -g github oamg main -p /plans

# Specify more individual test plans
$ tesar test brew c2r -ref 0.12-3 -git github oamg main -p /plans/tier0/basic_sanity_checks /plans/tier1/rhsm

```

```shell
# Get results for the requests in the default file ./latest_jobs
$ tesar report

# Report the latest test run on the plan level
$ tesar report --latest

# Report from custom file on the test level
$ tesar report --level2 --file /home/username/my_jobs_file

# Pass requests' references to the commandline
$ tesar report --cmd d60ee5ab-194f-442d-9e37-933be1daf2ce https://api.endpoint/requests/9f42645f-bcaa-4c73-87e2-6e1efef16635

# Shorten the displayed test and plan names
$ tesar report --level2 --cmd 9f42645f-bcaa-4c73-87e2-6e1efef16635 /home/username/my_jobs_file --short

```

# Currently used variables

## Payload

Link to the testing farm payload documentation:<br>
https://testing-farm.gitlab.io/api/ <br>
For convert2RHEL testing we are currently using this form of payload:
> **_NOTE:_** <br> Some of the targeted instances disallow to use root login when connecting through the ssh.
> Hardcoded post_install_script is sent with each request to enable root login on the target.
```json lines
    payload = {
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
                "artifacts": [
                    {
                        "id": artifact_id,
                        "type": artifact_type,
                        "packages": [package],
                    }
                ],
                "settings": {
                    "provisioning": {
                        "post_install_script": post_install_script,
                        "tags": {"BusinessUnit": cloud_resources_tag},
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
```


## Mapped composes
We are requesting official publicly available free instances from the AWS marketplace, if possible.<br>
At this moment this applies to the Alma Linux, Oracle Linux and Rocky Linux instances.<br>
CentOS 7 latest is the last one remaining to be implemented.<br>
Sadly, there is no instance of any relevance for CentOS 8 latest available.
```
# RHEL8 targets
cos8: CentOS-8-latest
ol8: OL8.7-x86_64-HVM-2023-03-07
al86: AlmaLinux OS 8.6.20220901 x86_64
al8: AlmaLinux OS 8.8.20230524 x86_64
roc86: Rocky-8-ec2-8.6-20220515.0.x86_64
roc8: Rocky-8-EC2-Base-8.8-20230518.0.x86_64

# RHEL7 targets
cos7: CentOS-7-latest
ol7: OL7.9-x86_64-HVM-2023-01-05
```

### List globally available composes
>**__INFO:__** Mostly deprecated.<br>
> As far as convert2rhel is concerned, the majority of those images is custom-built, thus we try to use the publicly available officially maintained instances from the AWS.

Testing farm has many available composes on both public and private ranch.<br>
To list them use commands bellow.

#### Public ranch

https://api.dev.testing-farm.io/v0.1/composes

`https GET https://api.dev.testing-farm.io/v0.1/composes`

#### Private ranch

`curl -s https://gitlab.cee.redhat.com/baseos-qe/citool-config/-/raw/production/variables-composes.yaml | grep 'compose:' | tr -s ' '`
