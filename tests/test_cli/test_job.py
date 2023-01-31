import pytest
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config


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

    def test_command_job_list_project(self):
        result = CliRunner().invoke(cli, "job list -p 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "The jobs for project" in result.output

    def test_command_job_list_project_with_note(self):
        result = CliRunner().invoke(cli, "job list -p 3456-3456-3456-3456")
        assert result.exit_code == 0
        assert "The jobs for project" in result.output
        assert "Note: the first 1 of 1,000 jobs are shown" in result.output

    def test_command_job_list_workspace(self):
        result = CliRunner().invoke(cli, "job list -w 4321-4321-4321-4321")
        assert result.exit_code == 0
        assert "The jobs for workspace" in result.output

    def test_command_job_list_error(self):
        result = CliRunner().invoke(cli, "job list -p 7890-7890-7890-7890")
        assert result.exit_code == 1
        assert "Something went wrong while listing the jobs" in result.output

    def test_command_job_list_empty(self):
        result = CliRunner().invoke(cli, "job list -p 5678-5678-5678-5678")
        assert result.exit_code == 0
        assert "We cannot find any job." in result.output


@pytest.mark.usefixtures("api_response")
class TestCliJobInfo:
    """
    Test 'askanna job info' where we expect to get a info of a job
    """

    def test_command_job_info_help(self):
        result = CliRunner().invoke(cli, "job info --help")
        assert result.exit_code == 0
        assert "job info [OPTIONS]" in result.output

    def test_command_job_info(self):
        result = CliRunner().invoke(cli, "job info --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "SUUID:       1234-1234-1234-1234" in result.output
        assert "Created:  2022-10-17 06:53:04.148997+00:00" in result.output

    def test_command_job_info_fail(self):
        result = CliRunner().invoke(cli, "job info --id 7890-7890-7890-7890")
        assert result.exit_code == 1
        assert "Something went wrong while getting the job info" in result.output

    def test_command_job_info_with_notifications(self):
        result = CliRunner().invoke(cli, "job info --id 5678-5678-5678-5678")
        assert result.exit_code == 0
        assert "SUUID:       5678-5678-5678-5678" in result.output
        assert "Notifications: Yes" in result.output

    def test_command_job_info_ask_job(self):
        config.project.clean_config()
        result = CliRunner().invoke(cli, ["job", "info"])
        assert result.exit_code == 0
        assert "Selected workspace" in result.output
        assert "Selected job" in result.output
        assert "Created:  2022-10-17 06:53:04.148997+00:00" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliJobRunRequest:
    """
    Test 'askanna job run request' where we expect to do a request to run a job
    """

    def test_command_job_run_request_help(self):
        result = CliRunner().invoke(cli, "job run-request --help")
        assert result.exit_code == 0
        assert "job run-request [OPTIONS]" in result.output

    def test_command_job_info(self):
        result = CliRunner().invoke(cli, "job run-request --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "Succesfully started a new run" in result.output
        assert "abcd-abcd-abcd-abcd" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliJobChange:
    """
    Test 'askanna job change' where we test changing job info
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

    def test_command_job_remove_error_2(self):
        result = CliRunner().invoke(cli, ["job", "remove", "--id", "9876-9876-9876-9876", "--force"])
        assert result.exit_code == 1
        assert "Something went wrong while removing the job SUUID '9876-9876-9876-9876" in result.output
