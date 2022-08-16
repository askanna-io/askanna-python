from click.testing import CliRunner

from askanna.cli.tool import cli_commands

from .base import BaseCLItest


class TestCliPush(BaseCLItest):
    """
    askanna push

    We expect to initiate a push action of our code to the AskAnna server
    """

    verb = "push"

    def test_command_push_base(self):
        result = CliRunner().invoke(cli_commands, "push --help")

        self.assertIn("push", result.output)
        self.assertNotIn("noop", result.output)
