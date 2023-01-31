import pytest
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config


class TestCliVariableMain:
    """
    Test 'askanna variable' main command
    """

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, "--help")
        assert result.exit_code == 0
        assert "variable" in result.output

    def test_command_variable_help(self):
        result = CliRunner().invoke(cli, ["variable", "--help"])
        assert result.exit_code == 0
        assert "variable [OPTIONS]" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliVariableList:
    """
    Test 'askanna variable list' where we expect to get a list of variables
    """

    def test_command_variable_list_help(self):
        result = CliRunner().invoke(cli, "variable list --help")
        assert result.exit_code == 0
        assert "variable list [OPTIONS]" in result.output

    def test_command_variable_list(self):
        result = CliRunner().invoke(cli, "variable list")
        assert result.exit_code == 0
        assert "VARIABLE SUUID" in result.output
        assert "1234-1234-1234-1234" in result.output
        assert "SUUID: 1234-1234-1234-1234" not in result.output


@pytest.mark.usefixtures("api_response")
class TestCliWVariableInfo:
    """
    Test 'askanna variable info' where we expect to get a info of a variable
    """

    def test_command_variable_info_help(self):
        result = CliRunner().invoke(cli, "variable info --help")
        assert result.exit_code == 0
        assert "variable info [OPTIONS]" in result.output

    def test_command_variable_info(self):
        result = CliRunner().invoke(cli, "variable info --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "SUUID:           1234-1234-1234-1234" in result.output
        assert "Created:         2020-04-01 09:44:11 UTC" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliVariableChange:
    """
    Test 'askanna variable change' where we test changing variable data
    """

    def test_command_variable_change_help(self):
        result = CliRunner().invoke(cli, "variable change --help")
        assert result.exit_code == 0
        assert "variable change [OPTIONS]" in result.output

    def test_command_variable_change(self):
        result = CliRunner().invoke(cli, ["variable", "change", "--id", "1234-1234-1234-1234", "--name", "new name"])
        assert result.exit_code == 0
        assert "You succesfully changed variable 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_workspace_change_no_input(self):
        result = CliRunner().invoke(
            cli, ["variable", "change", "--id", "1234-1234-1234-1234"], input="y\nnew name\nn\ny"
        )
        assert result.exit_code == 0
        assert "You succesfully changed variable 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_variable_change_not_found(self):
        result = CliRunner().invoke(cli, ["variable", "change", "--id", "7890-7890-7890-7890", "--value", "new value"])
        assert result.exit_code == 1
        assert "The variable SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_variable_change_error(self):
        result = CliRunner().invoke(cli, ["variable", "change", "--id", "0987-0987-0987-0987", "--name", "new name"])
        assert result.exit_code == 1
        assert "Something went wrong while getting the variable info:" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliVariableAdd:
    """
    Test 'askanna variable add' where we test adding a variable
    """

    def test_command_variable_add_help(self):
        result = CliRunner().invoke(cli, "variable add --help")
        assert result.exit_code == 0
        assert "variable add [OPTIONS]" in result.output

    def test_command_variable_add(self):
        result = CliRunner().invoke(
            cli,
            [
                "variable",
                "add",
                "--name",
                "a new variable",
                "--value",
                "new variable value",
            ],
            input="y\ny\n",
        )
        assert result.exit_code == 0
        assert (
            "You succesfully created variable 'a new variable' with SUUID '4321-4321-4321-4321' in project 'a project'"
            in result.output
        )

    def test_command_variable_add_choose_project(self):
        result = CliRunner().invoke(
            cli,
            [
                "variable",
                "add",
                "--name",
                "a new variable",
                "--value",
                "new variable value",
            ],
            input="n\ny\n",
        )
        assert result.exit_code == 0
        assert (
            "You succesfully created variable 'a new variable' with SUUID '4321-4321-4321-4321' in project 'a project'"
            in result.output
        )

    def test_command_variable_add_error(self):
        config.project.project_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli, ["variable", "add"], input="y\nvariable with error\nvalue\ny\ny\n")
        assert result.exit_code == 1
        assert "Something went wrong while creating the variable" in result.output
        assert "{'error': 'Internal Server Error'}" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliVariableRemove:
    """
    Test 'askanna variable remove' where we test removing a variable
    """

    def test_command_variable_remove_help(self):
        result = CliRunner().invoke(cli, "variable remove --help")
        assert result.exit_code == 0
        assert "variable remove [OPTIONS]" in result.output

    def test_command_variable_remove(self):
        result = CliRunner().invoke(cli, ["variable", "remove", "--id", "1234-1234-1234-1234", "--force"])
        assert result.exit_code == 0
        assert "You removed variable SUUID '1234-1234-1234-1234'" in result.output

    def test_command_variable_remove_confirm(self):
        result = CliRunner().invoke(cli, ["variable", "remove", "--id", "1234-1234-1234-1234"], input="y")
        assert result.exit_code == 0
        assert "You removed variable SUUID '1234-1234-1234-1234'" in result.output

    def test_command_variable_remove_abort(self):
        result = CliRunner().invoke(cli, ["variable", "remove", "--id", "1234-1234-1234-1234"], input="n")
        assert result.exit_code == 0
        assert "Understood. We are not removing the variable." in result.output

    def test_command_variable_remove_not_found(self):
        result = CliRunner().invoke(cli, ["variable", "remove", "--id", "7890-7890-7890-7890", "--force"])
        assert result.exit_code == 1
        assert "The variable SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_variable_remove_error(self):
        result = CliRunner().invoke(cli, ["variable", "remove", "--id", "0987-0987-0987-0987", "--force"])
        assert result.exit_code == 1
        assert "Something went wrong while getting the info of variable SUUID '0987-0987-0987-0987'" in result.output
