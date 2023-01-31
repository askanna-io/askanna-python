import pytest
from responses import RequestsMock

from .artifact import artifact_response
from .job import job_response
from .package import package_response
from .project import project_response
from .result import result_response
from .run import run_response
from .variable import variable_response
from .workspace import workspace_response


@pytest.fixture
def api_response(
    job_list,
    job_list_limit,
    job_list_duplicate_job_name,
    job_detail,
    job_with_schedule_detail,
    job_run_request,
    package_list,
    package_list_limit,
    package_list_limit_empty,
    package_zip_file,
    project_list,
    project_list_limit,
    project_detail,
    project_new_detail,
    run_list,
    run_detail,
    run_detail_no_metric_no_variable,
    run_manifest,
    run_payload,
    run_artifact_list,
    run_artifact_list_not_found,
    run_log,
    variable_list,
    variable_list_limit,
    variable_detail,
    workspace_list,
    workspace_list_limit,
    workspace_detail,
    workspace_new_detail,
):

    api_responses = RequestsMock()
    api_responses.start()

    api_responses = artifact_response(api_responses, package_zip_file, run_artifact_list, run_artifact_list_not_found)

    api_responses = job_response(
        api_responses,
        job_list,
        job_list_limit,
        job_list_duplicate_job_name,
        job_detail,
        job_with_schedule_detail,
        job_run_request,
    )

    api_responses = package_response(
        api_responses,
        package_zip_file,
        package_list_limit,
        package_list_limit_empty,
        package_list,
    )

    api_responses = run_response(
        api_responses,
        run_list,
        run_detail,
        run_detail_no_metric_no_variable,
        run_manifest,
        run_payload,
        job_run_request,  # as run status response
        run_log,
    )

    api_responses = project_response(
        api_responses,
        project_list,
        project_list_limit,
        project_detail,
        project_new_detail,
    )

    api_responses = result_response(api_responses)

    api_responses = variable_response(api_responses, variable_list, variable_list_limit, variable_detail)

    api_responses = workspace_response(
        api_responses, workspace_list, workspace_list_limit, workspace_detail, workspace_new_detail
    )

    yield

    api_responses.stop
    api_responses.reset
