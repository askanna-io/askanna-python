import unittest

from click.testing import CliRunner

from askanna.cli.run_utils.tool import cli_commands


class BaseCLItest(unittest.TestCase):
    def testCommandLineAccess(self):
        result = CliRunner().invoke(cli_commands, "--help")
        self.assertEqual(result.exit_code, 0)
        self.assertGreater(len(result.output), 0)
