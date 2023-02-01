from askanna.config.utils import read_config_from_url
from askanna.core.dataclasses.base import User
from askanna.core.exceptions import GetError, PostError
from askanna.gateways.api_client import client


class AuthGateway:
    """Management of authentication in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def login(
        self,
        email: str,
        password: str,
        remote_url: str = "",
        ui_url: str = "",
        server: str = "default",
        update_config_file: bool = False,
    ) -> None:
        client.config.server.server = server

        if ui_url:
            if ui_url[-1] == "/":
                ui_url = ui_url[:-1]
            ui_config = read_config_from_url(f"{ui_url}/askanna-config.yml")
            try:
                ui_remote_url = ui_config["askanna-remote"]
            except KeyError as e:
                raise KeyError(f"The config file on the URL '{ui_url}' did not contain the key {e}")

            if remote_url and remote_url != ui_remote_url:
                raise ValueError("The remote URL does not match the remote URL configured on the frontend")

            client.config.server.ui = ui_url
            remote_url = ui_remote_url

        if remote_url:
            if remote_url[-1] == "/":
                remote_url = remote_url[:-1]
            if remote_url[-3:] == "/v1":
                remote_url = remote_url[:-3]
            client.config.server.remote = remote_url

        if client.config.server.remote == "https://beta-api.askanna.eu" and not ui_url:
            client.config.server.ui = "https://beta.askanna.eu"

        response = client.post(
            url=client.askanna_url.auth.login(),
            json={
                "email": email.strip(),
                "password": password.strip(),
            },
        )
        if response.status_code == 400:
            raise PostError(f"{response.status_code} - We could not log you in. Please check your credentials.")
        if response.status_code == 404:
            raise PostError(
                f"{response.status_code} - We could not log you in. Please check the url or remote you provided."
            )
        if response.status_code != 200:
            raise PostError(f"{response.status_code} - We could not log you in: {response.reason}")

        client.config.server.token = str(response.json().get("key"))
        client.update_session()

        if update_config_file:
            client.config.server.save_server_to_config_file()

    def get_user_info(self) -> User:
        url = client.askanna_url.auth.user()
        response = client.get(url)

        if response.status_code == 401:
            raise GetError(
                "The provided token is not valid. Via `askanna logout` you can remove the token "
                "and via `askanna login` you can set a new token."
            )
        if response.status_code != 200:
            raise GetError(
                "{} - We could not connect to AskAnna. More info:\n" "{}".format(response.status_code, response.reason)
            )

        return User(**response.json())
