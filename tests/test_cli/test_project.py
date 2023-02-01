import pytest
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config


class TestCliProjectMain:
    """
    Test 'askanna project' main command
    """

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, "--help")
        assert result.exit_code == 0
        assert "project" in result.output

    def test_command_project_help(self):
        result = CliRunner().invoke(cli, "project --help")
        assert result.exit_code == 0
        assert "project [OPTIONS]" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliProjectList:
    """
    Test 'askanna project list' where we expect to get a list of projects
    """

    def test_command_project_list_help(self):
        result = CliRunner().invoke(cli, "project list --help")
        assert result.exit_code == 0
        assert "project list [OPTIONS]" in result.output

    def test_command_project_list(self):
        result = CliRunner().invoke(cli, "project list")
        assert result.exit_code == 0
        assert "WORKSPACE SUUID" in result.output
        assert "PROJECT SUUID" in result.output
        assert "1234-1234-1234-1234" in result.output
        assert "SUUID: 1234-1234-1234-1234" not in result.output

    def test_command_project_list_error(self):
        result = CliRunner().invoke(cli, "project list -w 7890-7890-7890-7890")
        assert result.exit_code == 1
        assert "Something went wrong while listing the projects" in result.output

    def test_command_project_list_workspace(self):
        result = CliRunner().invoke(cli, "project list -w 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "The projects for workspace" in result.output
        assert "WORKSPACE SUUID" not in result.output
        assert "PROJECT SUUID" in result.output
        assert "1234-1234-1234-1234" in result.output
        assert "SUUID: 1234-1234-1234-1234" not in result.output

    def test_command_project_list_empty(self):
        result = CliRunner().invoke(cli, "project list -w 5678-5678-5678-5678")
        assert result.exit_code == 0
        assert "We cannot find any project." in result.output

    def test_command_project_list_with_note(self):
        result = CliRunner().invoke(cli, "project list -w 3456-3456-3456-3456")
        assert result.exit_code == 0
        print(result.output)
        assert "Note: the first 1 of 1,000 projects are shown" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliProjectInfo:
    """
    Test 'askanna project info' where we expect to get a info of a project
    """

    def test_command_project_info_help(self):
        result = CliRunner().invoke(cli, "project info --help")
        assert result.exit_code == 0
        assert "project info [OPTIONS]" in result.output

    def test_command_project_info(self):
        result = CliRunner().invoke(cli, "project info --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "SUUID:       1234-1234-1234-1234" in result.output
        assert "Created:  2021-06-29 08:16:05.554963+00:00" in result.output

    def test_command_project_info_fail(self):
        result = CliRunner().invoke(cli, "project info --id 7890-7890-7890-7890")
        assert result.exit_code == 1
        assert "Something went wrong while getting the project" in result.output

    def test_command_project_info_ask(self):
        config.project.clean_config()
        result = CliRunner().invoke(cli, "project info")
        assert result.exit_code == 0
        assert "SUUID:       1234-1234-1234-1234" in result.output
        assert "Created:  2021-06-29 08:16:05.554963+00:00" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliProjectChange:
    """
    Test 'askanna project change' where we test changing project config
    """

    def test_command_project_change_help(self):
        result = CliRunner().invoke(cli, "project change --help")
        assert result.exit_code == 0
        assert "project change [OPTIONS]" in result.output

    def test_command_project_change(self):
        result = CliRunner().invoke(cli, ["project", "change", "--id", "1234-1234-1234-1234", "--name", "new name"])
        assert result.exit_code == 0
        assert "You succesfully changed project 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_project_change_no_input(self):
        config.project.clean_config()
        result = CliRunner().invoke(cli, "project change", input="y\nnew name\nn\nn\ny")
        assert result.exit_code == 0
        assert "You succesfully changed project 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_project_change_not_found(self):
        result = CliRunner().invoke(
            cli, ["project", "change", "--id", "7890-7890-7890-7890", "--description", "new description"]
        )
        assert result.exit_code == 1
        assert "The project SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_project_change_error(self):
        result = CliRunner().invoke(cli, ["project", "change", "--id", "0987-0987-0987-0987", "--name", "new name"])
        assert result.exit_code == 1
        assert "Something went wrong while changing the project SUUID '0987-0987-0987-0987'" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliProjectCreate:
    """
    Test 'askanna project create' where we test creating a project
    """

    def test_command_project_create_help(self):
        result = CliRunner().invoke(cli, "project create --help")
        assert result.exit_code == 0
        assert "project create [OPTIONS]" in result.output

    def test_command_project_create(self):
        result = CliRunner().invoke(
            cli,
            [
                "project",
                "create",
                "--workspace",
                "1234-1234-1234-1234",
                "--name",
                "a new project",
                "--description",
                "description new project",
                "--visibility",
                "PUBLIC",
            ],
            input="y",
        )
        assert result.exit_code == 0
        assert "You successfully created project 'a new project' with SUUID 'abcd-abcd-abcd-abcd'" in result.output

    def test_command_project_create_error(self):
        result = CliRunner().invoke(
            cli,
            ["project", "create", "--workspace", "1234-1234-1234-1234", "--visibility", "PRIVATE"],
            input="project with error\n\ny",
        )
        assert result.exit_code == 1
        assert "Something went wrong while creating the project" in result.output
        assert "{'error': 'Internal Server Error'}" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliProjectRemove:
    """
    Test 'askanna project remove' where we test removing a project
    """

    def test_command_project_remove_help(self):
        result = CliRunner().invoke(cli, "project remove --help")
        assert result.exit_code == 0
        assert "project remove [OPTIONS]" in result.output

    def test_command_project_remove(self):
        result = CliRunner().invoke(cli, ["project", "remove", "--id", "1234-1234-1234-1234", "--force"])
        assert result.exit_code == 0
        assert "You removed project SUUID '1234-1234-1234-1234'" in result.output

    def test_command_project_remove_confirm(self):
        result = CliRunner().invoke(cli, ["project", "remove", "--id", "1234-1234-1234-1234"], input="y")
        assert result.exit_code == 0
        assert "You removed project SUUID '1234-1234-1234-1234'" in result.output

    def test_command_project_remove_abort(self):
        result = CliRunner().invoke(cli, ["project", "remove", "--id", "1234-1234-1234-1234"], input="n")
        assert result.exit_code == 0
        assert "Understood. We are not removing the project." in result.output

    def test_command_project_remove_not_found(self):
        result = CliRunner().invoke(cli, ["project", "remove", "--id", "7890-7890-7890-7890", "--force"])
        assert result.exit_code == 1
        assert "The project SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_project_remove_error(self):
        result = CliRunner().invoke(cli, ["project", "remove", "--id", "0987-0987-0987-0987", "--force"])
        assert result.exit_code == 1
        assert "Something went wrong while removing the project SUUID '0987-0987-0987-0987" in result.output

    def test_command_project_remove_error_2(self):
        result = CliRunner().invoke(cli, ["project", "remove", "--id", "4321-4321-4321-4321", "--force"])
        assert result.exit_code == 1
        assert "Something went wrong while removing the project SUUID '4321-4321-4321-4321" in result.output
