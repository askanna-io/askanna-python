import pytest

from askanna.config import api_url, config


def test_base_url():
    assert api_url.base_url() == config.server.remote + "/v1/"


def test_askanna_url():
    assert type(api_url.askanna_url) == api_url.AskAnnaURL
    assert api_url.askanna_url.base_url == api_url.base_url()


class TestAskAnnaURL:
    def test_base_url(self):
        url = api_url.AskAnnaURL().base_url
        assert url == config.server.remote + "/v1/"

    def test_auth_url(self):
        url = api_url.AskAnnaURL().auth.base_auth_url
        assert url == config.server.remote + "/v1/auth/"

    def test_package_url(self):
        url = api_url.AskAnnaURL().package.base_package_url
        assert url == config.server.remote + "/v1/package/"

    def test_project_url(self):
        url = api_url.AskAnnaURL().project.base_project_url
        assert url == config.server.remote + "/v1/project/"

    def test_run_url(self):
        url = api_url.AskAnnaURL().run.base_run_url
        assert url == config.server.remote + "/v1/run/"

    def test_workspace_url(self):
        url = api_url.AskAnnaURL().workspace.base_workspace_url
        assert url == config.server.remote + "/v1/workspace/"


class TestAuthURL:
    def test_base_auth_url(self):
        url = api_url.AuthURL().base_auth_url
        assert url == config.server.remote + "/v1/auth/"

    def test_login_url(self):
        url = api_url.AuthURL().login()
        assert url == config.server.remote + "/v1/auth/login/"

    def test_logout_url(self):
        url = api_url.AuthURL().logout()
        assert url == config.server.remote + "/v1/auth/logout/"

    def test_user_url(self):
        url = api_url.AuthURL().user()
        assert url == config.server.remote + "/v1/auth/user/"


class TestJobURL:
    def test_base_project_url(self):
        url = api_url.JobURL().base_job_url
        assert url == config.server.remote + "/v1/job/"

    def test_job_url(self):
        url = api_url.JobURL().job()
        assert url == config.server.remote + "/v1/job/"

    def test_job_list_url(self):
        url = api_url.JobURL().job_list()
        assert url == config.server.remote + "/v1/job/"

    def test_job_detail_url(self):
        url = api_url.JobURL().job_detail("test_job")
        assert url == config.server.remote + "/v1/job/test_job/"

    def test_job_detail_url_without_job_suuid(self):
        with pytest.raises(TypeError):
            api_url.JobURL().job_detail()  # type: ignore

    def test_job_run_request_url(self):
        url = api_url.JobURL().run_request("test_job")
        assert url == config.server.remote + "/v1/job/test_job/run/request/batch/"

    def test_job_run_request_url_without_job_suuid(self):
        with pytest.raises(TypeError):
            api_url.JobURL().run_request()  # type: ignore


class TestPackageURL:
    def test_base_package_url(self):
        url = api_url.PackageURL().base_package_url
        assert url == config.server.remote + "/v1/package/"

    def test_package_url(self):
        url = api_url.PackageURL().package()
        assert url == config.server.remote + "/v1/package/"

    def test_package_list_url(self):
        url = api_url.PackageURL().package_list()
        assert url == config.server.remote + "/v1/package/"

    def test_package_detail_url(self):
        url = api_url.PackageURL().package_detail("test_package")
        assert url == config.server.remote + "/v1/package/test_package/"

    def test_package_detail_url_withtout_package_suuid(self):
        with pytest.raises(TypeError):
            api_url.PackageURL().package_detail()  # type: ignore

    def test_package_chunck(self):
        url = api_url.PackageURL().package_chunk("test_package")
        assert url == config.server.remote + "/v1/package/test_package/packagechunk/"

    def test_package_chunck_upload(self):
        url = api_url.PackageURL().package_chunk_upload("test_package", "test_chunk")
        assert url == config.server.remote + "/v1/package/test_package/packagechunk/test_chunk/chunk/"

    def test_package_finish_upload(self):
        url = api_url.PackageURL().package_finish_upload("test_package")
        assert url == config.server.remote + "/v1/package/test_package/finish_upload/"

    def test_download_url(self):
        url = api_url.PackageURL().package_download("test_package")
        assert url == config.server.remote + "/v1/package/test_package/download/"


class TestProjectURL:
    def test_base_project_url(self):
        url = api_url.ProjectURL().base_project_url
        assert url == config.server.remote + "/v1/project/"

    def test_project_url(self):
        url = api_url.ProjectURL().project()
        assert url == config.server.remote + "/v1/project/"

    def test_project_list_url(self):
        url = api_url.ProjectURL().project_list()
        assert url == config.server.remote + "/v1/project/"

    def test_project_detail_url(self):
        url = api_url.ProjectURL().project_detail("test_project")
        assert url == config.server.remote + "/v1/project/test_project/"

    def test_project_detail_url_without_project_suuid(self):
        with pytest.raises(TypeError):
            api_url.ProjectURL().project_detail()  # type: ignore


class TestRunURL:
    def test_base_run_url(self):
        url = api_url.RunURL().base_run_url
        assert url == config.server.remote + "/v1/run/"

    def test_run_url(self):
        url = api_url.RunURL().run()
        assert url == config.server.remote + "/v1/run/"

    def test_run__detail_url(self):
        url = api_url.RunURL().run_detail("test_run")
        assert url == config.server.remote + "/v1/run/test_run/"

    def test_run__detail_url_without_run_suuid(self):
        with pytest.raises(TypeError):
            api_url.RunURL().run_detail()  # type: ignore

    def test_run_list_url(self):
        url = api_url.RunURL().run_list()
        assert url == config.server.remote + "/v1/run/"

    def test_run_payload_list_url(self):
        url = api_url.RunURL().payload_list("test_run")
        assert url == config.server.remote + "/v1/run/test_run/payload/"

    def test_run_payload_download_url_without_payload_suuid(self):
        with pytest.raises(TypeError):
            api_url.RunURL().payload_download("test_run")  # type: ignore

    def test_run_payload_download_url(self):
        url = api_url.RunURL().payload_download("test_run", "test_payload")
        assert url == config.server.remote + "/v1/run/test_run/payload/test_payload/"

    def test_run_manifest_url(self):
        url = api_url.RunURL().manifest("test_run")
        assert url == config.server.remote + "/v1/run/test_run/manifest/"

    def test_artifact(self):
        url = api_url.RunURL().artifact("test_run")
        assert url == config.server.remote + "/v1/run/test_run/artifact/"

    def test_artifact_list(self):
        url = api_url.RunURL().artifact_list("test_run")
        assert url == config.server.remote + "/v1/run/test_run/artifact/"

    def test_artifact_chunck(self):
        url = api_url.RunURL().artifact_chunk("test_run", "test_artifact")
        assert url == config.server.remote + "/v1/run/test_run/artifact/test_artifact/artifactchunk/"

    def test_artifact_chunck_upload(self):
        url = api_url.RunURL().artifact_chunk_upload("test_run", "test_artifact", "test_chunk")
        assert url == config.server.remote + "/v1/run/test_run/artifact/test_artifact/artifactchunk/test_chunk/chunk/"

    def test_artifact_finish_upload(self):
        url = api_url.RunURL().artifact_finish_upload("test_run", "test_artifact")
        assert url == config.server.remote + "/v1/run/test_run/artifact/test_artifact/finish_upload/"

    def test_result(self):
        url = api_url.RunURL().result("test_run")
        assert url == config.server.remote + "/v1/run/test_run/result/"

    def test_result_upload(self):
        url = api_url.RunURL().result_upload("test_run")
        assert url == config.server.remote + "/v1/run/test_run/result-upload/"

    def test_result_upload_detail(self):
        url = api_url.RunURL().result_upload_detail("test_run", "test_result")
        assert url == config.server.remote + "/v1/run/test_run/result-upload/test_result/"

    def test_result_chunck(self):
        url = api_url.RunURL().result_chunk("test_run", "test_result")
        assert url == config.server.remote + "/v1/run/test_run/result-upload/test_result/resultchunk/"

    def test_result_chunck_upload(self):
        url = api_url.RunURL().result_chunk_upload("test_run", "test_result", "test_chunk")
        assert url == config.server.remote + "/v1/run/test_run/result-upload/test_result/resultchunk/test_chunk/chunk/"

    def test_result_finish_upload(self):
        url = api_url.RunURL().result_finish_upload("test_run", "test_result")
        assert url == config.server.remote + "/v1/run/test_run/result-upload/test_result/finish_upload/"


class WorkspaceURL:
    def test_base_workspace_url(self):
        url = api_url.WorkspaceURL().base_workspace_url
        assert url == config.server.remote + "/v1/workspace/"

    def test_workspace_url(self):
        url = api_url.WorkspaceURL().workspace()
        assert url == config.server.remote + "/v1/workspace/"

    def test_workspace_list_url(self):
        url = api_url.WorkspaceURL().workspace_list()
        assert url == config.server.remote + "/v1/workspace/"

    def test_workspace_detail_url(self):
        url = api_url.WorkspaceURL().workspace_detail("test_workspace")
        assert url == config.server.remote + "/v1/workspace/test_workspace/"

    def test_workspace_detail_url_without_workspace_suuid(self):
        with pytest.raises(TypeError):
            api_url.WorkspaceURL().workspace_detail()  # type: ignore

    def test_workspace_project_list_url(self):
        url = api_url.WorkspaceURL().project_list("test_workspace")
        assert url == config.server.remote + "/v1/workspace/test_workspace/project/"
