# AskAnna CLI & Python SDK

The AskAnna CLI offers a command-line interface to the AskAnna platform. With the Python SDK you can run AskAnna
functions directly from your Python script. The CLI & Python SDK simplifies the communication with the AskAnna
platform and provides facilities for supporting every part of a data science project.

[![PyPi](https://img.shields.io/pypi/v/askanna.svg)](https://pypi.org/project/askanna/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-brightgreen.svg)](https://gitlab.com/askanna/askanna-python/-/blob/master/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-success.svg)](https://docs.askanna.io/)
[![Downloads](https://pepy.tech/badge/askanna)](https://pepy.tech/project/askanna)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Documentation

For the latest information check the [AskAnna Documentation](https://docs.askanna.io/). Or open directly the
documentation for:

* [Command line (CLI)](https://docs.askanna.io/cli/)
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


### Authorization token

When the AskAnna CLI & Python SDK is used in for example a CI/CD, one can configure authentication by setting an
environment variable:

```bash
export AA_REMOTE=https://beta-api.askanna.eu
export AA_TOKEN={{ API TOKEN }}
```

The API token can be found in the created `~/.askanna.yml` file after you logged in with `askanna login`.

### How to push code to AskAnna

```bash
askanna init
```

Run this command on the main directory of your project. The command will create a new project on AskAnna and will
add a `askanna.yml` file to your local project directory.

```bash
askanna create
```

If you want to start a project from scratch (or a template), you can run this command.

```bash
askanna push
```

Run `askanna push` and your code will be uploaded to the project in AskAnna.

## Credits

Tools used in the AskAnna package:

* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
