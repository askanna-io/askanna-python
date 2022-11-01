from pathlib import Path

import pytest


@pytest.fixture
def run_payload():
    return {"test_payload_key": "test_payload_value"}


@pytest.fixture
def run_manifest():
    file_path = "tests/fixtures/files/run_manifest.sh"

    with open(file_path) as f:
        content = f.read()

    return content


@pytest.fixture
def run_artifact_file() -> bytes:
    zip_file_path = Path("tests/fixtures/files/zip_file.zip")

    with zip_file_path.open("rb") as f:
        content = f.read()

    return content


@pytest.fixture
def run_artifact_list() -> list:
    return [
        {
            "uuid": "1ffeb3e8-6b4e-41e1-9565-a2256d8f7994",
            "project": {
                "relation": "project",
                "name": "Test project",
                "uuid": "95be337b-f09d-4527-9b06-69a27a7ce870",
                "short_uuid": "4YYm-HyoP-rfIs-mghs",
            },
            "created": "2022-08-23T07:22:58.778753Z",
            "modified": "2022-08-23T07:22:58.778794Z",
            "deleted": None,
            "short_uuid": "abcd-abcd-abcd-abcd",
            "size": 198,
            "count_dir": 0,
            "count_files": 1,
            "run": "8247df11-e2b4-478e-9ee4-a01609ba781f",
        }
    ]


@pytest.fixture
def run_artifact_list_not_found() -> list:
    return [
        {
            "uuid": "1ffeb3e8-6b4e-41e1-9565-a2256d8f7994",
            "project": {
                "relation": "project",
                "name": "Test project",
                "uuid": "95be337b-f09d-4527-9b06-69a27a7ce870",
                "short_uuid": "4YYm-HyoP-rfIs-mghs",
            },
            "created": "2022-08-23T07:22:58.778753Z",
            "modified": "2022-08-23T07:22:58.778794Z",
            "deleted": None,
            "short_uuid": "wxyz-wxyz-wxyz-wxyz",
            "size": 198,
            "count_dir": 0,
            "count_files": 1,
            "run": "8247df11-e2b4-478e-9ee4-a01609ba781f",
        }
    ]
