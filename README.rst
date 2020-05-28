===========
askanna-cli
===========

askanna-cli offers a CLI interface for creating AskAnna and supported DSP
projects. It simplifies the communication with the AskAnna platform and
provides facilities for supporting every part of the data science process.

Documentation
-------------

Placeholder information on how to use the documentation.

Add locations, see the different formats and consider the CI required for
building the default documentation set.

Quickstart
----------

Install askanna-cli::

   pip install git+https://gitlab.askanna.io/open/askanna-cli.git#egg=askanna-cli

Login to askanna:

   askanna login

When used in a CI, one can configure authentication by setting an environment variable:

   AA_REMOTE=https://beta-api.askanna.eu/v1/
   AA_TOKEN=<your api token>

Upload your package to AskAnna:
First setup your `askanna.yml`:

   project:
      url: "https://beta.askanna.eu/workspace/project/7MQT-6309-9g3t-R5QR/"
      name: "AskAnna Sandbox"
      uuid: "f1e2144a-87f9-4936-8562-4304c51332ea"

Values on the URL and `uuid` needs to be configured for your own project.

Uploading a package from a CI environment requires the following variables to be set:


   AA_REMOTE=https://beta-api.askanna.eu/v1/
   AA_TOKEN=<your api token>
   PROJECT_UUID=<uuid for your project>



Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

   source <YOURVIRTUALENV>/bin/activate
   (myenv) $ pip install tox
   (myenv) $ tox

   
Credits
-------

Tools used in rendering this package:

* Cookiecutter_
* `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
