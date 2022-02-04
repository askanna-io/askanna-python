# AskAnna CLI & Python SDK

The AskAnna CLI offers a command-line interface to the AskAnna platform. With the Python SDK
you can run AskAnna functions directly from your Python script. The CLI & Python SDK
simplifies the communication with the AskAnna platform and provides facilities
for supporting every part of a data science project.

[![PyPi](https://img.shields.io/pypi/v/askanna.svg)](https://pypi.org/project/askanna/)
[![License](https://img.shields.io/badge/license-Apache%202-brightgreen.svg)](https://gitlab.askanna.io/askanna/askanna-cli/-/blob/release/0.6.2/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-success.svg)](https://docs.askanna.io/)
[![Downloads](https://pepy.tech/badge/askanna)](https://pepy.tech/project/askanna)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Documentation

For the latest version check the
[AskAnna Documentation](https://docs.askanna.io/). Or open directly the documentation for:

* [Command-line (CLI)](https://docs.askanna.io/cli/)
* [Python SDK](https://docs.askanna.io/python-sdk/)

## Quickstart

### Install AskAnna

```bash
pip install askanna
```

## Update AskAnna

```bash
pip install -U askanna
```

### Login to AskAnna

```bash
askanna login
```

This will create a `.askanna.yml` in your home folder.

When used in a CI, one can configure authentication by setting an environment
variable:

```bash
export AA_REMOTE=https://beta-api.askanna.eu
export AA_TOKEN={{ API TOKEN }}
```

The API token can be found in the created `.askanna.yml` file or in the
curl information on a job run page in the AskAnna platform.

### How to push your code to AskAnna

First add a `askanna.yml` file to the main directory of your project. In
AskAnna create a project, copy the push-target and add it to the `askanna.yml`
file.

Next run `askanna push` and your code will be uploaded to the project in
AskAnna.

You can also push code from a CI environment. This requires the following
environment variables to be set:

```bash
export AA_TOKEN={{ API TOKEN }}
```

## Credits

Tools used in the AskAnna package:

* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
