import pytest


@pytest.fixture
def job_detail() -> dict:
    return {
        "suuid": "1234-1234-1234-1234",
        "name": "a job",
        "description": None,
        "workspace": {
            "relation": "workspace",
            "suuid": "7aYw-rkCA-wdMo-1Gi6",
            "name": "a workspace",
        },
        "project": {
            "relation": "project",
            "suuid": "abcd-abcd-abcd-abcd",
            "name": "a project",
        },
        "environment": "askanna/askanna-python:3-slim",
        "timezone": "UTC",
        "schedules": None,
        "notifications": {"all": {"email": []}, "error": {"email": []}},
        "created": "2022-10-17T06:53:04.148997Z",
        "modified": "2022-10-17T06:53:04.150201Z",
    }


@pytest.fixture
def job_with_schedule_detail() -> dict:
    return {
        "suuid": "5678-5678-5678-5678",
        "name": "a scheduled job",
        "description": None,
        "workspace": {
            "relation": "workspace",
            "suuid": "7aYw-rkCA-wdMo-1Gi6",
            "name": "a workspace",
        },
        "project": {
            "relation": "project",
            "name": "a project",
            "suuid": "abcd-abcd-abcd-abcd",
        },
        "environment": "askanna/python:3.7",
        "timezone": "UTC",
        "schedules": [
            {
                "raw_definition": "{'weekday': 1, 'hour': 3, 'minute': 21}",
                "cron_definition": "21 3 * * 1",
                "cron_timezone": "UTC",
                "next_run": "2022-10-31T03:21:00Z",
                "last_run": "2022-10-24T03:21:00Z",
            }
        ],
        "notifications": {"all": {"email": ["notify@example.com"]}, "error": {"email": []}},
        "created": "2021-12-23T11:29:37.153209Z",
        "modified": "2022-06-21T07:08:10.858126Z",
    }


@pytest.fixture
def job_list(job_detail) -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [job_detail],
    }


@pytest.fixture
def job_list_limit(job_with_schedule_detail) -> dict:
    return {
        "count": 45,
        "next": "https://api.askanna.eu/v1/job/?cursor=567&page_size=1",
        "previous": None,
        "results": [job_with_schedule_detail],
    }


@pytest.fixture
def job_list_duplicate_job_name(job_detail) -> dict:
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [job_detail, job_detail],
    }


@pytest.fixture
def job_run_request() -> dict:
    return {
        "suuid": "abcd-abcd-abcd-abcd",
        "status": "queued",
        "name": "a run",
        "started": None,
        "finished": None,
        "duration": 0,
        "next_url": "https://api.askanna.eu/v1/run/5678-5678-5678-5678/status/",
        "created_by": {
            "relation": "membership",
            "suuid": "4bWd-sWHg-Xz4o-8ICi",
            "name": "Robbert",
            "job_title": "Founder AskAnna",
            "role": {"name": "Workspace Admin", "code": "WA"},
            "status": "active",
        },
        "job": {
            "relation": "job",
            "suuid": "1234-1234-1234-1234",
            "name": "a job",
        },
        "project": {
            "relation": "project",
            "suuid": "abcd-abcd-abcd-abcd",
            "name": "a project",
        },
        "workspace": {
            "relation": "workspace",
            "suuid": "7aYw-rkCA-wdMo-1Gi6",
            "name": "a workspace",
        },
        "created": "2022-10-17T06:53:04.148997Z",
        "modified": "2022-10-17T06:53:04.150201Z",
    }
