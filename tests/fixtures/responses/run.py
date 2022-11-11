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
            "suuid": "abcd-abcd-abcd-abcd",
            "workspace": {
                "relation": "workspace",
                "suuid": "7aYw-rkCA-wdMo-1Gi6",
                "name": "a workspace",
            },
            "project": {
                "relation": "project",
                "suuid": "4YYm-HyoP-rfIs-mghs",
                "name": "a project",
            },
            "job": {
                "relation": "job",
                "suuid": "HyoP-rfIs-mghs-4YYm",
                "name": "a job",
            },
            "run": {
                "relation": "run",
                "suuid": "HyoP-rfIs-mghs-4YYm",
                "name": None,
            },
            "size": 198,
            "count_dir": 0,
            "count_files": 1,
            "created": "2022-08-23T07:22:58.778753Z",
            "modified": "2022-08-23T07:22:58.778794Z",
        }
    ]


@pytest.fixture
def run_artifact_list_not_found() -> list:
    return [
        {
            "suuid": "wxyz-wxyz-wxyz-wxyz",
            "workspace": {
                "relation": "workspace",
                "suuid": "7aYw-rkCA-wdMo-1Gi6",
                "name": "a workspace",
            },
            "project": {
                "relation": "project",
                "suuid": "4YYm-HyoP-rfIs-mghs",
                "name": "a project",
            },
            "job": {
                "relation": "job",
                "suuid": "HyoP-rfIs-mghs-4YYm",
                "name": "a job",
            },
            "run": {
                "relation": "run",
                "suuid": "HyoP-rfIs-mghs-4YYm",
                "name": None,
            },
            "size": 198,
            "count_dir": 0,
            "count_files": 1,
            "created": "2022-08-23T07:22:58.778753Z",
            "modified": "2022-08-23T07:22:58.778794Z",
        }
    ]
