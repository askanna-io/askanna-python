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
def package_detail_for_list() -> dict:
    return {
        "suuid": "68s4-wjJ7-7Omp-2UOf",
        "workspace": {
            "relation": "workspace",
            "suuid": "7aYw-rkCA-wdMo-1Gi6",
            "name": "a workspace",
        },
        "project": {
            "relation": "project",
            "suuid": "71cZ-OfBp-Q2jC-DbRP",
            "name": "a project",
        },
        "created_by": {
            "relation": "membership",
            "suuid": "4bWd-sWHg-Xz4o-8ICi",
            "name": "Robbert",
            "job_title": "Founder AskAnna",
            "role": {"name": "Workspace Admin", "code": "WA"},
            "status": "active",
        },
        "created": "2020-10-29T12:26:29.850420Z",
        "modified": "2021-01-11T15:52:53.844154Z",
        "name": "askanna-hello.zip",
        "description": "askanna-hello.zip",
        "filename": "513_askanna-hello.zip",
        "size": 513,
    }


@pytest.fixture
def package_list(package_detail_for_list) -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [package_detail_for_list],
    }


@pytest.fixture
def package_list_limit(package_detail_for_list) -> dict:
    return {
        "count": 8,
        "next": f"{askanna_url.package.package_list()}?limit=1&offset=1",
        "previous": None,
        "results": [package_detail_for_list],
    }


@pytest.fixture
def package_list_limit_empty() -> dict:
    return {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }
