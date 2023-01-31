import pytest
from click.testing import CliRunner

from askanna.cli import cli
from askanna.config import config


class TestCliRunMain:
    """
    Test 'askanna run' main command
    """

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, "--help")
        assert result.exit_code == 0
        assert "run" in result.output

    def test_command_run_help(self):
        result = CliRunner().invoke(cli, "run --help")
        assert result.exit_code == 0
        assert "run [OPTIONS]" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunRequest:
    """
    Test 'askanna run' where we expect to do a request to run a job
    """

    def test_command_run_help(self):
        result = CliRunner().invoke(cli, "run --help")
        assert result.exit_code == 0
        assert "run [OPTIONS] [JOB_NAME]" in result.output

    def test_command_run_request(self):
        result = CliRunner().invoke(cli, "run --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "Succesfully started a new run" in result.output
        assert "abcd-abcd-abcd-abcd" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunList:
    """
    Test 'askanna run list' where we expect to get a list of runs
    """

    def test_command_run_list_help(self):
        result = CliRunner().invoke(cli, "run list --help")
        assert result.exit_code == 0
        assert "run [JOB_NAME] list [OPTIONS]" in result.output
        assert "Search for a" in result.output

    def test_command_run_list(self):
        result = CliRunner().invoke(cli, "run list")
        assert result.exit_code == 0
        assert "1234-1234-1234-1234" in result.output

    def test_command_run_list_job(self):
        result = CliRunner().invoke(cli, "run list -j 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "The runs for job" in result.output

    def test_command_run_list_project(self):
        result = CliRunner().invoke(cli, "run list -p 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "The runs for project" in result.output

    def test_command_run_list_project_with_note(self):
        result = CliRunner().invoke(cli, "run list -p 3456-3456-3456-3456")
        assert result.exit_code == 0
        assert "The runs for project" in result.output
        assert "Note: the first 1 of 1,000 runs are shown" in result.output

    def test_command_run_list_workspace(self):
        result = CliRunner().invoke(cli, "run list -w 4321-4321-4321-4321")
        assert result.exit_code == 0
        assert "The runs for workspace" in result.output

    def test_command_run_list_error(self):
        result = CliRunner().invoke(cli, "run list -p 7890-7890-7890-7890")
        assert result.exit_code == 1
        assert "Something went wrong while listing the runs" in result.output

    def test_command_run_list_empty(self):
        result = CliRunner().invoke(cli, "run list -p 5678-5678-5678-5678")
        assert result.exit_code == 0
        assert "We cannot find any run." in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunInfo:
    """
    Test 'askanna run info' where we expect to get a info of a run
    """

    def test_command_run_info_help(self):
        result = CliRunner().invoke(cli, "run info --help")
        assert result.exit_code == 0
        assert "run [JOB_NAME] info [OPTIONS]" in result.output

    def test_command_run_info(self):
        result = CliRunner().invoke(cli, "run info --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "SUUID:           1234-1234-1234-1234" in result.output
        assert "Created:         2023-01-26 09:47:41 UTC" in result.output

    def test_command_run_info_no_metric_no_variable(self):
        result = CliRunner().invoke(cli, "run info --id 4321-4321-4321-4321")
        assert result.exit_code == 0
        assert "SUUID:           4321-4321-4321-4321" in result.output
        assert "Created:         2023-01-26 09:47:41 UTC" in result.output
        assert "No metrics" in result.output
        assert "No variables" in result.output

    def test_command_run_info_fail(self):
        result = CliRunner().invoke(cli, "run info --id 7890-7890-7890-7890")
        assert result.exit_code == 1
        assert "The run SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_run_info_fail_2(self):
        result = CliRunner().invoke(cli, "run info --id 0987-0987-0987-0987")
        assert result.exit_code == 1
        assert "Something went wrong while getting info of run SUUID '0987-0987-0987-0987':" in result.output

    def test_command_run_info_ask_run(self):
        config.project.clean_config()
        result = CliRunner().invoke(cli, "run info")
        assert result.exit_code == 0
        assert "Selected workspace" in result.output
        assert "Selected run" in result.output
        assert "Created:         2023-01-26 09:47:41 UTC" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunStatus:
    """
    Test 'askanna run status' where we expect to get the run status
    """

    def test_command_run_status_help(self):
        result = CliRunner().invoke(cli, "run status --help")
        assert result.exit_code == 0
        assert "run [JOB_NAME] status [OPTIONS]" in result.output

    def test_command_run_status(self):
        result = CliRunner().invoke(cli, "run status --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "Status run SUUID '1234-1234-1234-1234': queued" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunLog:
    """
    Test 'askanna run log' where we expect to get the run logs
    """

    def test_command_run_log_help(self):
        result = CliRunner().invoke(cli, "run log --help")
        assert result.exit_code == 0
        assert "run [JOB_NAME] log [OPTIONS]" in result.output

    def test_command_run_log(self):
        result = CliRunner().invoke(cli, "run log --id 1234-1234-1234-1234")
        assert result.exit_code == 0
        assert "Log run SUUID '1234-1234-1234-1234'" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunChange:
    """
    Test 'askanna run change' where we test changing run info
    """

    def test_command_run_change_help(self):
        result = CliRunner().invoke(cli, "run change --help")
        assert result.exit_code == 0
        assert "run [JOB_NAME] change [OPTIONS]" in result.output

    def test_command_run_change(self):
        result = CliRunner().invoke(cli, "run change --id 1234-1234-1234-1234 --name 'new name'")
        assert result.exit_code == 0
        assert "You succesfully changed run 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_run_change_no_input(self):
        result = CliRunner().invoke(cli, "run change", input="y\nnew name\ny\nnew description\ny")
        assert result.exit_code == 0
        assert "You succesfully changed run 'new name' with SUUID '1234-1234-1234-1234'" in result.output

    def test_command_run_change_not_found(self):
        result = CliRunner().invoke(cli, "run change --id 7890-7890-7890-7890 --description 'new description'")
        assert result.exit_code == 1
        assert "The run SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_run_change_error(self):
        result = CliRunner().invoke(cli, "run change --id 0987-0987-0987-0987 --name 'new name'")
        assert result.exit_code == 1
        assert "Something went wrong while changing the run SUUID '0987-0987-0987-0987'" in result.output


@pytest.mark.usefixtures("api_response")
class TestCliRunRemove:
    """
    Test 'askanna run remove' where we test removing a run
    """

    def test_command_run_remove_help(self):
        result = CliRunner().invoke(cli, "run remove --help")
        assert result.exit_code == 0
        assert "run [JOB_NAME] remove [OPTIONS]" in result.output

    def test_command_run_remove(self):
        result = CliRunner().invoke(cli, "run remove --id 1234-1234-1234-1234 --force")
        assert result.exit_code == 0
        assert "You removed run SUUID '1234-1234-1234-1234'" in result.output

    def test_command_run_remove_confirm(self):
        result = CliRunner().invoke(cli, "run remove --id 1234-1234-1234-1234", input="y")
        assert result.exit_code == 0
        assert "You removed run SUUID '1234-1234-1234-1234'" in result.output

    def test_command_run_remove_no_input(self):
        result = CliRunner().invoke(cli, "run remove", input="y")
        assert result.exit_code == 0
        assert "You removed run SUUID '1234-1234-1234-1234'" in result.output

    def test_command_run_remove_abort(self):
        result = CliRunner().invoke(cli, "run remove --id 1234-1234-1234-1234", input="n")
        assert result.exit_code == 0
        assert "Understood. We are not removing the run." in result.output

    def test_command_run_remove_not_found(self):
        result = CliRunner().invoke(cli, "run remove --id 7890-7890-7890-7890 --force")
        assert result.exit_code == 1
        assert "The run SUUID '7890-7890-7890-7890' was not found" in result.output

    def test_command_run_remove_error(self):
        result = CliRunner().invoke(cli, "run remove --id 0987-0987-0987-0987 --force")
        assert result.exit_code == 1
        assert "Something went wrong while getting the info of run SUUID '0987-0987-0987-0987" in result.output

    def test_command_run_remove_error_2(self):
        result = CliRunner().invoke(cli, "run remove --id 9876-9876-9876-9876 --force")
        assert result.exit_code == 1
        assert "Something went wrong while removing the run SUUID '9876-9876-9876-9876" in result.output
