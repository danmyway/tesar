Send requests to the Testing farm API through cli
===============================================

## Edit the payload to the testing farm API through the command line

Link to the testing farm payload documentation:

https://testing-farm.gitlab.io/api/

** This is WIP **
========
## Prerequisites

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
>$ dnf install brew-koji<br>
>$ dnf install python-copr, python-copr-docs

### Run 

`git clone https://gitlab.cee.redhat.com/ddiblik/tf_api_req.git`

Edit the .env file as needed.

Run `python tf-api-req.py`

### List available composes

#### Public ranch

https://api.dev.testing-farm.io/v0.1/composes

`https GET https://api.dev.testing-farm.io/v0.1/composes`

#### Private ranch

`curl -s https://gitlab.cee.redhat.com/baseos-qe/citool-config/-/raw/production/variables.yaml | grep 'symbolic_compose' | sed 's/.*symbolic_compose: //' | sort`

