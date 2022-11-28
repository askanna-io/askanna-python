import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from askanna.cli.run_utils import cli


@pytest.mark.usefixtures("api_response", "reset_environment_and_work_dir")
class TestCliGetPackage:
    """
    Test 'askanna-run-utils get-package'
    """

    verb = "get-package"

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert self.verb in result.output

    def test_command_get_package_help(self):
        result = CliRunner().invoke(cli, [self.verb, "--help"])
        assert result.exit_code == 0
        assert f"{self.verb} [OPTIONS]" in result.output

    def test_command_get_package_no_package_suuid(self):
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_get_package_success(self, temp_dir):
        package_suuid = "1234-1234-1234-1234"
        code_dir = str(temp_dir) + "/code-1234"

        result = CliRunner().invoke(cli, f"{self.verb} --package {package_suuid} --output {code_dir}")

        assert result.exit_code == 0
        assert Path(code_dir).exists()

        num_files_code_dir = len([e for e in Path(code_dir).iterdir() if e.is_file()])
        assert num_files_code_dir == 1

    def test_command_get_package_environment_variables(self, temp_dir):
        package_suuid = "1234-1234-1234-1234"
        code_dir = str(temp_dir) + "/code-1234"

        os.environ["AA_PACKAGE_SUUID"] = package_suuid
        os.environ["AA_CODE_DIR"] = code_dir

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 0
        assert Path(code_dir).exists()

        num_files_code_dir = len([e for e in Path(code_dir).iterdir() if e.is_file()])
        assert num_files_code_dir == 1

    def test_command_get_package_not_exist(self):
        package_suuid = "wxyz-wxyz-wxyz-wxyz"

        result = CliRunner().invoke(cli, f"{self.verb} --package {package_suuid}")

        assert result.exit_code == 1
        assert f"404 - Package SUUID '{package_suuid}' was not found" in result.output

    def test_command_get_package_not_exist_environment_variables(self):
        package_suuid = "wxyz-wxyz-wxyz-wxyz"

        os.environ["AA_PACKAGE_SUUID"] = package_suuid

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 1
        assert f"404 - Package SUUID '{package_suuid}' was not found" in result.output
