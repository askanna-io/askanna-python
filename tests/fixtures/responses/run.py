from pathlib import Path

import pytest


@pytest.fixture
def run_detail() -> dict:
    return {
        "suuid": "1234-1234-1234-1234",
        "name": "",
        "description": "",
        "status": "finished",
        "started": "2022-01-26T09:47:41.874998Z",
        "finished": "2022-01-26T09:48:15.766553Z",
        "duration": 33,
        "trigger": "WEBUI",
        "created_by": {
            "relation": "membership",
            "suuid": "7FzS-oPBG-BIi5-lTeL",
            "name": "Robbert",
            "job_title": "Founder AskAnna",
            "role": {"name": "Workspace Admin", "code": "WA"},
            "status": "active",
            "avatar": {
                "icon": "https://cdn-api.askanna.eu/files/avatars/ee78fc794bee886999ed5ffe3b68/avatar_3b68_icon.png",
                "small": "https://cdn-api.askanna.eu/files/avatars/ee78f80ee886999ed5ffe3b68/avatar_86999ed_small.png",
                "medium": "https://cdn-api.askanna.eu/files/avatars/ee7e8999ed5ffe3b68/avatar_ee78fc7f8b68_medium.png",
                "large": "https://cdn-api.askanna.eu/files/avatars/ee78fc7f80a94be899efffe3b68/avatar_e88e8_large.png",
            },
        },
        "package": {
            "relation": "package",
            "suuid": "3FqG-if1Z-Gd2s-uYvq",
            "name": "train-select-and-serve_f8cbd1bd38a544f1819b8e9b957e933c.zip",
        },
        "payload": None,
        "result": {
            "relation": "result",
            "suuid": "2TOk-YPPO-ughS-63u5",
            "name": "model.pkl",
            "size": 758,
            "extension": "pkl",
            "mime_type": "application/octet-stream",
        },
        "artifact": None,
        "metrics_meta": {
            "count": 3,
            "size": 512,
            "metric_names": [
                {"name": "mae", "type": "float", "count": 1},
                {"name": "r2", "type": "float", "count": 1},
                {"name": "rmse", "type": "float", "count": 1},
            ],
            "label_names": [],
        },
        "variables_meta": {
            "count": 12,
            "size": 2950,
            "variable_names": [
                {"name": "model", "type": "string", "count": 1},
                {"name": "l1_ratio", "type": "float", "count": 1},
                {"name": "alpha", "type": "float", "count": 1},
                {"name": "AA_PACKAGE_SUUID", "type": "string", "count": 1},
                {"name": "AA_PROJECT_SUUID", "type": "string", "count": 1},
                {"name": "AA_JOB_NAME", "type": "string", "count": 1},
                {"name": "AA_RUN_SUUID", "type": "string", "count": 1},
                {"name": "AA_REMOTE", "type": "string", "count": 1},
                {"name": "AA_TOKEN", "type": "string", "count": 1},
                {"name": "LANG", "type": "string", "count": 1},
                {"name": "LC_ALL", "type": "string", "count": 1},
                {"name": "TZ", "type": "string", "count": 1},
            ],
            "label_names": [
                {"name": "source", "type": "string"},
                {"name": "is_masked", "type": "tag"},
                {"name": "model", "type": "tag"},
                {"name": "parameter", "type": "tag"},
            ],
        },
        "log": {"relation": "log", "suuid": "6Uda-gBIN-HjDS-5KAj", "name": "log.json", "size": 13720, "lines": 88},
        "environment": {
            "name": "",
            "image": {
                "relation": "image",
                "suuid": "6UyU-pZUX-wyBo-PEAN",
                "name": "askanna/python:3.7-slim",
                "tag": "3.7-slim",
                "digest": "sha256:d3be9e9aa5873db96c83147eea63e7b534715875efe4f705d2b1394abbb5ab14",
            },
            "timezone": "UTC",
        },
        "job": {"relation": "jobdef", "suuid": "69Nk-vIwe-0YKU-uSRB", "name": "train-model"},
        "project": {"relation": "project", "suuid": "GZFT-EmyJ-CJ5V-kYKM", "name": "Train, select and serve"},
        "workspace": {"relation": "workspace", "suuid": "1S6G-K3fI-visU-LKac", "name": "Demo AskAnna"},
        "created": "2023-01-26T09:47:41.077335Z",
        "modified": "2023-01-26T09:48:15.774587Z",
    }


@pytest.fixture
def run_detail_no_metric_no_variable() -> dict:
    return {
        "suuid": "4321-4321-4321-4321",
        "name": "",
        "description": "",
        "status": "finished",
        "started": "2022-01-26T09:47:41.874998Z",
        "finished": "2022-01-26T09:48:15.766553Z",
        "duration": 33,
        "trigger": "WEBUI",
        "created_by": {
            "relation": "membership",
            "suuid": "7FzS-oPBG-BIi5-lTeL",
            "name": "Robbert",
            "job_title": "Founder AskAnna",
            "role": {"name": "Workspace Admin", "code": "WA"},
            "status": "active",
            "avatar": {
                "icon": "https://cdn-api.askanna.eu/files/avatars/ee78fc794bee886999ed5ffe3b68/avatar_3b68_icon.png",
                "small": "https://cdn-api.askanna.eu/files/avatars/ee78f80ee886999ed5ffe3b68/avatar_86999ed_small.png",
                "medium": "https://cdn-api.askanna.eu/files/avatars/ee7e8999ed5ffe3b68/avatar_ee78fc7f8b68_medium.png",
                "large": "https://cdn-api.askanna.eu/files/avatars/ee78fc7f80a94be899efffe3b68/avatar_e88e8_large.png",
            },
        },
        "package": {
            "relation": "package",
            "suuid": "3FqG-if1Z-Gd2s-uYvq",
            "name": "train-select-and-serve_f8cbd1bd38a544f1819b8e9b957e933c.zip",
        },
        "payload": None,
        "result": None,
        "artifact": None,
        "metrics_meta": {
            "count": 0,
            "size": 0,
            "metric_names": None,
            "label_names": None,
        },
        "variables_meta": {
            "count": 0,
            "size": 0,
            "variable_names": None,
            "label_names": None,
        },
        "log": {"relation": "log", "suuid": "6Uda-gBIN-HjDS-5KAj", "name": "log.json", "size": 13720, "lines": 88},
        "environment": {
            "name": "",
            "image": {
                "relation": "image",
                "suuid": "6UyU-pZUX-wyBo-PEAN",
                "name": "askanna/python:3.7-slim",
                "tag": "3.7-slim",
                "digest": "sha256:d3be9e9aa5873db96c83147eea63e7b534715875efe4f705d2b1394abbb5ab14",
            },
            "timezone": "UTC",
        },
        "job": {"relation": "jobdef", "suuid": "69Nk-vIwe-0YKU-uSRB", "name": "train-model"},
        "project": {"relation": "project", "suuid": "GZFT-EmyJ-CJ5V-kYKM", "name": "Train, select and serve"},
        "workspace": {"relation": "workspace", "suuid": "1S6G-K3fI-visU-LKac", "name": "Demo AskAnna"},
        "created": "2023-01-26T09:47:41.077335Z",
        "modified": "2023-01-26T09:48:15.774587Z",
    }


@pytest.fixture
def run_list(run_detail) -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [run_detail],
    }


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


@pytest.fixture
def run_log() -> dict:
    return {
        "count": 89,
        "next": "https://api.askanna.eu/v1/run/1234-1234-1234-1234/log/?limit=10&offset=10",
        "previous": None,
        "results": [
            [1, "2023-01-26T09:47:42.427272", "Preparing run environment"],
            [
                2,
                "2023-01-26T09:47:42.428665",
                "Getting image gitlab.askanna.io:4567/askanna/askanna-cli/review:changes-cursor-pagination-3.7-slim",
            ],
            [3, "2023-01-26T09:47:42.429156", "Check AskAnna requirements and if not available, try to install them"],
            [4, "2023-01-26T09:47:42.437785", "All AskAnna requirements are available"],
            [5, "2023-01-26T09:47:42.438332", ""],
            [6, "2023-01-26T09:47:45.108259183Z", "AskAnna CLI, version 0.20.0"],
            [7, "2023-01-26T09:47:45.238008736Z", ""],
            [8, "2023-01-26T09:47:45.241614127Z", "Loading code package into the run environment"],
            [9, "2023-01-26T09:47:46.130351965Z", "Finished loading code package"],
            [10, "2023-01-26T09:47:46.130415631Z", "Payload is not set"],
        ],
    }
