import unittest

import responses
from click.testing import CliRunner

from askanna.cli.tool import cli_commands
from askanna.config import config
from askanna.core.apiclient import client


class TestCliPush(unittest.TestCase):
    """
    askanna push

    We expect to initiate a push action of our code to the AskAnna server
    """

    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.GET,
            url=client.base_url + "project/1234-1234-1234-1234/packages/",
            status=200,
            json={
                "count": 9,
                "next": client.base_url + "project/1234-1234-1234-1234/packages/?limit=1&offset=1",
                "previous": None,
                "results": [
                    {
                        "uuid": "d83b6138-a9a9-44a6-b286-cc55e34abf56",
                        "created_by": {
                            "relation": "membership",
                            "name": "test@test.com",
                            "uuid": "2ba3b8fc-2045-4f1f-9687-878119a59214",
                            "short_uuid": "1KLU-TJMX-zx1y-EofD",
                        },
                        "project": {
                            "name": "001 Simple",
                            "uuid": "020720b2-9f39-4cfa-97cc-e417453eeae9",
                            "short_uuid": "1234-1234-1234-1234",
                        },
                        "filename": "001-simple_5ce008c6caef40289cd541dc1d81408b.zip",
                        "created": "2022-08-30T13:15:14.343891Z",
                        "modified": "2022-08-30T13:15:14.343936Z",
                        "deleted": None,
                        "description": "Initial push",
                        "name": None,
                        "short_uuid": "6a1T-iH8R-4tkl-B2pp",
                        "original_filename": "001-simple_5ce008c6caef40289cd541dc1d81408b.zip",
                        "size": 1212,
                        "finished": "2022-08-30T13:15:14.497068Z",
                        "member": "2ba3b8fc-2045-4f1f-9687-878119a59214",
                    }
                ],
            },
        )
        self.responses.add(
            responses.POST,
            url=client.base_url + "package/",
            status=201,
            json={"short_uuid": "abcd-abcd-abcd-abcd"},
        )
        self.responses.add(
            responses.POST,
            url=client.base_url + "package/abcd-abcd-abcd-abcd/packagechunk/",
            # status=200,
            json={"uuid": "d83b6138-a9a9-44a6-b286-cc55e34abf56"},
        )
        self.responses.add(
            responses.POST,
            url=client.base_url
            + "package/abcd-abcd-abcd-abcd/packagechunk/d83b6138-a9a9-44a6-b286-cc55e34abf56/chunk/",
            status=200,
        )
        self.responses.add(
            responses.POST,
            url=client.base_url + "package/abcd-abcd-abcd-abcd/finish_upload/",
            status=200,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

    def test_command_push_base(self):
        result = CliRunner().invoke(cli_commands, "push --help")

        assert not result.exception
        assert "push" in result.output
        assert "noop" not in result.output

    def test_command_push_missing_config_path(self):
        config.project.project_config_path = ""
        result = CliRunner().invoke(cli_commands, "push")

        assert result.exception
        assert "We cannot upload without a project config path." in result.output

    def test_command_push_description_and_message(self):
        result = CliRunner().invoke(cli_commands, "push --description test --message test")

        assert result.exception
        assert "Cannot use both --description and --message." in result.output

    def test_command_push_missing_project_suuid(self):
        config.project.project_config_path = "tests/resources/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = ""
        result = CliRunner().invoke(cli_commands, "push")

        assert result.exception
        assert "We cannot upload to AskAnna without the project SUUID set." in result.output

    def test_command_push_without_force_no_replace(self):
        config.project.project_config_path = "tests/resources/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli_commands, "push", input="N")

        assert not result.exception
        assert "You choose not to replace your existing code." in result.output

    def test_command_push_without_force_replace_code(self):
        config.project.project_config_path = "tests/resources/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli_commands, "push", input="y")

        assert not result.exception
        assert "Uploading" in result.output

    def test_command_push_with_force(self):
        config.project.project_config_path = "tests/resources/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli_commands, "push --force")

        assert not result.exception
        assert "Uploading" in result.output
