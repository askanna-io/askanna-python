from .base import BaseCLItest, CliRunner, cli_commands


class TestCLIJob(BaseCLItest):
    """
    askanna job

    We expect to be able to list and change jobs
    """

    verb = "workspace"

    def testCommandWorkspaceBase(self):
        assert "workspace" in self.result.output
        self.assertIn("workspace", self.result.output)
        self.assertNotIn("noop", self.result.output)

    def testCommadWorkspaceChange(self):
        result = CliRunner().invoke(cli_commands, "workspace change --help")
        assert "change [OPTIONS]" in result.output

    def testCommadWorkspaceList(self):
        result = CliRunner().invoke(cli_commands, "workspace list --help")
        assert "list [OPTIONS]" in result.output

    def testCommadWorkspaceCreate(self):
        result = CliRunner().invoke(cli_commands, "workspace create --help")
        assert "create [OPTIONS]" in result.output

    def testCommadWorkspaceRemove(self):
        result = CliRunner().invoke(cli_commands, "workspace remove --help")
        assert "remove [OPTIONS]" in result.output
