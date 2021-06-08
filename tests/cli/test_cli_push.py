from .base import BaseCLItest


class TestCliPush(BaseCLItest):
    """
    askanna push

    We expect to initiate a push action of our code to the AskAnna server
    """
    verb = "push"

    def test_command_push_base(self):
        assert "push" in self.result.output
        self.assertIn("push", self.result.output)
        self.assertNotIn("noop", self.result.output)
