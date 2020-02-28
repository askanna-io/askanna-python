from .base import BaseCLItest


class TestCliLogout(BaseCLItest):
    """
    askanna logout

    We expect to logout the user (when authenicated)
    """
    verb = "logout"

    def testCommandLoginBase(self):
        assert "logout" in self.result.output
        self.assertIn("logout", self.result.output)
        self.assertNotIn("noop", self.result.output)
