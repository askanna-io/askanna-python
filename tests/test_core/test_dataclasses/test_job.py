from datetime import datetime, timezone

from askanna.core.dataclasses.job import Job, Payload


def test_job(job_detail):
    job = Job.from_dict(job_detail.copy())

    assert job.suuid == job_detail["suuid"]
    assert job.name == job_detail["name"]
    assert job.description == job_detail["description"]
    assert job.environment == job_detail["environment"]
    assert job.timezone == job_detail["timezone"]
    assert job.schedules == job_detail["schedules"]
    assert job.notifications == job_detail["notifications"]
    assert job.project.suuid == job_detail["project"]["suuid"]
    assert job.workspace.suuid == job_detail["workspace"]["suuid"]
    assert job.created_at == datetime.strptime(job_detail["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert job.modified_at == datetime.strptime(job_detail["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )


def test_payload(run_payload_detail):
    payload = Payload.from_dict(run_payload_detail.copy())

    assert payload.suuid == run_payload_detail["suuid"]
    assert payload.size == run_payload_detail["size"]
    assert payload.lines == run_payload_detail["lines"]
    assert payload.created_at == datetime.strptime(run_payload_detail["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert payload.modified_at == datetime.strptime(
        run_payload_detail["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=timezone.utc)

    assert str(payload) == "Payload: 1234-1234-1234-1234 (184 bytes & 30 lines)"
