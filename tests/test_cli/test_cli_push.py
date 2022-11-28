import unittest

import responses
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config
from askanna.config.api_url import askanna_url


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
            url=askanna_url.base_url + "project/1234-1234-1234-1234/package/",
            status=200,
            json={
                "count": 9,
                "next": askanna_url.base_url + "project/1234-1234-1234-1234/package/?limit=1&offset=1",
                "previous": None,
                "results": [
                    {
                        "suuid": "6a1T-iH8R-4tkl-B2pp",
                        "workspace": {
                            "relation": "workspace",
                            "suuid": "1234-1234-1234-1234",
                            "name": "a workspace",
                        },
                        "project": {
                            "relation": "project",
                            "suuid": "1234-1234-1234-1234",
                            "name": "001 Simple",
                        },
                        "created_by": {
                            "relation": "membership",
                            "suuid": "1KLU-TJMX-zx1y-EofD",
                            "name": "test@test.com",
                            "job_title": "",
                            "role": {
                                "code": "WA",
                                "name": "Workspace Admin",
                            },
                            "status": "accepted",
                        },
                        "created": "2022-08-30T13:15:14.343891Z",
                        "modified": "2022-08-30T13:15:14.343936Z",
                        "name": None,
                        "description": "Initial push",
                        "filename": "001-simple_5ce008c6caef40289cd541dc1d81408b.zip",
                        "size": 1212,
                    }
                ],
            },
        )
        self.responses.add(
            responses.POST,
            url=askanna_url.base_url + "package/",
            status=201,
            json={"suuid": "abcd-abcd-abcd-abcd"},
        )
        self.responses.add(
            responses.POST,
            url=askanna_url.base_url + "package/abcd-abcd-abcd-abcd/packagechunk/",
            status=201,
            json={"uuid": "d83b6138-a9a9-44a6-b286-cc55e34abf56"},
        )
        self.responses.add(
            responses.POST,
            url=askanna_url.base_url
            + "package/abcd-abcd-abcd-abcd/packagechunk/d83b6138-a9a9-44a6-b286-cc55e34abf56/chunk/",
            status=200,
        )
        self.responses.add(
            responses.POST,
            url=askanna_url.base_url + "package/abcd-abcd-abcd-abcd/finish_upload/",
            status=200,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

    def test_command_push_base(self):
        result = CliRunner().invoke(cli, "push --help")

        assert not result.exception
        assert "push" in result.output
        assert "noop" not in result.output

    def test_command_push_missing_config_path(self):
        config.project.project_config_path = ""
        result = CliRunner().invoke(cli, "push")

        assert result.exception
        assert "We cannot upload without a project config path." in result.output

    def test_command_push_description_and_message(self):
        result = CliRunner().invoke(cli, "push --description test --message test")

        assert result.exception
        assert "Cannot use both --description and --message." in result.output

    def test_command_push_missing_project_suuid(self):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = ""
        result = CliRunner().invoke(cli, "push")

        assert result.exception
        assert "We cannot upload to AskAnna without the project SUUID set." in result.output

    def test_command_push_without_force_no_replace(self):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli, "push", input="N")

        assert not result.exception
        assert "You choose not to replace your existing code." in result.output

    def test_command_push_without_force_replace_code(self):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli, "push", input="y")

        assert not result.exception
        assert "Uploading" in result.output

    def test_command_push_with_force(self):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli, "push --force")

        assert not result.exception
        assert "Uploading" in result.output
