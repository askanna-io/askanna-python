from datetime import datetime

import pytest

from askanna.core.dataclasses.base import Label
from askanna.core.dataclasses.run import (
    ArtifactFile,
    ArtifactFileList,
    ArtifactInfo,
    MetricList,
    MetricObject,
    Run,
    RunStatus,
    Variable,
    VariableList,
    VariableObject,
)
from askanna.core.exceptions import MultipleObjectsReturnedError
from tests.utils import str_to_datetime


def test_run(run_detail):
    run = Run.from_dict(run_detail.copy())

    assert run.suuid == run_detail["suuid"]
    assert run.name == run_detail["name"]
    assert run.description == run_detail["description"]
    assert run.created_by.name == run_detail["created_by"]["name"]
    assert run.created_at == str_to_datetime(run_detail["created_at"])
    assert run.modified_at == str_to_datetime(run_detail["modified_at"])
    assert run.job.suuid == run_detail["job"]["suuid"]

    assert (
        str(run)
        == "Run summary: {'suuid': '1234-1234-1234-1234', 'name': '', 'status': 'finished', "
        + "'duration': 33, 'result': {'relation': 'result', 'suuid': '2TOk-YPPO-ughS-63u5', 'name': 'model.pkl', "
        + "'size': 758, 'extension': 'pkl', 'mime_type': 'application/octet-stream'}, 'metrics': 3, 'variables': 12}"
    )

    assert repr(run) == "Run(suuid='1234-1234-1234-1234', status='finished')"


def test_run_without_started_and_finished_date(run_detail):
    run_without_dates = run_detail.copy()
    run_without_dates["started_at"] = None
    run_without_dates["finished_at"] = None

    run = Run.from_dict(run_without_dates)

    assert run.suuid == run_detail["suuid"]
    assert run.started_at is None
    assert run.finished_at is None


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
    assert run_status.created_at == str_to_datetime(job_run_request["created_at"])
    assert run_status.modified_at == str_to_datetime(job_run_request["modified_at"])

    assert str(run_status) == "a run (abcd-abcd-abcd-abcd): queued"

    assert repr(run_status) == "RunStatus(suuid='abcd-abcd-abcd-abcd', status='queued')"


def test_run_status_without_started_and_finished_date(job_run_request):
    run_status_without_dates = job_run_request.copy()
    run_status_without_dates["started_at"] = None
    run_status_without_dates["finished_at"] = None

    run_status = RunStatus.from_dict(run_status_without_dates)

    assert run_status.suuid == job_run_request["suuid"]
    assert run_status.started_at is None
    assert run_status.finished_at is None


def test_run_status_with_started_and_finished_date(job_run_request):
    run_status_without_dates = job_run_request.copy()
    run_status_without_dates["started_at"] = "2023-03-23T14:02:00.000000Z"
    run_status_without_dates["finished_at"] = "2023-03-23T14:03:00.000000Z"

    run_status = RunStatus.from_dict(run_status_without_dates)

    assert run_status.suuid == job_run_request["suuid"]
    assert run_status.started_at == str_to_datetime("2023-03-23T14:02:00.000000Z")
    assert run_status.finished_at == str_to_datetime("2023-03-23T14:03:00.000000Z")


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
    assert run_status.created_at == str_to_datetime(job_run_request["created_at"])
    assert run_status.modified_at == str_to_datetime(job_run_request["modified_at"])

    assert str(run_status) == "Run abcd-abcd-abcd-abcd: queued"

    assert repr(run_status) == "RunStatus(suuid='abcd-abcd-abcd-abcd', status='queued')"


def test_variable_object_with_created_at():
    variable = Variable(name="test", value="test", type="string")
    label = Label(name="test", value=None, type="tag")
    created_at = datetime.now()

    variable_object = VariableObject(variable=variable, label=[label], created_at=created_at)

    assert variable_object.created_at == created_at


def test_variable_object_fom_dict(run_variable):
    variable_object = VariableObject.from_dict(run_variable)

    assert variable_object.variable.name == run_variable["variable"]["name"]
    assert variable_object.run_suuid == run_variable["run_suuid"]


def test_variable_list(run_variable):
    variable_object = VariableObject.from_dict(run_variable)
    variable_list = VariableList(variables=[variable_object])

    assert len(variable_list) == 1

    for variable in variable_list:
        assert variable.variable.name == run_variable["variable"]["name"]
        assert variable.run_suuid == run_variable["run_suuid"]

    assert variable_list[0].variable.name == run_variable["variable"]["name"]

    assert variable_list.get(run_variable["variable"]["name"]).variable.name == run_variable["variable"]["name"]

    assert variable_list.get("not_exist") is None

    variable_list = VariableList(variables=[variable_object, variable_object])

    with pytest.raises(MultipleObjectsReturnedError):
        variable_list.get(run_variable["variable"]["name"])

    assert len(variable_list.filter(run_variable["variable"]["name"])) == 2


def test_metric_object_fom_dict(run_metric):
    metric_object = MetricObject.from_dict(run_metric)

    assert metric_object.metric.name == run_metric["metric"]["name"]
    assert metric_object.run_suuid == run_metric["run_suuid"]


def test_metric_list(run_metric):
    metric_object = MetricObject.from_dict(run_metric)
    metric_list = MetricList(metrics=[metric_object])

    assert len(metric_list) == 1

    for metric in metric_list:
        assert metric.metric.name == run_metric["metric"]["name"]
        assert metric.run_suuid == run_metric["run_suuid"]

    assert metric_list[0].metric.name == run_metric["metric"]["name"]

    assert metric_list.get(run_metric["metric"]["name"]).metric.name == run_metric["metric"]["name"]
    assert metric_list.get("not_exist") is None

    metric_list = MetricList(metrics=[metric_object, metric_object])

    with pytest.raises(MultipleObjectsReturnedError):
        metric_list.get(run_metric["metric"]["name"])

    assert len(metric_list.filter(run_metric["metric"]["name"])) == 2


def test_artifact_file(run_artifact_file_dict):
    artifact_file = ArtifactFile.from_dict(run_artifact_file_dict.copy())

    assert artifact_file.name == "test.zip"
    assert artifact_file.size == 1234
    assert artifact_file.path == "./demo"
    assert artifact_file.type == "zip"


def test_artifact_file_list(run_artifact_file_dict):
    artifact_file = ArtifactFile.from_dict(run_artifact_file_dict.copy())
    artifact_file_list = ArtifactFileList(files=[artifact_file])

    assert len(artifact_file_list) == 1
    assert artifact_file_list[0].name == "test.zip"

    for file in artifact_file_list:
        assert file.name == "test.zip"
        assert file.size == 1234
        assert file.path == "./demo"
        assert file.type == "zip"


def test_artifact_info(run_artifact_item):
    artifact_info = ArtifactInfo.from_dict(run_artifact_item.copy())

    assert artifact_info.suuid == "abcd-abcd-abcd-abcd"
