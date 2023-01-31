from askanna.config import config


def base_url() -> str:
    return config.server.remote + "/v1/"


class AskAnnaURL:
    def __init__(self):
        self.auth = AuthURL()
        self.job = JobURL()
        self.package = PackageURL()
        self.project = ProjectURL()
        self.run = RunURL()
        self.variable = VariableURL()
        self.workspace = WorkspaceURL()

    @property
    def base_url(self) -> str:
        return base_url()


class AuthURL:
    @property
    def base_auth_url(self) -> str:
        return base_url() + "auth/"

    def login(self) -> str:
        return self.base_auth_url + "login/"

    def logout(self) -> str:
        return self.base_auth_url + "logout/"

    def user(self) -> str:
        return self.base_auth_url + "user/"


class JobURL:
    @property
    def base_job_url(self) -> str:
        return base_url() + "job/"

    def job(self) -> str:
        return self.base_job_url

    def job_list(self) -> str:
        return self.base_job_url

    def job_detail(self, job_suuid: str) -> str:
        return self.base_job_url + job_suuid + "/"

    def run_request(self, job_suuid: str) -> str:
        return self.job_detail(job_suuid) + "run/request/batch/"


class PackageURL:
    @property
    def base_package_url(self) -> str:
        return base_url() + "package/"

    def package(self) -> str:
        return self.base_package_url

    def package_list(self) -> str:
        return self.base_package_url

    def package_detail(self, package_suuid: str) -> str:
        return self.package() + package_suuid + "/"

    def package_chunk(self, package_suuid: str) -> str:
        return self.package_detail(package_suuid) + "packagechunk/"

    def package_chunk_upload(self, package_suuid: str, chunk_uuid: str) -> str:
        return self.package_chunk(package_suuid) + chunk_uuid + "/chunk/"

    def package_finish_upload(self, package_suuid: str) -> str:
        return self.package_detail(package_suuid) + "finish_upload/"

    def package_download(self, package_suuid: str) -> str:
        return self.package_detail(package_suuid) + "download/"


class ProjectURL:
    @property
    def base_project_url(self) -> str:
        return base_url() + "project/"

    def project(self) -> str:
        return self.base_project_url

    def project_list(self) -> str:
        return self.base_project_url

    def project_detail(self, project_suuid: str) -> str:
        return self.base_project_url + project_suuid + "/"


class RunURL:
    @property
    def base_run_url(self) -> str:
        return base_url() + "run/"

    def run(self) -> str:
        return self.base_run_url

    def run_list(self) -> str:
        return self.base_run_url

    def run_detail(self, run_suuid: str) -> str:
        return self.base_run_url + run_suuid + "/"

    def payload_list(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "payload/"

    def payload_download(self, run_suuid: str, payload_suuid: str) -> str:
        return self.payload_list(run_suuid) + payload_suuid + "/"

    def status(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "status/"

    def manifest(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "manifest/"

    def metric(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "metric/"

    def metric_detail(self, run_suuid: str) -> str:
        return self.metric(run_suuid) + run_suuid + "/"

    def variable(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "variable/"

    def variable_detail(self, run_suuid: str) -> str:
        return self.variable(run_suuid) + run_suuid + "/"

    def log(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "log/"

    def artifact(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "artifact/"

    def artifact_list(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "artifact/"

    def artifact_detail(self, run_suuid: str, artifact_suuid: str) -> str:
        return self.run_detail(run_suuid) + "artifact/" + artifact_suuid + "/"

    def artifact_chunk(self, run_suuid, artifact_suuid: str) -> str:
        return self.artifact_detail(run_suuid, artifact_suuid) + "artifactchunk/"

    def artifact_chunk_upload(self, run_suuid: str, artifact_suuid: str, chunk_uuid: str) -> str:
        return self.artifact_chunk(run_suuid, artifact_suuid) + chunk_uuid + "/chunk/"

    def artifact_finish_upload(self, run_suuid: str, artifact_suuid: str) -> str:
        return self.artifact_detail(run_suuid, artifact_suuid) + "finish_upload/"

    def artifact_download(self, run_suuid: str, artifact_suuid: str) -> str:
        return self.artifact_detail(run_suuid, artifact_suuid) + "download/"

    def result(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "result/"

    def result_upload(self, run_suuid: str) -> str:
        return self.run_detail(run_suuid) + "result-upload/"

    def result_upload_detail(self, run_suuid: str, result_suuid: str) -> str:
        return self.result_upload(run_suuid) + result_suuid + "/"

    def result_chunk(self, run_suuid, result_suuid: str) -> str:
        return self.result_upload_detail(run_suuid, result_suuid) + "resultchunk/"

    def result_chunk_upload(self, run_suuid: str, result_suuid: str, chunk_uuid: str) -> str:
        return self.result_chunk(run_suuid, result_suuid) + chunk_uuid + "/chunk/"

    def result_finish_upload(self, run_suuid: str, result_suuid: str) -> str:
        return self.result_upload_detail(run_suuid, result_suuid) + "finish_upload/"


class VariableURL:
    @property
    def base_variable_url(self) -> str:
        return base_url() + "variable/"

    def variable(self) -> str:
        return self.base_variable_url

    def variable_list(self) -> str:
        return self.base_variable_url

    def variable_detail(self, variable_suuid: str) -> str:
        return self.base_variable_url + variable_suuid + "/"


class WorkspaceURL:
    @property
    def base_workspace_url(self) -> str:
        return base_url() + "workspace/"

    def workspace(self) -> str:
        return self.base_workspace_url

    def workspace_list(self) -> str:
        return self.base_workspace_url

    def workspace_detail(self, workspace_suuid: str) -> str:
        return self.base_workspace_url + workspace_suuid + "/"


askanna_url = AskAnnaURL()
