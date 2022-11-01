from click.testing import CliRunner

from askanna.cli.run_utils import cli


class TestCliPushMetrics:
    """
    Test 'askanna-run-utils push-metrics'
    """

    verb = "push-metrics"

    def test_command_line_access(self):
        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert self.verb in result.output

    def test_command_get_package_help(self):
        result = CliRunner().invoke(cli, [self.verb, "--help"])
        assert result.exit_code == 0
        assert f"{self.verb} [OPTIONS]" in result.output
