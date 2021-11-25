import requests

from askanna.core.exceptions import ConnectionError


class Session:
    def __init__(self, headers=None, *args, **kwargs):
        self.session = requests.Session()

        if headers:
            self.session.headers.update(headers)

    def _connection_error_message(self, url, error):
        connection_error_message_base = 'Something went wrong. Please check whether the URL is an AskAnna backend.'
        return f'{connection_error_message_base}\n    URL:    {url}\n    Error: {error}'

    def get(self, url, **kwargs):
        try:
            return self.session.get(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def head(self, url, **kwargs):
        try:
            return self.session.head(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def patch(self, url, **kwargs):
        try:
            return self.session.patch(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def put(self, url, **kwargs):
        try:
            return self.session.put(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def post(self, url, **kwargs):
        try:
            return self.session.post(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def create(self, url, **kwargs):
        try:
            return self.post(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def delete(self, url, **kwargs):
        try:
            return self.session.delete(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))
