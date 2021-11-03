from askanna.core.apiclient import client
from askanna.core.dataclasses import User
from askanna.core.exceptions import GetError, PostError


class AuthGateway:
    """
    Authentication management for AskAnna CLI & SDK
    """

    def __init__(self):
        self.base_url = client.base_url.replace("/v1/", "")

    def login(
        self,
        email: str,
        password: str,
        remote: str = None,
        server: str = "default",
        update_config_file: bool = False,
    ) -> None:
        client.config.server.server = server

        if remote:
            self.base_url = remote.replace("/v1/", "")
            client.config.server.remote = self.base_url

        if self.base_url == "https://beta-api.askanna.eu":
            client.config.server.ui = "https://beta.askanna.eu"
        else:
            client.config.server.ui = ""

        url = "{remote}/rest-auth/login/".format(remote=self.base_url)
        r = client.post(
            url, json={"username": email.strip(), "password": password.strip()}
        )

        if r.status_code == 400:
            raise PostError(
                "{} - We could not log you in. Please check your credentials.".format(
                    r.status_code
                )
            )
        if r.status_code == 404:
            raise PostError(
                "{} - We could not log you in. Please check the remote you provided.".format(
                    r.status_code
                )
            )
        if r.status_code != 200:
            raise PostError(
                "{} - We could not log you in: {}".format(r.status_code, r.reason)
            )

        client.config.server.token = str(r.json().get("key"))

        if update_config_file:
            client.config.server.save_server_to_config_file()

    def get_user_info(self) -> User:
        url = f"{self.base_url}/rest-auth/user/"
        r = client.get(url)

        if r.status_code == 200:
            return User(**r.json())
        elif r.status_code == 401:
            raise GetError(
                "The provided token is not valid. Via `askanna logout` you can remove the token "
                "and via `askanna login` you can set a new token."
            )
        else:
            raise GetError(
                "{} - We could not connect to AskAnna. More info:\n"
                "{}".format(r.status_code, r.reason)
            )
