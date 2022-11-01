import pytest


@pytest.fixture
def job_detail() -> dict:
    return {
        "uuid": "8e79792f-cc67-4695-850f-5e00e5942d5b",
        "project": {
            "relation": "project",
            "name": "a project",
            "uuid": "47bd90d7-0061-4a51-9b15-0aaad5582d98",
            "short_uuid": "abcd-abcd-abcd-abcd",
        },
        "environment": "askanna/askanna-python:3-slim",
        "schedules": [],
        "notifications": {"all": {"email": []}, "error": {"email": []}},
        "created": "2022-10-17T06:53:04.148997Z",
        "modified": "2022-10-17T06:53:04.150201Z",
        "description": None,
        "name": "a job",
        "short_uuid": "1234-1234-1234-1234",
        "timezone": "UTC",
    }


@pytest.fixture
def job_with_schedule_detail() -> dict:
    return {
        "uuid": "fb4519ea-74c0-42a6-8534-e3c2f094d2b1",
        "project": {
            "relation": "project",
            "name": "a project",
            "uuid": "47bd90d7-0061-4a51-9b15-0aaad5582d98",
            "short_uuid": "abcd-abcd-abcd-abcd",
        },
        "environment": "askanna/python:3.7",
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
        "description": None,
        "name": "a scheduled job",
        "short_uuid": "5678-5678-5678-5678",
        "timezone": "UTC",
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
        "next": "https://api.askanna.eu/v1/job/?limit=1&offset=1",
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
