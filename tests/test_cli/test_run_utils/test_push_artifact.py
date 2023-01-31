import os

import pytest
from click.testing import CliRunner

from askanna.cli.run_utils import cli
from askanna.config import config


@pytest.mark.usefixtures("api_response", "reset_environment_and_work_dir")
class TestCLIPushArtifact:
    """
    Test 'askanna-run-utils push-artifact'
    """

    verb = "push-artifact"
    run_suuid = "1234-1234-1234-1234"
    run_suuid_with_finish_fail = "7890-7890-7890-7890"
    run_suuid_not_found_artifact = "5678-5678-5678-5678"

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert self.verb in result.output

    def test_command_push_artifact_help(self):
        result = CliRunner().invoke(cli, [self.verb, "--help"])
        assert result.exit_code == 0
        assert f"{self.verb} [OPTIONS]" in result.output

    def test_command_push_artifact_unregistered_run(self):
        os.environ["AA_RUN_SUUID"] = ""
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_push_artifact_missing_job_name(self):
        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = ""
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_push_artifact_config_ok_no_artifact(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 0
        assert "Artifact: no `artifact` defined for this job in `askanna.yml`" in result.output

    def test_command_push_artifact_config_ok_job_with_artifact(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job_artifact"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 0
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" in result.output

    def test_command_push_artifact_config_artifact_path_with_variable(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid
        os.environ["AA_JOB_NAME"] = "test_job_artifact_variable"
        os.environ["FILENAME"] = "result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 0
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" in result.output
        assert "does not exists...skipping" not in result.output

    def test_command_push_artifact_config_ok_upload_fail(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid_with_finish_fail
        os.environ["AA_JOB_NAME"] = "test_job_artifact_variable"
        os.environ["FILENAME"] = "result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 1
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" not in result.output
        assert "Artifact upload failed" in result.output

    def test_command_push_artifact_config_ok_upload_fail_2(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)
        config.project.reload_config()

        os.environ["AA_RUN_SUUID"] = self.run_suuid_not_found_artifact
        os.environ["AA_JOB_NAME"] = "test_job_artifact_variable"
        os.environ["FILENAME"] = "result"

        result = CliRunner().invoke(cli, self.verb)

        assert result.exit_code == 1
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" not in result.output
        assert "In the AskAnna platform something went wrong" in result.output
