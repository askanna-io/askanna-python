import unittest

from askanna.cli.run_utils import __main__


class TestCliMain(unittest.TestCase):
    def test_cli_import_main(self):

        self.assertTrue("cli" in dir(__main__))
