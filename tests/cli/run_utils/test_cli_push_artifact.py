import os
import sys
import unittest

import pytest
import responses
from click.testing import CliRunner

from askanna.cli.run_utils.tool import cli_commands
from askanna.core.apiclient import client


def delete_modules():
    try:  # nosec
        del sys.modules["askanna.cli.run_utils.tool"]
        del sys.modules["askanna.cli.run_utils.push_artifact"]
        del sys.modules["askanna.core.apiclient"]
        del sys.modules["askanna.config"]
        del sys.modules["askanna.config.server"]
        del sys.modules["askanna.config.project"]
    except:  # noqa
        pass


@pytest.fixture(autouse=True)
def test_setup_and_teardown(monkeypatch):
    cwd = os.getcwd()
    environ_bck = dict(os.environ)
    os.environ["AA_REMOTE"] = "https://beta-api.askanna.eu"
    os.environ["AA_TOKEN"] = "12345678910"  # nosec

    yield

    os.chdir(cwd)
    os.environ.clear()
    os.environ.update(environ_bck)


class TestCLIPushArtifact(unittest.TestCase):
    """
    Test 'askanna-run-utils push-artifact'
    """

    verb = "push-artifact"

    def setUp(self):
        self.base_url = client.base_url

        self.responses = responses.RequestsMock()
        self.responses.start()

        self.responses.add(
            responses.POST,
            url=self.base_url + "runinfo/abcd-abcd-abcd-abcd/artifact/",
            json={"short_uuid": "1234-1234-1234-1234"},
            status=201,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url + "runinfo/abcd-abcd-abcd-abcd/artifact/1234-1234-1234-1234/artifactchunk/",
            json={"uuid": "ab12-ab12-ab12-ab12"},
            status=201,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url
            + "runinfo/abcd-abcd-abcd-abcd/artifact/1234-1234-1234-1234/artifactchunk/ab12-ab12-ab12-ab12/chunk/",  # noqa
            status=200,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url + "runinfo/abcd-abcd-abcd-abcd/artifact/1234-1234-1234-1234/finish_upload/",
            status=200,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

    def test_command_line_access(self):
        result = CliRunner().invoke(
            cli_commands,
            [
                "--help",
                self.verb,
            ],
        )
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_command_push_artifact(self):
        result = CliRunner().invoke(
            cli_commands,
            [
                "--help",
                self.verb,
            ],
        )
        assert self.verb in result.output
        self.assertIn(self.verb, result.output)
        self.assertNotIn("noop", result.output)

    def test_command_push_artifact_help(self):
        result = CliRunner().invoke(cli_commands, self.verb + " --help")
        assert f"{self.verb} [OPTIONS]" in result.output

    def test_command_push_artifact_unregistered_run(self):
        result = CliRunner().invoke(cli_commands, self.verb)
        assert result.exit_code == 1
        assert "Cannot push artifact from unregistered run to AskAnna." in result.output

    def test_command_push_artifact_missing_job_name(self):
        os.environ["AA_RUN_SUUID"] = "abcd-abcd-abcd-abcd"
        result = CliRunner().invoke(cli_commands, self.verb)
        assert result.exit_code == 1
        assert "The job name is not set. We cannot push artifact to AskAnna." in result.output

    def test_command_push_artifact_config_ok_no_artifact(self):
        project_dir = "tests/resources/projects/project-001-simple"
        os.chdir(project_dir)

        os.environ["AA_RUN_SUUID"] = "abcd-abcd-abcd-abcd"
        os.environ["AA_JOB_NAME"] = "test_job"

        delete_modules()
        from askanna.cli.run_utils.tool import cli_commands

        result = CliRunner().invoke(cli_commands, self.verb)
        assert result.exit_code == 0
        assert "Artifact creation aborted, no `output/artifact` defined for this job in `askanna.yml`" in result.output

    def test_command_push_artifact_config_ok_job_with_artifact(self):
        project_dir = "tests/resources/projects/project-001-simple"
        os.chdir(project_dir)

        os.environ["AA_RUN_SUUID"] = "abcd-abcd-abcd-abcd"
        os.environ["AA_JOB_NAME"] = "test_job_artifact"

        delete_modules()
        from askanna.cli.run_utils.tool import cli_commands

        result = CliRunner().invoke(cli_commands, self.verb)
        assert result.exit_code == 0
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" in result.output

    def test_command_push_artifact_config_ok_with_depr_paths(self):
        project_dir = "tests/resources/projects/project-001-simple"
        os.chdir(project_dir)

        os.environ["AA_RUN_SUUID"] = "abcd-abcd-abcd-abcd"
        os.environ["AA_JOB_NAME"] = "test_job_depr_paths"

        delete_modules()
        from askanna.cli.run_utils.tool import cli_commands

        result = CliRunner().invoke(cli_commands, self.verb)

        assert result.exit_code == 0
        assert "Deprecation warning: in a future version we remove the output/paths option." in result.output
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" in result.output

    def test_command_push_artifact_config_artifact_path_with_variable(self):
        project_dir = "tests/resources/projects/project-001-simple"
        os.chdir(project_dir)

        os.environ["AA_RUN_SUUID"] = "abcd-abcd-abcd-abcd"
        os.environ["AA_JOB_NAME"] = "test_job_artifact_variable"
        os.environ["FILENAME"] = "result"

        delete_modules()
        from askanna.cli.run_utils.tool import cli_commands

        result = CliRunner().invoke(cli_commands, self.verb)
        assert result.exit_code == 0
        assert "Uploading artifact to AskAnna..." in result.output
        assert "Artifact is uploaded" in result.output
        assert "does not exists...skipping" not in result.output
