from askanna.core.utils import extract_push_target, get_config
from askanna.core.user import User


config = get_config(check_config=False)


class Config:
    """
    Configuration management for AskAnna CLI & SDK
    """

    @property
    def remote(self):
        return config.get("askanna", {}).get(
            "remote", "https://beta-api.askanna.eu/v1/"
        )

    @property
    def user(self):
        token = config.get("auth", {}).get("token")
        return User(token=token)

    @property
    def push_target(self):
        return config.get("push-target")

    @property
    def workspace_suuid(self):
        try:
            push_target = extract_push_target(self.push_target)
        except ValueError:
            # the push-target is not set, so don't bother reading it
            return None
        return push_target.get("workspace_suuid")

    @property
    def project_suuid(self):
        try:
            push_target = extract_push_target(self.push_target)
        except ValueError:
            # the push-target is not set, so don't bother reading it
            return None
        return push_target.get("project_suuid")
