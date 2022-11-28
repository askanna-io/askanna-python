import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from askanna.cli.run_utils import cli


@pytest.mark.usefixtures("api_response", "reset_environment_and_work_dir")
class TestCliGetRunManifest:
    """
    Test 'askanna-run-utils get-run-manifest'
    """

    verb = "get-run-manifest"

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert self.verb in result.output

    def test_command_get_run_manifest_help(self):
        result = CliRunner().invoke(cli, [self.verb, "--help"])
        assert result.exit_code == 0
        assert f"{self.verb} [OPTIONS]" in result.output

    def test_command_get_run_manifest_no_run_suuid(self):
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_get_run_manifest_successs(self, temp_dir, run_manifest):
        run_suuid = "1234-1234-1234-1234"
        run_manifest_path = str(temp_dir) + "/run-manifest-1234/entrypoint.sh"

        result = CliRunner().invoke(cli, f"{self.verb} --run {run_suuid} --output {run_manifest_path}")

        assert result.exit_code == 0
        assert Path(run_manifest_path).exists()
        assert Path(run_manifest_path).is_file()
        assert Path(run_manifest_path).read_text() == run_manifest

    def test_command_get_run_manifest_successs_environment_variables(self, temp_dir, run_manifest):
        run_suuid = "1234-1234-1234-1234"
        run_manifest_path = str(temp_dir) + "/run-manifest-1234/entrypoint.sh"

        os.environ["AA_RUN_SUUID"] = run_suuid
        os.environ["AA_RUN_MANIFEST_PATH"] = run_manifest_path

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 0
        assert Path(run_manifest_path).exists()
        assert Path(run_manifest_path).is_file()
        assert Path(run_manifest_path).read_text() == run_manifest

    def test_command_get_run_manifest_not_exist(self):
        run_suuid = "wxyz-wxyz-wxyz-wxyz"

        result = CliRunner().invoke(cli, f"{self.verb} --run {run_suuid}")

        assert result.exit_code == 1
        assert f"404 - The manifest for run SUUID '{run_suuid}' was not found" in result.output

    def test_command_get_run_manifest_not_exist_environment_variables(self):
        run_suuid = "wxyz-wxyz-wxyz-wxyz"

        os.environ["AA_RUN_SUUID"] = run_suuid

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 1
        assert f"404 - The manifest for run SUUID '{run_suuid}' was not found" in result.output

    def test_command_get_run_manifest_not_200(self):
        run_suuid = "zyxw-zyxw-zyxw-zyxw"

        result = CliRunner().invoke(cli, f"{self.verb} --run {run_suuid}")

        assert result.exit_code == 1
        assert f"500 - Something went wrong while retrieving the manifest for run SUUID '{run_suuid}'" in result.output

    def test_command_get_run_manifest_not_200_environment_variables(self):
        run_suuid = "zyxw-zyxw-zyxw-zyxw"

        os.environ["AA_RUN_SUUID"] = run_suuid

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 1
        assert f"500 - Something went wrong while retrieving the manifest for run SUUID '{run_suuid}'" in result.output
