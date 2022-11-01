import os

import pytest
from click.testing import CliRunner

from askanna.cli import cli


@pytest.mark.usefixtures("reset_environment_and_work_dir", "api_response")
class TestCliInit:
    """
    Test 'askanna init' to initiate a project init action in the current directory
    """

    def test_command_help(self):
        result = CliRunner().invoke(cli, "--help")
        assert not result.exception
        assert "init" in result.output

    def test_command_init_help(self):
        result = CliRunner().invoke(cli, "init --help")
        assert not result.exception
        assert "init [OPTIONS]" in result.output

    def test_command_init_base(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "init new-project --workspace 5678-5678-5678-5678")
        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

    def test_command_init_ask_info(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "init", input="new-project\n\n")
        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

    def test_command_init_duplicate(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "init new-project --workspace 5678-5678-5678-5678")

        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

        result = CliRunner().invoke(cli, "init new-project --workspace 5678-5678-5678-5678", input="y")

        assert not result.exception
        assert "This directory already has an 'askanna.yml' file." in result.output

    def test_command_init_duplicate_abort(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "init new-project --workspace 5678-5678-5678-5678")

        assert not result.exception
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

        result = CliRunner().invoke(cli, "init new-project --workspace 5678-5678-5678-5678", input="n")

        assert result.exit_code == 1
        assert "Aborted!" in result.output
