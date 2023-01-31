import pytest
from click.testing import CliRunner

from askanna.cli import cli


class TestCliWorkspaceMain:
    """
    Test 'askanna workspace' main command
    """

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, "--help")
        assert result.exit_code == 0
        assert "workspace" in result.output

    def test_command_workspace_help(self):
        result = CliRunner().invoke(cli, ["workspace", "--help"])
        assert result.exit_code == 0
        assert "workspace [OPTIONS]" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliWorkspaceList:
    """
    Test 'askanna workspace list' where we expect to get a list of workspaces
    """

    def test_command_workspace_list_help(self):
        result = CliRunner().invoke(cli, "workspace list --help")
        assert result.exit_code == 0
        assert "workspace list [OPTIONS]" in result.output

    def test_command_workspace_list(self):
        result = CliRunner().invoke(cli, "workspace list")
        assert result.exit_code == 0
        assert "WORKSPACE SUUID" in result.output
        assert "1234-1234-1234-1234" in result.output
        assert "SUUID: 1234-1234-1234-1234" not in result.output


@pytest.mark.usefixtures("api_response")
class TestCliWorkspaceInfo:
    """
    Test 'askanna workspace info' where we expect to get a info of a workspace
    """

    def test_command_workspace_info_help(self):
        result = CliRunner().invoke(cli, "workspace info --help")
        assert result.exit_code == 0
        assert "workspace info [OPTIONS]" in result.output

    def test_command_workspace_info(self):
        result = CliRunner().invoke(cli, ["workspace", "info", "--id", "1234-1234-1234-1234"])
        assert result.exit_code == 0
        assert "SUUID:       1234-1234-1234-1234" in result.output
        assert "Created:  2020-04-01 09:44:11.853000+00:00" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliWorkspaceChange:
    """
    Test 'askanna workspace change' where we test changing workspace config
    """

    def test_command_workspace_change_help(self):
        result = CliRunner().invoke(cli, "workspace change --help")
        assert result.exit_code == 0
        assert "workspace change [OPTIONS]" in result.output

    def test_command_workspace_change(self):
        result = CliRunner().invoke(cli, ["workspace", "change", "--id", "1234-1234-1234-1234", "--name", "new name"])
        assert result.exit_code == 0
        assert "You succesfully changed workspace 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_workspace_change_no_input(self):
        result = CliRunner().invoke(
            cli, ["workspace", "change", "--id", "1234-1234-1234-1234"], input="y\nnew name\nn\nn\ny"
        )
        assert result.exit_code == 0
        assert "You succesfully changed workspace 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_workspace_change_not_found(self):
        result = CliRunner().invoke(
            cli, ["workspace", "change", "--id", "7890-7890-7890-7890", "--description", "new description"]
        )
        assert result.exit_code == 1
        assert "The workspace SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_workspace_change_error(self):
        result = CliRunner().invoke(cli, ["workspace", "change", "--id", "0987-0987-0987-0987", "--name", "new name"])
        assert result.exit_code == 1
        assert "Something went wrong while changing the workspace SUUID '0987-0987-0987-0987'" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliWorkspaceCreate:
    """
    Test 'askanna workspace create' where we test creating a workspace
    """

    def test_command_workspace_create_help(self):
        result = CliRunner().invoke(cli, "workspace create --help")
        assert result.exit_code == 0
        assert "workspace create [OPTIONS]" in result.output

    def test_command_workspace_create(self):
        result = CliRunner().invoke(
            cli,
            [
                "workspace",
                "create",
                "--name",
                "a new workspace",
                "--description",
                "description new workspace",
                "--visibility",
                "PUBLIC",
            ],
            input="y",
        )
        assert result.exit_code == 0
        assert "You successfully created workspace 'a new workspace' with SUUID '4buD-tVhI-emHj-QXCY'" in result.output

    def test_command_workspace_create_error(self):
        result = CliRunner().invoke(
            cli, ["workspace", "create", "--visibility", "PRIVATE"], input="workspace with error\n\ny"
        )
        assert result.exit_code == 1
        assert "Something went wrong while creating the workspace" in result.output
        assert "{'error': 'Internal Server Error'}" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliWorkspaceRemove:
    """
    Test 'askanna workspace remove' where we test removing a workspace
    """

    def test_command_workspace_remove_help(self):
        result = CliRunner().invoke(cli, "workspace remove --help")
        assert result.exit_code == 0
        assert "workspace remove [OPTIONS]" in result.output

    def test_command_workspace_remove(self):
        result = CliRunner().invoke(cli, ["workspace", "remove", "--id", "1234-1234-1234-1234", "--force"])
        assert result.exit_code == 0
        assert "You removed workspace SUUID '1234-1234-1234-1234'" in result.output

    def test_command_workspace_remove_confirm(self):
        result = CliRunner().invoke(cli, ["workspace", "remove", "--id", "1234-1234-1234-1234"], input="y")
        assert result.exit_code == 0
        assert "You removed workspace SUUID '1234-1234-1234-1234'" in result.output

    def test_command_workspace_remove_abort(self):
        result = CliRunner().invoke(cli, ["workspace", "remove", "--id", "1234-1234-1234-1234"], input="n")
        assert result.exit_code == 0
        assert "Understood. We are not removing the workspace." in result.output

    def test_command_workspace_remove_not_found(self):
        result = CliRunner().invoke(cli, ["workspace", "remove", "--id", "7890-7890-7890-7890", "--force"])
        assert result.exit_code == 1
        assert "The workspace SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_workspace_remove_error(self):
        result = CliRunner().invoke(cli, ["workspace", "remove", "--id", "0987-0987-0987-0987", "--force"])
        assert result.exit_code == 1
        assert "Something went wrong while removing the workspace SUUID '0987-0987-0987-0987" in result.output
