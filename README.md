## Edit payload to the testing farm API in a bit more convenient way

Link to the testing farm payload documentation:

https://testing-farm.gitlab.io/api/

<br>**This is WIP**

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

