from .base import BaseCLItest


class TestCliLogin(BaseCLItest):
    """
    askanna login

    We expect a login prompt to appear to setup the authentication session
    """
    verb = "login"

    def testCommandLoginBase(self):
        assert "login" in self.result.output
        self.assertIn("login", self.result.output)
        self.assertNotIn("noop", self.result.output)
