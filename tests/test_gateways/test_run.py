from pathlib import Path

import pytest

from askanna.core.dataclasses.run import (
    ArtifactInfo,
    MetricList,
    MetricObject,
    VariableList,
    VariableObject,
)
from askanna.core.exceptions import DeleteError, GetError, PatchError, PutError
from askanna.gateways.run import RunGateway
from tests.utils import str_to_datetime


@pytest.mark.usefixtures("api_response")
class TestGatewayRun:
    def test_run_list(self):
        run_gateway = RunGateway()
        result = run_gateway.list()

        assert len(result.runs) == 1
        assert result.runs[0].suuid == "1234-1234-1234-1234"

    def test_run_list_cursor(self):
        run_gateway = RunGateway()
        result = run_gateway.list(page_size=1, cursor="123")

        assert len(result.runs) == 1
        assert result.runs[0].suuid == "1234-1234-1234-1234"

    def test_run_list_error(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.list(cursor="999")

        assert (
            "500 - Something went wrong while retrieving the run list:\n  {'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_run_list_error_2(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.list(cursor="888")

        assert "503 - Something went wrong while retrieving the run list" in e.value.args[0]

    def test_run_list_page_size_validation(self):
        run_gateway = RunGateway()

        with pytest.raises(ValueError) as exc:
            run_gateway.list(page_size=0)
        assert "page_size must be a positive integer" in exc.value.args[0]

        with pytest.raises(ValueError) as exc:
            run_gateway.list(page_size=-1)
        assert "page_size must be a positive integer" in exc.value.args[0]

        with pytest.raises(ValueError) as exc:
            run_gateway.list(page_size=True)
        assert "page_size must be a positive integer" in exc.value.args[0]

        with pytest.raises(ValueError) as exc:
            run_gateway.list(page_size="test")  # type: ignore
        assert "page_size must be a positive integer" in exc.value.args[0]

        run = run_gateway.list(page_size=1)
        assert len(run.runs) == 1

    def test_run_list_run_suuid(self):
        run_gateway = RunGateway()
        result = run_gateway.list(run_suuid_list=["1234-1234-1234-1234", "5678-5678-5678-5678"])

        assert len(result.runs) == 1
        assert result.runs[0].suuid == "1234-1234-1234-1234"

    def test_run_list_project(self):
        run_gateway = RunGateway()
        result = run_gateway.list(project_suuid="1234-1234-1234-1234")

        assert len(result.runs) == 1
        assert result.runs[0].suuid == "1234-1234-1234-1234"

    def test_run_detail(self):
        run_gateway = RunGateway()
        result = run_gateway.detail("1234-1234-1234-1234")

        assert result.suuid == "1234-1234-1234-1234"

    def test_run_detail_not_found(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.detail("7890-7890-7890-7890")

        assert "404 - The run SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_run_detail_error(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.detail("0987-0987-0987-0987")

        assert (
            "500 - Something went wrong while retrieving run SUUID '0987-0987-0987-0987': "
            + "{'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_run_status(self):
        run_gateway = RunGateway()
        result = run_gateway.status("1234-1234-1234-1234")

        assert result.suuid == "abcd-abcd-abcd-abcd"

    def test_run_status_404(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.status("7890-7890-7890-7890")

        assert "404 - The run SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_run_status_500(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.status("0987-0987-0987-0987")

        assert (
            "500 - Something went wrong while retrieving the status of run SUUID '0987-0987-0987-0987': "
            + "{'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_run_change_no_changes(self):
        run_gateway = RunGateway()
        with pytest.raises(ValueError) as e:
            run_gateway.change("1234-1234-1234-1234")

        assert "At least one of the parameters 'name' or 'description' must be set" in e.value.args[0]

    def test_run_change(self):
        run_gateway = RunGateway()
        result = run_gateway.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_run_change_error(self):
        run_gateway = RunGateway()
        with pytest.raises(PatchError) as e:
            run_gateway.change("0987-0987-0987-0987", name="new name")

        assert "500 - Something went wrong while updating the run SUUID '0987-0987-0987-0987'" in e.value.args[0]

    def test_run_delete(self):
        run_gateway = RunGateway()
        result = run_gateway.delete("1234-1234-1234-1234")

        assert result is True

    def test_run_delete_not_found(self):
        run_gateway = RunGateway()
        with pytest.raises(DeleteError) as e:
            run_gateway.delete("7890-7890-7890-7890")

        assert "404 - The run SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_run_delete_error(self):
        run_gateway = RunGateway()
        with pytest.raises(DeleteError) as e:
            run_gateway.delete("0987-0987-0987-0987")

        assert "500 - Something went wrong while deleting the run SUUID '0987-0987-0987-0987'" in e.value.args[0]

    def test_run_manifest(self, run_manifest):
        run_gateway = RunGateway()
        result = run_gateway.manifest("1234-1234-1234-1234")

        assert result is not None
        assert result.decode() == run_manifest

    def test_run_manifest_404(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.manifest("wxyz-wxyz-wxyz-wxyz")

        assert "404 - The manifest for run SUUID 'wxyz-wxyz-wxyz-wxyz' was not found" in e.value.args[0]

    def test_run_manifest_not_200_not_404(self):
        run_gateway = RunGateway()
        with pytest.raises(GetError) as e:
            run_gateway.manifest("zyxw-zyxw-zyxw-zyxw")

        assert (
            "500 - Something went wrong while retrieving the manifest for run SUUID 'zyxw-zyxw-zyxw-zyxw'"
            in e.value.args[0]
        )

    def test_run_manifest_output_path(self, temp_dir, run_manifest):
        run_gateway = RunGateway()
        run_manifest_path = temp_dir + "/run-manifest-1234.sh"
        result = run_gateway.manifest("1234-1234-1234-1234", run_manifest_path)

        assert result is None
        assert Path(run_manifest_path).exists()
        assert Path(run_manifest_path).is_file()
        assert Path(run_manifest_path).read_text() == run_manifest

    def test_run_manifest_output_path_404(self, temp_dir):
        run_gateway = RunGateway()
        run_manifest_path = temp_dir + "/run-manifest-1234.sh"
        with pytest.raises(GetError) as e:
            run_gateway.manifest("wxyz-wxyz-wxyz-wxyz", run_manifest_path)

        assert "404 - The manifest for run SUUID 'wxyz-wxyz-wxyz-wxyz' was not found" in e.value.args[0]

    def test_run_manifest_output_path_not_200_not_404(self, temp_dir):
        run_gateway = RunGateway()
        run_manifest_path = temp_dir + "/run-manifest-1234.sh"
        with pytest.raises(GetError) as e:
            run_gateway.manifest("zyxw-zyxw-zyxw-zyxw", run_manifest_path)

        assert (
            "500 - Something went wrong while retrieving the manifest for run SUUID 'zyxw-zyxw-zyxw-zyxw'"
            in e.value.args[0]
        )

    def test_run_metric(self, run_metric):
        run_gateway = RunGateway()
        result = run_gateway.metric("1234-1234-1234-1234")

        assert result is not None
        assert isinstance(result, MetricList)
        assert result[0].metric.name == run_metric["metric"]["name"]
        assert result[0].created_at == str_to_datetime(run_metric["created_at"])

    def test_run_metric_404(self):
        run_gateway = RunGateway()

        with pytest.raises(GetError) as e:
            run_gateway.metric("wxyz-wxyz-wxyz-wxyz")

        assert "404 - The run SUUID 'wxyz-wxyz-wxyz-wxyz' was not found" in e.value.args[0]

    def test_run_metric_500(self):
        run_gateway = RunGateway()

        with pytest.raises(GetError) as e:
            run_gateway.metric("zyxw-zyxw-zyxw-zyxw")

        assert (
            "500 - Something went wrong while retrieving the metrics of run SUUID 'zyxw-zyxw-zyxw-zyxw'"
            in e.value.args[0]
        )

    def test_run_metric_update(self, run_metric):
        run_gateway = RunGateway()
        metric_object = MetricObject.from_dict(run_metric)
        metric_list = MetricList(metrics=[metric_object])

        assert run_gateway.metric_update("1234-1234-1234-1234", metric_list) is None

    def test_run_metric_update_404(self, run_metric):
        run_gateway = RunGateway()
        metric_object = MetricObject.from_dict(run_metric)
        metric_list = MetricList(metrics=[metric_object])

        with pytest.raises(PutError) as exc:
            run_gateway.metric_update("wxyz-wxyz-wxyz-wxyz", metric_list)

        assert "404 - The run SUUID 'wxyz-wxyz-wxyz-wxyz' was not found" in exc.value.args[0]

    def test_run_metric_update_500(self, run_metric):
        run_gateway = RunGateway()
        metric_object = MetricObject.from_dict(run_metric)
        metric_list = MetricList(metrics=[metric_object])

        with pytest.raises(PutError) as exc:
            run_gateway.metric_update("zyxw-zyxw-zyxw-zyxw", metric_list)

        assert (
            "500 - Something went wrong while updating metrics of run SUUID 'zyxw-zyxw-zyxw-zyxw'" in exc.value.args[0]
        )

    def test_run_variable_update(self, run_variable):
        run_gateway = RunGateway()
        variable_object = VariableObject.from_dict(run_variable)
        variable_list = VariableList(variables=[variable_object])

        assert run_gateway.variable_update("1234-1234-1234-1234", variable_list) is None

    def test_run_variable_update_404(self, run_variable):
        run_gateway = RunGateway()
        variable_object = VariableObject.from_dict(run_variable)
        variable_list = VariableList(variables=[variable_object])

        with pytest.raises(PatchError) as e:
            run_gateway.variable_update("wxyz-wxyz-wxyz-wxyz", variable_list)

        assert "404 - The run SUUID 'wxyz-wxyz-wxyz-wxyz' was not found" in e.value.args[0]

    def test_run_variable_update_500(self, run_variable):
        run_gateway = RunGateway()
        variable_object = VariableObject.from_dict(run_variable)
        variable_list = VariableList(variables=[variable_object])

        with pytest.raises(PatchError) as e:
            run_gateway.variable_update("zyxw-zyxw-zyxw-zyxw", variable_list)

        assert (
            "500 - Something went wrong while updating variables of run SUUID 'zyxw-zyxw-zyxw-zyxw'" in e.value.args[0]
        )

    def test_run_artifiact_info(self, run_artifact_item):
        run_gateway = RunGateway()
        result = run_gateway.artifact_info("1234-1234-1234-1234", "abcd-abcd-abcd-abcd")

        assert result is not None
        assert isinstance(result, ArtifactInfo)
        assert result.files is not None
        assert result.files[0].name == run_artifact_item["files"][0]["name"]

    def test_run_artifiact_info_404(self):
        run_gateway = RunGateway()

        with pytest.raises(GetError) as e:
            run_gateway.artifact_info("wxyz-wxyz-wxyz-wxyz", "abcd-abcd-abcd-abcd")

        assert "404 - The artifact for run SUUID 'wxyz-wxyz-wxyz-wxyz' was not found" in e.value.args[0]

    def test_run_artifiact_info_500(self):
        run_gateway = RunGateway()

        with pytest.raises(GetError) as e:
            run_gateway.artifact_info("zyxw-zyxw-zyxw-zyxw", "abcd-abcd-abcd-abcd")

        assert (
            "500 - Something went wrong while retrieving the artifact for run SUUID 'zyxw-zyxw-zyxw-zyxw'"
            in e.value.args[0]
        )
