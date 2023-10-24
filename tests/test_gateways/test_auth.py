import pytest

from askanna.core.dataclasses.base import User
from askanna.gateways.auth import AuthGateway


@pytest.mark.usefixtures("api_response", "user_detail")
class TestGatewayAuth:
    def test_auth_get_user_info(self, user_detail):
        auth_gateway = AuthGateway()
        result = auth_gateway.get_user_info()

        assert isinstance(result, User)
        assert result.suuid == user_detail["suuid"]
