import pytest


@pytest.fixture
def variable_detail() -> dict:
    return {
        "suuid": "1234-1234-1234-1234",
        "name": "test",
        "value": "test",
        "is_masked": False,
        "project": {
            "relation": "project",
            "suuid": "1234-1234-1234-1234",
            "name": "test project",
        },
        "workspace": {
            "relation": "workspace",
            "suuid": "1234-1234-1234-1234",
            "name": "test workspace",
        },
        "created": "2020-04-01T09:44:11.853000Z",
        "modified": "2022-09-19T08:47:40.214291Z",
    }


@pytest.fixture
def variable_list(variable_detail) -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [variable_detail],
    }


@pytest.fixture
def variable_list_limit(variable_detail) -> dict:
    return {
        "count": 8,
        "next": "https://api.askanna.eu/v1/variable/?cursor=567&page_size=1",
        "previous": None,
        "results": [
            variable_detail,
        ],
    }
