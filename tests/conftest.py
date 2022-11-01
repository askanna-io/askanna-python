import os
import shutil

import pytest

pytest_plugins = [
    "tests.fixtures.responses.api",
    "tests.fixtures.responses.job",
    "tests.fixtures.responses.package",
    "tests.fixtures.responses.project",
    "tests.fixtures.responses.run",
    "tests.fixtures.responses.workspace",
]


@pytest.fixture()
def temp_dir(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("askanna-test-")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def reset_environment_and_work_dir():
    cwd = os.getcwd()
    environ_bck = dict(os.environ)

    yield

    os.chdir(cwd)
    os.environ.clear()
    os.environ.update(environ_bck)
