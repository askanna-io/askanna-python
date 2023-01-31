import os

import pytest
from click.testing import CliRunner

from askanna.cli.run_utils import cli
from askanna.config import config


@pytest.mark.usefixtures("api_response", "reset_environment_and_work_dir")
class TestCLIPushResult:
    """
    Test 'askanna-run-utils push-result'
    """

    verb = "push-result"
    run_suuid = "1234-1234-1234-1234"
    run_suuid_fail = "5678-5678-5678-5678"
    run_suuid_finish_fail = "7890-7890-7890-7890"

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert self.verb in result.output

    def test_command_push_result_help(self):
        result = CliRunner().invoke(cli, [self.verb, "--help"])
        assert result.exit_code == 0
        assert f"{self.verb} [OPTIONS]" in result.output

    def test_command_push_result_unregistered_run(self):
        os.environ["AA_RUN_SUUID"] = ""
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_push_result_missing_job_name(self):
        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = ""
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_push_result_config_ok_no_result(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 0
        assert "Result: no `result` defined for this job in `askanna.yml`" in result.output

    def test_command_push_result_no_list(self):
        project_dir = "tests/fixtures/projects/project-004-wrong-config"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 1
        assert "Please enter a path in `result` definition, not a list." in result.output

    def test_command_push_result_config_ok_job_with_result(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job_result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 0
        assert "Uploading result to AskAnna..." in result.output
        assert "Result is uploaded" in result.output
        assert "does not exist." not in result.output

    def test_command_push_result_config_ok_job_with_result_not_exist(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job_result_not_exist"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 1
        assert "Uploading result to AskAnna..." not in result.output
        assert "Result is uploaded" not in result.output
        assert "does not exist." in result.output

    def test_command_push_result_config_result_path_with_variable(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job_result_variable"
        os.environ["FILENAME"] = "result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 0
        assert "Uploading result to AskAnna..." in result.output
        assert "Result is uploaded" in result.output
        assert "does not exist." not in result.output

    def test_command_push_result_config_ok_upload_fail(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid_fail
        os.environ["AA_JOB_NAME"] = "test_job_result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 1
        assert "Uploading result to AskAnna..." in result.output
        assert "Result is uploaded" not in result.output
        assert "In the AskAnna platform something went wrong" in result.output

    def test_command_push_result_config_ok_upload_fail_finish(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid_finish_fail
        os.environ["AA_JOB_NAME"] = "test_job_result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 1
        assert "Uploading result to AskAnna..." in result.output
        assert "Result is uploaded" not in result.output
        assert " Result upload failed" in result.output
