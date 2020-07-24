# askanna-cli


askanna-cli offers a CLI interface for creating AskAnna and supported DSP
projects. It simplifies the communication with the AskAnna platform and
provides facilities for supporting every part of the data science process.

## Documentation

## Quickstart

### Install askanna-cli::

```
pip install askanna
```

### Login to askanna:

```
askanna login
```

This will create a `.askanna.yml` in your home folder.

When used in a CI, one can configure authentication by setting an environment variable:

```bash
export AA_REMOTE=https://beta-api.askanna.eu/v1/
export AA_TOKEN=<your api token, can be found in ~/.askanna.yml>
```

Upload your package to AskAnna:
First setup your `askanna.yml`:
```yml
push-target: https://beta.askanna.eu/project/7MQT-6309-9g3t-R5QR/
```
Values on the URL and `project-uuid` needs to be configured for your own project.

Uploading a package from a CI environment requires the following variables to be set:

```bash
export AA_TOKEN=<your api token>
```

## Features

## Running Tests

Does the code actually work?
```bash
source <YOURVIRTUALENV>/bin/activate
(myenv) $ pip install tox
(myenv) $ tox
```

   
## Credits

Tools used in rendering this package:

* Cookiecutter: https://github.com/audreyr/cookiecutter
* `cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
