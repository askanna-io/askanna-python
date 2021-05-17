from .base import BaseCLItest, CliRunner, cli_commands


class TestCLIJob(BaseCLItest):
    """
    askanna job

    We expect to be able to list and change jobs
    """

    verb = "job"

    def testCommandJobBase(self):
        assert "job" in self.result.output
        self.assertIn("job", self.result.output)
        self.assertNotIn("noop", self.result.output)

    def testCommadJobChange(self):
        result = CliRunner().invoke(cli_commands, "job change --help")
        assert "change [OPTIONS]" in result.output

    def testCommadJobList(self):
        result = CliRunner().invoke(cli_commands, "job list --help")
        assert "list [OPTIONS]" in result.output
