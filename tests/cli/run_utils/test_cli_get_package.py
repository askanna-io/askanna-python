import os
import shutil
import tempfile
import unittest

import pytest
import responses
from click.testing import CliRunner

from askanna.cli.run_utils.tool import cli_commands
from askanna.core.apiclient import client
from tests.create_fake_files import create_zip_file


@pytest.fixture(autouse=True)
def test_setup_and_teardown(monkeypatch):
    cwd = os.getcwd()
    environ_bck = dict(os.environ)

    yield

    os.chdir(cwd)
    os.environ.clear()
    os.environ.update(environ_bck)


class TestCliGetPackage(unittest.TestCase):
    """
    askanna-run-utils get-package

    We expect to initiate a push action of our code to the AskAnna server
    """

    verb = "get-package"

    def setUp(self):
        api_server = client.base_url
        url_package_zip = "https://cdn/files/packages/test.zip"

        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-get-package")
        self.package_zip_file = create_zip_file(self.tempdir, 10)

        with open(self.package_zip_file, "rb") as f:
            content = f.read()

        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.GET,
            url=f"{api_server}project/abcd-abcd-abcd-abcd/packages/1234-1234-1234-1234/download/",
            status=200,
            content_type="application/json",
            json={
                "action": "redirect",
                "target": url_package_zip,
            },
        )
        self.responses.add(
            responses.GET,
            url=f"{api_server}project/abcd-abcd-abcd-abcd/packages/wxyz-wxyz-wxyz-wxyz/download/",
            status=404,
            body="{'detail': 'Not found.'}",
        )
        self.responses.add(
            responses.GET,
            url=url_package_zip,
            headers={"Range": f"bytes=0-{os.path.getsize(self.package_zip_file)}"},
            stream=True,
            content_type="application/zip",
            status=206,
            body=content,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.remove(self.package_zip_file)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_command_get_package_help(self):
        result = CliRunner().invoke(cli_commands, [self.verb, "--help"])

        self.assertIn("get-package", result.output)
        self.assertNotIn("noop", result.output)

    def test_command_get_package_no_project_suuid(self):
        result = CliRunner().invoke(cli_commands, self.verb)

        self.assertTrue(result.exit_code)
        self.assertIn("No AA_PROJECT_SUUID found.", result.output)
        self.assertNotIn("noop", result.output)

    def test_command_get_package_no_package_suuid(self):
        os.environ["AA_PROJECT_SUUID"] = "abcd-abcd-abcd-abcd"

        result = CliRunner().invoke(cli_commands, self.verb)

        self.assertTrue(result.exit_code)
        self.assertIn("No AA_PACKAGE_SUUID found.", result.output)
        self.assertNotIn("noop", result.output)

    def test_command_get_package_successs(self):
        os.environ["AA_PROJECT_SUUID"] = "abcd-abcd-abcd-abcd"
        os.environ["AA_PACKAGE_SUUID"] = "1234-1234-1234-1234"
        os.environ["AA_CODE_DIR"] = self.tempdir + "/code"
        output_zip_file = f"{tempfile.gettempdir()}/askanna/code.zip"

        result = CliRunner().invoke(cli_commands, self.verb)

        self.assertFalse(result.exit_code)
        self.assertEqual(os.path.getsize(self.package_zip_file), os.path.getsize(output_zip_file))
        os.remove(output_zip_file)

    def test_command_get_package_not_exist(self):
        os.environ["AA_PROJECT_SUUID"] = "abcd-abcd-abcd-abcd"
        os.environ["AA_PACKAGE_SUUID"] = "wxyz-wxyz-wxyz-wxyz"

        result = CliRunner().invoke(cli_commands, self.verb)

        self.assertTrue(result.exit_code)
        self.assertIn("This package does not exist.", result.output)
