# AskAnna CLI

The AskAnna CLI offers a command-line interface to the AskAnna platform. It
simplifies the communication with the AskAnna platform and provides facilities
for supporting every part of a data science project.

## Documentation

For the latest version check the
[AskAnna Documentation](https://docs.askanna.io/#/cli).

## Quickstart

### Install AskAnna

```
pip install askanna
```

### Login to askanna

```
askanna login
```

This will create a `.askanna.yml` in your home folder.

When used in a CI, one can configure authentication by setting an environment
variable:

```bash
export AA_REMOTE=https://beta-api.askanna.eu/v1/
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

## Running Tests

Does the code actually work?

```bash
source <YOURVIRTUALENV>/bin/activate
(myenv) $ pip install tox
(myenv) $ tox
```

## Make a new release

We use `bumpversion` to bump the version number of a release:

```bash
# upgrade version by 0.0.x
bumpversion patch

# upgrade version by 0.x.0
bumpversion minor

# upgrade version by x.0.0
bumpversion major
```

## Credits

Tools used in the AskAnna package:

* Cookiecutter: https://github.com/audreyr/cookiecutter
* `cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
