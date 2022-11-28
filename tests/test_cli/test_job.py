import pytest
from click.testing import CliRunner

from askanna.cli import cli


class TestCliJobMain:
    """
    Test 'askanna job' main command
    """

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, "--help")
        assert result.exit_code == 0
        assert "job" in result.output

    def test_command_job_help(self):
        result = CliRunner().invoke(cli, "job --help")
        assert result.exit_code == 0
        assert "job [OPTIONS]" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliJobList:
    """
    Test 'askanna job list' where we expect to get a list of jobs
    """

    def test_command_job_list_help(self):
        result = CliRunner().invoke(cli, "job list --help")
        assert result.exit_code == 0
        assert "job list [OPTIONS]" in result.output

    def test_command_job_list(self):
        result = CliRunner().invoke(cli, "job list")
        assert result.exit_code == 0
        assert "1234-1234-1234-1234" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliJobChange:
    """
    Test 'askanna job change' where we test changing job config
    """

    def test_command_job_change_help(self):
        result = CliRunner().invoke(cli, "job change --help")
        assert result.exit_code == 0
        assert "job change [OPTIONS]" in result.output

    def test_command_job_change(self):
        result = CliRunner().invoke(cli, ["job", "change", "--id", "1234-1234-1234-1234", "--name", "new name"])
        assert result.exit_code == 0
        assert "You succesfully changed job 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_job_change_no_input(self):
        result = CliRunner().invoke(cli, ["job", "change", "--id", "1234-1234-1234-1234"], input="y\nnew name\nn\ny")
        assert result.exit_code == 0
        assert "You succesfully changed job 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_job_change_not_found(self):
        result = CliRunner().invoke(
            cli, ["job", "change", "--id", "7890-7890-7890-7890", "--description", "new description"]
        )
        assert result.exit_code == 1
        assert "The job SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_job_change_error(self):
        result = CliRunner().invoke(cli, ["job", "change", "--id", "0987-0987-0987-0987", "--name", "new name"])
        assert result.exit_code == 1
        assert "Something went wrong while changing the job SUUID '0987-0987-0987-0987'" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliJobRemove:
    """
    Test 'askanna job remove' where we test removing a job
    """

    def test_command_job_remove_help(self):
        result = CliRunner().invoke(cli, "job remove --help")
        assert result.exit_code == 0
        assert "job remove [OPTIONS]" in result.output

    def test_command_job_remove(self):
        result = CliRunner().invoke(cli, ["job", "remove", "--id", "1234-1234-1234-1234", "--force"])
        assert result.exit_code == 0
        assert "You removed job SUUID '1234-1234-1234-1234'" in result.output

    def test_command_job_remove_confirm(self):
        result = CliRunner().invoke(cli, ["job", "remove", "--id", "1234-1234-1234-1234"], input="y")
        assert result.exit_code == 0
        assert "You removed job SUUID '1234-1234-1234-1234'" in result.output

    def test_command_job_remove_abort(self):
        result = CliRunner().invoke(cli, ["job", "remove", "--id", "1234-1234-1234-1234"], input="n")
        assert result.exit_code == 0
        assert "Understood. We are not removing the job." in result.output

    def test_command_job_remove_not_found(self):
        result = CliRunner().invoke(cli, ["job", "remove", "--id", "7890-7890-7890-7890", "--force"])
        assert result.exit_code == 1
        assert "The job SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_job_remove_error(self):
        result = CliRunner().invoke(cli, ["job", "remove", "--id", "0987-0987-0987-0987", "--force"])
        assert result.exit_code == 1
        assert "Something went wrong while removing the job SUUID '0987-0987-0987-0987" in result.output
