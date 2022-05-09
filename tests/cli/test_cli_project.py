from .base import BaseCLItest, CliRunner, cli_commands


class TestCLIJob(BaseCLItest):
    """
    askanna job

    We expect to be able to list and change jobs
    """

    verb = "project"

    def testCommandProjectBase(self):
        assert "project" in self.result.output
        self.assertIn("project", self.result.output)
        self.assertNotIn("noop", self.result.output)

    def testCommadProjectChange(self):
        result = CliRunner().invoke(cli_commands, "project change --help")
        assert "change [OPTIONS]" in result.output

    def testCommadProjectList(self):
        result = CliRunner().invoke(cli_commands, "project list --help")
        assert "list [OPTIONS]" in result.output
