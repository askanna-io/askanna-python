import unittest

from click.testing import CliRunner

from askanna.cli.tool import cli_commands


class BaseCLItest(unittest.TestCase):
    verb = ""

    def setUp(self):
        self.result = CliRunner().invoke(
            cli_commands,
            [
                "--help",
                self.verb,
            ],
        )

    def testCommandLineAccess(self):
        self.assertEqual(self.result.exit_code, 0)
        self.assertGreater(len(self.result.output), 0)
