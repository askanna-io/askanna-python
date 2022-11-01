from pathlib import Path

import pytest

from askanna.config.api_url import askanna_url


@pytest.fixture
def package_zip_file() -> bytes:
    zip_file_path = Path("tests/fixtures/files/zip_file.zip")

    with zip_file_path.open("rb") as f:
        content = f.read()

    return content


@pytest.fixture
def package_list() -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "uuid": "c9d7cd78-2111-4502-99ef-b26e47847f00",
                "created_by": {
                    "relation": "membership",
                    "name": "Robbert",
                    "uuid": "9750876a-5b34-403d-a9f1-9e9862368416",
                    "short_uuid": "4bWd-sWHg-Xz4o-8ICi",
                    "job_title": "Founder AskAnna",
                    "role": {"name": "Workspace Admin", "code": "WA"},
                    "status": "accepted",
                },
                "project": {
                    "name": "Hello AskAnna",
                    "uuid": "e6db8d69-d762-4e3b-b4ed-a57a256f91dc",
                    "short_uuid": "71cZ-OfBp-Q2jC-DbRP",
                },
                "filename": "513_askanna-hello.zip",
                "created": "2020-10-29T12:26:29.850420Z",
                "modified": "2021-01-11T15:52:53.844154Z",
                "deleted": None,
                "description": "askanna-hello.zip",
                "name": "askanna-hello.zip",
                "short_uuid": "68s4-wjJ7-7Omp-2UOf",
                "original_filename": "513_askanna-hello.zip",
                "size": 513,
                "finished": "2020-10-29T12:26:30.074319Z",
                "member": "9750876a-5b34-403d-a9f1-9e9862368416",
            },
        ],
    }


@pytest.fixture
def package_list_limit() -> dict:
    return {
        "count": 8,
        "next": f"{askanna_url.package.package_list()}?limit=1&offset=1",
        "previous": None,
        "results": [
            {
                "uuid": "c9d7cd78-2111-4502-99ef-b26e47847f00",
                "created_by": {
                    "relation": "membership",
                    "name": "Robbert",
                    "uuid": "9750876a-5b34-403d-a9f1-9e9862368416",
                    "short_uuid": "4bWd-sWHg-Xz4o-8ICi",
                    "job_title": "Founder AskAnna",
                    "role": {"name": "Workspace Admin", "code": "WA"},
                    "status": "accepted",
                },
                "project": {
                    "name": "Hello AskAnna",
                    "uuid": "e6db8d69-d762-4e3b-b4ed-a57a256f91dc",
                    "short_uuid": "71cZ-OfBp-Q2jC-DbRP",
                },
                "filename": "513_askanna-hello.zip",
                "created": "2020-10-29T12:26:29.850420Z",
                "modified": "2021-01-11T15:52:53.844154Z",
                "deleted": None,
                "description": "askanna-hello.zip",
                "name": "askanna-hello.zip",
                "short_uuid": "68s4-wjJ7-7Omp-2UOf",
                "original_filename": "513_askanna-hello.zip",
                "size": 513,
                "finished": "2020-10-29T12:26:30.074319Z",
                "member": "9750876a-5b34-403d-a9f1-9e9862368416",
            }
        ],
    }


@pytest.fixture
def package_list_limit_empty() -> dict:
    return {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }
