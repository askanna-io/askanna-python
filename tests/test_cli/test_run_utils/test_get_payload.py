import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from askanna.cli.run_utils import cli


@pytest.mark.usefixtures("api_response", "reset_environment_and_work_dir")
class TestCliGetPackage:
    """
    Test 'askanna-run-utils get-paylaod'
    """

    verb = "get-payload"

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert self.verb in result.output

    def test_command_get_payload_help(self):
        result = CliRunner().invoke(cli, [self.verb, "--help"])
        assert result.exit_code == 0
        assert f"{self.verb} [OPTIONS]" in result.output

    def test_command_get_payload_no_run_suuid(self):
        result = CliRunner().invoke(cli, self.verb)
        assert result.exit_code == 2

    def test_command_get_payload_no_payload_suuid(self):
        run_suuid = "1234-1234-1234-1234"
        result = CliRunner().invoke(cli, f"{self.verb} --run {run_suuid}")
        assert result.exit_code == 2

    def test_command_get_payload_successs(self, temp_dir, run_payload):
        run_suuid = "1234-1234-1234-1234"
        payload_suuid = "abcd-abcd-abcd-abcd"
        payload_path = str(temp_dir) + "/payload-abcd/payload.json"

        result = CliRunner().invoke(
            cli, f"{self.verb} --run {run_suuid} --payload {payload_suuid} --output {payload_path}"
        )

        assert result.exit_code == 0
        assert Path(payload_path).exists()
        assert Path(payload_path).is_file()

        assert Path(payload_path).read_text() == json.dumps(run_payload)

    def test_command_get_payload_successs_environment_variables(self, temp_dir, run_payload):
        run_suuid = "1234-1234-1234-1234"
        payload_suuid = "abcd-abcd-abcd-abcd"
        payload_path = str(temp_dir) + "/payload-abcd/payload.json"

        os.environ["AA_RUN_SUUID"] = run_suuid
        os.environ["AA_PAYLOAD_SUUID"] = payload_suuid
        os.environ["AA_PAYLOAD_PATH"] = payload_path

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 0
        assert Path(payload_path).exists()
        assert Path(payload_path).is_file()

        assert Path(payload_path).read_text() == json.dumps(run_payload)

    def test_command_get_payload_not_exist(self):
        run_suuid = "1234-1234-1234-1234"
        payload_suuid = "wxyz-wxyz-wxyz-wxyz"

        result = CliRunner().invoke(cli, f"{self.verb} --run {run_suuid} --payload {payload_suuid}")

        assert result.exit_code == 1
        assert f"404 - The payload for run SUUID '{run_suuid}' was not found" in result.output

    def test_command_get_payload_not_exist_environment_variables(self):
        run_suuid = "1234-1234-1234-1234"
        payload_suuid = "wxyz-wxyz-wxyz-wxyz"

        os.environ["AA_RUN_SUUID"] = run_suuid
        os.environ["AA_PAYLOAD_SUUID"] = payload_suuid

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 1
        assert f"404 - The payload for run SUUID '{run_suuid}' was not found" in result.output

    def test_command_get_payload_not_200(self):
        run_suuid = "1234-1234-1234-1234"
        payload_suuid = "zyxw-zyxw-zyxw-zyxw"

        result = CliRunner().invoke(cli, f"{self.verb} --run {run_suuid} --payload {payload_suuid}")

        assert result.exit_code == 1
        assert f"500 - Something went wrong while retrieving the payload for run SUUID '{run_suuid}'" in result.output

    def test_command_get_payload_not_200_environment_variables(self):
        run_suuid = "1234-1234-1234-1234"
        payload_suuid = "zyxw-zyxw-zyxw-zyxw"

        os.environ["AA_RUN_SUUID"] = run_suuid
        os.environ["AA_PAYLOAD_SUUID"] = payload_suuid

        result = CliRunner().invoke(cli, f"{self.verb}")

        assert result.exit_code == 1
        assert f"500 - Something went wrong while retrieving the payload for run SUUID '{run_suuid}'" in result.output
