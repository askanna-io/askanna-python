from click.testing import CliRunner

from askanna.cli.run_utils import __main__, cli


def test_command_line_access():
    result = CliRunner().invoke(cli, "--help")
    assert result.exit_code == 0
    assert "The run util is used to support AskAnna runs" in result.output


def test_cli_import_main():
    assert "cli" in dir(__main__)
