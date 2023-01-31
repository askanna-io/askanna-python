import os

import pytest
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config


@pytest.mark.usefixtures("reset_environment_and_work_dir", "api_response")
class TestCliCreate:
    """
    Test 'askanna create' to create a new project in a new directory and optionally push it to AskAnna
    """

    def test_command_help(self):
        result = CliRunner().invoke(cli, "--help")
        assert not result.exception
        assert "create" in result.output

    def test_command_create_help(self):
        result = CliRunner().invoke(cli, "create --help")
        assert not result.exception
        assert "create [OPTIONS]" in result.output

    def test_command_create_base(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "create new-project --workspace 5678-5678-5678-5678")
        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output
        assert "Success with your project!" in result.output
        assert config.server.ui in result.output

    def test_command_create_error(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "create 'project with error' --workspace 1234-1234-1234-1234")
        assert result.exception
        assert "You successfully created project" not in result.output
        assert "Something went wrong while creating the project" in result.output

    def test_command_create_ask_info(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "create", input="new-project\n\n")
        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output
        assert "Success with your project!" in result.output

    def test_command_create_project_exist(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "init new-project --workspace 5678-5678-5678-5678")

        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

        result = CliRunner().invoke(cli, "create new-project --workspace 5678-5678-5678-5678")

        assert result.exit_code == 1
        assert "This directory already has an 'askanna.yml' file" in result.output
        assert "Success with your project!" not in result.output

    def test_command_create_project_duplicate(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "create new-project --workspace 5678-5678-5678-5678")

        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

        result = CliRunner().invoke(cli, "create new-project --workspace 5678-5678-5678-5678")

        assert result.exit_code == 1
        assert "You already have a project directory" in result.output
        assert "Success with your project!" in result.output

    def test_command_create_with_push(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "create new-project --workspace 5678-5678-5678-5678 --push")

        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output
        assert "Successfully pushed the project to AskAnna!" in result.output

    def test_command_create_no_ui_config(self, temp_dir):
        ui_config = config.server.ui
        config.server.ui = ""

        os.chdir(temp_dir)

        result = CliRunner().invoke(cli, "create new-project --workspace 5678-5678-5678-5678")

        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output
        assert ui_config not in result.output

        config.server.ui = ui_config
