# AskAnna CLI & Python SDK

The AskAnna CLI offers a command line interface to the AskAnna platform. With the Python SDK you can run AskAnna
functions directly from your Python script. The CLI & Python SDK simplifies the communication with the AskAnna
platform and provides facilities for supporting every part of a data science project.

[![PyPI](https://img.shields.io/pypi/v/askanna.svg?color=%2334D058)](https://pypi.org/project/askanna/)
[![Python](https://img.shields.io/pypi/pyversions/askanna.svg?color=%2334D058)](https://pypi.org/project/askanna/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-brightgreen.svg?label=license)](https://gitlab.com/askanna/askanna-python/-/blob/master/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-available-success.svg)](https://docs.askanna.io/)

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

### Update AskAnna

```bash
pip install -U askanna
```

### Login to AskAnna

```bash
askanna login
```

This will create a `.askanna.yml` in your home directory.

### Authorization token

When the AskAnna CLI & Python SDK is used in for example a CI/CD, one can configure authentication by setting an
environment variable:

```bash
export AA_REMOTE=https://beta-api.askanna.eu
export AA_TOKEN={{ API TOKEN }}
```

The API token can be found in the created `~/.askanna.yml` file after you logged in with `askanna login`.

### How to push code to AskAnna

Run the innit-command on the main directory of your project. The command will create a new project on AskAnna and will
add a `askanna.yml` file to your local project directory. In the `askanna.yml` file you can configure jobs. For more
information, see the [askanna.yml documentation](https://docs.askanna.io/code/#askannayml).

```bash
askanna init
```

If you want to start a project from scratch (or a template), you can run the create-command.

```bash
askanna create
```

With the push-command your code will be uploaded to the project in AskAnna.

```bash
askanna push
```

### Track metrics

To track metrics for your runs, you can use the function `track_metric`. For more information, see the
[metrics documentation](https://docs.askanna.io/metrics/).

```python
from askanna import track_metric

track_metric("name", "value")
```

### Track variables

To track variables for your runs, you can use the function `track_variable`. For more information, see the
[variables documentation](https://docs.askanna.io/variable/tracking/).

```python
from askanna import track_variable

track_variable("name", "value")
```
