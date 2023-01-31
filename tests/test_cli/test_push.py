import pytest
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config


@pytest.mark.usefixtures("api_response")
class TestCliPush:
    """
    askanna push

    We expect to initiate a push action of our code to the AskAnna server
    """

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

    def test_command_push_project_not_exist(self):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "7890-7890-7890-7890"
        result = CliRunner().invoke(cli, "push", input="N")

        assert result.exception
        assert "We cannot find your project on AskAnna." in result.output

    def test_command_push_without_force_no_replace(self):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli, "push", input="N")

        assert not result.exception
        assert "You choose to not replace your existing code." in result.output

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
