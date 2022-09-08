import os
import shutil
import tempfile
import unittest

import responses
from click.testing import CliRunner

from askanna.cli.tool import cli_commands
from askanna.config import config
from askanna.core.apiclient import client


class TestCliPush(unittest.TestCase):
    """
    askanna init

    We expect to initiate a project init action
    """

    def setUp(self):
        self.bck_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-create")
        os.chdir(self.tempdir)

        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.POST,
            url=client.base_url + "project/",
            status=201,
            json={
                "uuid": "798a599f-48e8-4aff-823a-f21d0b0f95ff",
                "short_uuid": "3hLI-SToG-4WQo-j7xS",
                "name": "Testing",
                "description": None,
                "workspace": {
                    "relation": "workspace",
                    "name": "Review Private",
                    "uuid": "f95ff93c-1f80-4216-8464-5b7ba59f4b64",
                    "short_uuid": "7aYw-rkCA-wdMo-1Gi6",
                },
                "package": {"uuid": None, "short_uuid": None, "name": None},
                "notifications": {},
                "permission": {},
                "is_member": True,
                "created_by": {
                    "uuid": "726f6262-6572-7440-6173-6b616e6e6121",
                    "short_uuid": "3Tw1-jp9H-FjQw-8PYY",
                    "name": "robbert@askanna.io",
                },
                "visibility": "PRIVATE",
                "created": "2022-08-30T16:16:46.911121Z",
                "modified": "2022-08-30T16:16:46.911150Z",
                "url": config.server.ui + "/7aYw-rkCA-wdMo-1Gi6/project/3hLI-SToG-4WQo-j7xS",
            },
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.chdir(self.bck_cwd)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_command_init_help(self):
        result = CliRunner().invoke(cli_commands, "init --help")

        self.assertIn("init", result.output)
        self.assertNotIn("noop", result.output)

    def test_command_init_base(self):
        result = CliRunner().invoke(cli_commands, "init test --workspace 1234-1234-1234-1234")

        assert not result.exception
        assert "You have successfully created a new project in AskAnna!" in result.output
