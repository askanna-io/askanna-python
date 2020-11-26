from askanna.cli.utils import get_config
from askanna.cli.core.user import User


class Config:
    """
    Configuration management for AskAnna CLI
    """

    def __init__(self, *args, **kwargs):
        self.config = get_config()
        self.user = self.user_from_config()

    @property
    def remote(self):
        return self.config.get("askanna", {}).get("remote", "https://api.askanna.eu/v1/")

    @property
    def auth(self):
        return self.config.get('auth', {})

    def user_from_config(self):
        """
        Try to read an auth token
        if that is the case configure a User instance with a token set
        """
        token = self.auth.get('token')
        return User(token=token)
