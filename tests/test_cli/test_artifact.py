import os
import shutil

import pytest
from click.testing import CliRunner

from askanna.cli import cli


@pytest.fixture()
def temp_artifact_dir(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("askanna-test-cli-artifact-")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestCLIArtifact:
    """
    Test 'askanna artifact' main command
    """

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, "--help")
        assert result.exit_code == 0
        assert "artifact" in result.output

    def test_command_artifact_help(self):
        result = CliRunner().invoke(cli, "artifact --help")
        assert result.exit_code == 0
        assert "artifact" in result.output


@pytest.mark.usefixtures("api_response", "reset_environment_and_work_dir")
class TestCLIArtifactGet:
    """
    Test 'askanna artifact get' where we expect to get a run artifact file
    """

    def test_command_artifact_get_help(self):
        result = CliRunner().invoke(cli, "artifact get --help")

        assert "artifact" in result.output
        assert "artifact get [OPTIONS]" in result.output

    def test_command_artifact_get_prompt_invalid_suuid(self):
        result = CliRunner().invoke(cli, "artifact get", input="test")

        assert result.exception
        assert "Run SUUID: test" in result.output

    def test_command_artifact_get_prompt(self, temp_dir):
        os.chdir(temp_dir)
        assert not os.path.exists("artifact_1234-1234-1234-1234.zip")

        result = CliRunner().invoke(cli, "artifact get", input="1234-1234-1234-1234")

        assert not result.exception
        assert "Run SUUID: 1234-1234-1234-1234" in result.output
        assert "Downloading the artifact has started..." in result.output
        assert "The artifact is saved in: artifact_1234-1234-1234-1234.zip" in result.output

        assert os.path.exists("artifact_1234-1234-1234-1234.zip")
        assert os.stat("artifact_1234-1234-1234-1234.zip").st_size == 198

    def test_command_artifact_get_argument_full(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "artifact get --id 1234-1234-1234-1234")

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert "The artifact is saved in: artifact_1234-1234-1234-1234.zip" in result.output

        assert os.path.exists("artifact_1234-1234-1234-1234.zip")
        assert os.stat("artifact_1234-1234-1234-1234.zip").st_size == 198

    def test_command_artifact_get_argument_short(self, temp_dir):
        os.chdir(temp_dir)
        result = CliRunner().invoke(cli, "artifact get -i 1234-1234-1234-1234")

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert "The artifact is saved in: artifact_1234-1234-1234-1234.zip" in result.output

        assert os.path.exists("artifact_1234-1234-1234-1234.zip")
        assert os.stat("artifact_1234-1234-1234-1234.zip").st_size == 198

    def test_command_artifact_get_unknown_file(self):
        result = CliRunner().invoke(cli, "artifact get", input="5678-5678-5678-5678")

        assert result.exception
        assert "Run SUUID: 5678-5678-5678-5678" in result.output
        assert "404 - The artifact for run SUUID '5678-5678-5678-5678' was not found" in result.output

    def test_command_artifact_get_already_exist(self):
        assert not os.path.exists("artifact_1234-1234-1234-1234.zip")

        CliRunner().invoke(cli, "artifact get", input="1234-1234-1234-1234")
        assert os.path.exists("artifact_1234-1234-1234-1234.zip")
        assert os.stat("artifact_1234-1234-1234-1234.zip").st_size == 198
        result = CliRunner().invoke(cli, "artifact get", input="1234-1234-1234-1234")

        assert os.path.exists("artifact_1234-1234-1234-1234.zip")
        assert os.stat("artifact_1234-1234-1234-1234.zip").st_size == 198

        os.remove("artifact_1234-1234-1234-1234.zip")

        assert result.exception
        assert "Run SUUID: 1234-1234-1234-1234" in result.output
        assert (
            "The file 'artifact_1234-1234-1234-1234.zip' already exists. We will not overwrite the existing file."
            in result.output
        )

    def test_command_artifact_get_argument_output_file(self, temp_dir):
        output_file = str(temp_dir) + "/artifact-1234-1234-12344-1244.zip"
        result = CliRunner().invoke(cli, f"artifact get --id 1234-1234-1234-1234 --output {output_file}")

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert f"The artifact is saved in: {output_file}" in result.output

        assert os.path.exists(output_file)
        assert os.stat(output_file).st_size == 198

    def test_command_artifact_get_argument_output_file_short(self, temp_dir):
        output_file = str(temp_dir) + "/artifact-1234-1234-12344-1244.zip"
        result = CliRunner().invoke(cli, f"artifact get -i 1234-1234-1234-1234 -o {output_file}")

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert f"The artifact is saved in: {output_file}" in result.output

        assert os.path.exists(output_file)
        assert os.stat(output_file).st_size == 198

    def test_command_artifact_get_argument_output_dir(self, temp_dir):
        result = CliRunner().invoke(cli, f"artifact get --id abcd-abcd-abcd-abcd --output {temp_dir}")

        assert result.exception
        assert "The output argument is a directory. Please provide a filename (zip) for the output." in result.output
