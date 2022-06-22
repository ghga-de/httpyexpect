![tests](https://github.com/ghga-de/httpyexpect/actions/workflows/unit_and_int_tests.yaml/badge.svg)
[![PyPI version shields.io](https://img.shields.io/pypi/v/httpyexpect.svg)](https://pypi.python.org/pypi/httpyexpect/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/httpyexpect.svg)](https://pypi.python.org/pypi/httpyexpect/)
[![Coverage Status](https://coveralls.io/repos/github/ghga-de/httpyexpect/badge.svg?branch=main)](https://coveralls.io/github/ghga-de/httpyexpect?branch=main)

# httpyexpect
An opinionated way to translate server side HTTP errors to the client side.

## Installation
This package is available at PyPI:
https://pypi.org/project/httpyexpect

You can install it from there using:
```
pip install httpyexpect
```

If you want to use the server-oriented utilities of the package, please
install the following extra: `server`.

## Client-Server Contract
Httpyexcept proposes a client-server contract on how to communicate exceptions.
All error responses coming from the server (i.e. all responses with a 4xx or a 5xx
status code) should have a body that complies with the following schema:
[](./json_schemas/http_exception.json)

## Usage

A detailed documentation is coming soon, until then please have a look at the
integration tests as a usage example.

[test_fastapi.py](./tests/integration/test_fastapi.py) demonstrates the server side
usage with FastAPI.

[test_client.py](./tests/integration/test_client.py) demonstrates how to translate an
HTTP error into a Python exception on the client side.
## Development
For setting up the development environment, we rely on the
[devcontainer feature](https://code.visualstudio.com/docs/remote/containers) of vscode.

To use it, you have to have Docker as well as vscode with its "Remote - Containers" extension (`ms-vscode-remote.remote-containers`) extension installed.
Then, you just have to open this repo in vscode and run the command
`Remote-Containers: Reopen in Container` from the vscode "Command Palette".

This will give you a full-fledged, pre-configured development environment including:
- infrastructural dependencies of the service (databases, etc.)
- all relevant vscode extensions pre-installed
- pre-configured linting and auto-formating
- a pre-configured debugger
- automatic license-header insertion

Moreover, inside the devcontainer, there is follwing convenience command available
(please type it in the integrated terminal of vscode):
- `dev_install` - install the lib with all development dependencies and pre-commit hooks
(please run that if you are starting the devcontainer for the first time
or if added any python dependencies to the [`./setup.cfg`](./setup.cfg))

If you prefer not to use vscode, you could get a similar setup (without the editor specific features)
by running the following commands:
``` bash
# Execute in the repo's root dir:
cd ./.devcontainer

# build and run the environment with docker-compose
docker build -t httpyexpect .
docker run -it httpyexpect /bin/bash

```

## License
This repository is free to use and modify according to the [Apache 2.0 License](./LICENSE).
