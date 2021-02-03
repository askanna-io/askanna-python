from askanna.core import client, exceptions
from askanna.core.dataclasses import User
from askanna.core.utils import store_config, CONFIG_FILE_ASKANNA


class AuthGateway:
    """
    Authentication management for AskAnna CLI & SDK
    """

    def __init__(self):
        self.base_url = client.config.remote.replace("v1/", '')

    def login(self, email: str, password: str, remote: str = None, update_config_file: bool = False) -> str:
        if remote:
            self.base_url = remote.replace("v1/", '') or self.base_url

        url = "{remote}rest-auth/login/".format(remote=self.base_url)
        r = client.post(url, json={
            'username': email.strip(),
            'password': password.strip()
            })

        if r.status_code == 400:
            raise exceptions.PostError("{} - We could not log you in. Please check your credentials."
                                       .format(r.status_code))
        if r.status_code == 404:
            raise exceptions.PostError("{} - We could not log you in. Please check the remote you provided."
                                       .format(r.status_code))
        elif r.status_code != 200:
            raise exceptions.PostError("{} - We could not log you in: {}".format(r.status_code, r.reason))

        token = str(r.json().get('key'))
        client.config.user.token = token

        if update_config_file:
            if remote:
                new_config = {
                    'askanna': {
                        'remote': remote
                        },
                    'auth': {
                        'token': token
                        }
                    }
            else:
                new_config = {
                    'auth': {
                        'token': token
                        }
                    }
            config = store_config(new_config)
            with open(CONFIG_FILE_ASKANNA, "w") as fd:
                fd.write(config)

        return token

    def get_user_info(self) -> User:
        url = "{remote}rest-auth/user".format(remote=self.base_url)

        r = client.get(url)

        if r.status_code == 200:
            return User(**r.json())
        elif r.status_code == 401:
            raise exceptions.GetError("The provided token is not valid. Via `askanna logout` you can remove the token "
                                      "and via `askanna login` you can set a new token.")
        else:
            raise exceptions.GetError("{} - We could not connect to AskAnna. More info:\n"
                                      "{}".format(r.status_code, r.reason))
