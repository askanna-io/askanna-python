import pytest

from askanna.core.utils.suuid import create_suuid
from tests.utils import faker


@pytest.fixture
def user_detail() -> dict:
    return {
        "suuid": create_suuid(),
        "name": faker.fake.name(),
        "email": faker.fake.email(),
        "is_active": faker.fake.boolean(),
        "date_joined": faker.date_time_str(),
        "last_login": faker.date_time_str(),
    }
