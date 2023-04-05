import pytest

from askanna.core.dataclasses.run import ArtifactInfo, MetricList, VariableList
from askanna.sdk.run import RunSDK
from tests.utils import str_to_datetime


@pytest.mark.usefixtures("api_response")
class TestSDKRun:
    def test_run_list(self):
        run_sdk = RunSDK()
        result = run_sdk.list()

        assert len(result) == 1
        assert result[0].suuid == "1234-1234-1234-1234"

    def test_run_list_run_suuid(self):
        run_sdk = RunSDK()
        result = run_sdk.list(run_suuid_list=["1234-1234-1234-1234", "5678-5678-5678-5678"])

        assert len(result) == 1
        assert result[0].suuid == "1234-1234-1234-1234"

    def test_run_list_project(self):
        run_sdk = RunSDK()
        result = run_sdk.list(project_suuid="1234-1234-1234-1234")

        assert len(result) == 1
        assert result[0].suuid == "1234-1234-1234-1234"

    def test_run_get(self):
        run_sdk = RunSDK()
        result = run_sdk.get("1234-1234-1234-1234")

        assert result.suuid == "1234-1234-1234-1234"

    def test_run_status(self):
        run_sdk = RunSDK()
        result = run_sdk.status("1234-1234-1234-1234")

        assert result.suuid == "abcd-abcd-abcd-abcd"

    def test_run_change(self):
        run_sdk = RunSDK()
        result = run_sdk.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_run_delete(self):
        run_sdk = RunSDK()
        result = run_sdk.delete("1234-1234-1234-1234")

        assert result is True

    def test_run_metric(self, run_metric):
        run_sdk = RunSDK()
        result = run_sdk.get_metric("1234-1234-1234-1234")

        assert result is not None
        assert isinstance(result, MetricList)
        assert result[0].metric.name == run_metric["metric"]["name"]
        assert result[0].created_at == str_to_datetime(run_metric["created_at"])

    def test_run_variable(self, run_variable):
        run_sdk = RunSDK()
        result = run_sdk.get_variable("1234-1234-1234-1234")

        assert result is not None
        assert isinstance(result, VariableList)
        assert result[0].variable.name == run_variable["variable"]["name"]
        assert result[0].created_at == str_to_datetime(run_variable["created_at"])

    def test_run_artifiact_info(self, run_artifact_item):
        run_sdk = RunSDK()
        result = run_sdk.artifact_info("1234-1234-1234-1234")

        assert result is not None
        assert isinstance(result, ArtifactInfo)
        assert result.files is not None
        assert result.files[0].name == run_artifact_item["files"][0]["name"]
