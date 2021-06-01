import unittest

from click.testing import CliRunner

from askanna.cli.tool import cli_commands


class BaseCLItest(unittest.TestCase):
    verb = ""

    def setUp(self):
        self.result = CliRunner().invoke(cli_commands, ['--help', self.verb, ])

    def testCommandLineAccess(self):
        assert self.result.exit_code == 0
        assert len(self.result.output) > 0
