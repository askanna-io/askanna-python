from datetime import datetime, timezone

from askanna.core.dataclasses.run import Run, RunStatus


def test_run(run_detail):
    run = Run.from_dict(run_detail.copy())

    assert run.suuid == run_detail["suuid"]
    assert run.name == run_detail["name"]
    assert run.description == run_detail["description"]
    assert run.created_by.name == run_detail["created_by"]["name"]
    assert run.created_at == datetime.strptime(run_detail["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert run.modified_at == datetime.strptime(run_detail["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert run.job.suuid == run_detail["job"]["suuid"]

    assert (
        str(run)
        == "Run summary: {'suuid': '1234-1234-1234-1234', 'name': '', 'status': 'finished', "
        + "'duration': 33, 'result': {'relation': 'result', 'suuid': '2TOk-YPPO-ughS-63u5', 'name': 'model.pkl', "
        + "'size': 758, 'extension': 'pkl', 'mime_type': 'application/octet-stream'}, 'metrics': 3, 'variables': 12}"
    )

    assert repr(run) == "Run(suuid='1234-1234-1234-1234', status='finished')"


def test_run_status(job_run_request):
    run_status = RunStatus.from_dict(job_run_request.copy())

    assert run_status.suuid == job_run_request["suuid"]
    assert run_status.status == job_run_request["status"]
    assert run_status.name == job_run_request["name"]
    assert run_status.next_url == job_run_request["next_url"]
    assert run_status.created_by.name == job_run_request["created_by"]["name"]
    assert run_status.job.suuid == job_run_request["job"]["suuid"]
    assert run_status.project.suuid == job_run_request["project"]["suuid"]
    assert run_status.workspace.suuid == job_run_request["workspace"]["suuid"]
    assert run_status.created_at == datetime.strptime(job_run_request["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert run_status.modified_at == datetime.strptime(
        job_run_request["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=timezone.utc)

    assert str(run_status) == "a run (abcd-abcd-abcd-abcd): queued"

    assert repr(run_status) == "RunStatus(suuid='abcd-abcd-abcd-abcd', status='queued')"


def test_run_status_no_name(job_run_request):
    job_run_request["name"] = None
    run_status = RunStatus.from_dict(job_run_request.copy())

    assert run_status.suuid == job_run_request["suuid"]
    assert run_status.status == job_run_request["status"]
    assert run_status.name == job_run_request["name"]
    assert run_status.next_url == job_run_request["next_url"]
    assert run_status.created_by.name == job_run_request["created_by"]["name"]
    assert run_status.job.suuid == job_run_request["job"]["suuid"]
    assert run_status.project.suuid == job_run_request["project"]["suuid"]
    assert run_status.workspace.suuid == job_run_request["workspace"]["suuid"]
    assert run_status.created_at == datetime.strptime(job_run_request["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert run_status.modified_at == datetime.strptime(
        job_run_request["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=timezone.utc)

    assert str(run_status) == "Run abcd-abcd-abcd-abcd: queued"

    assert repr(run_status) == "RunStatus(suuid='abcd-abcd-abcd-abcd', status='queued')"
