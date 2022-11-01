from responses import RequestsMock
from responses.matchers import json_params_matcher

from askanna.config.api_url import askanna_url


def project_response(
    api_responses: RequestsMock,
    project_list,
    project_list_limit,
    project_detail,
    project_new_detail,
    package_list,
    package_list_limit,
) -> RequestsMock:
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.project_list()}?offset=1&limit=1&ordering=-created",
        status=200,
        content_type="application/json",
        json=project_list_limit,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.project_list()}?offset=999&limit=100&ordering=-created",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.project_list()}?offset=0&limit=100&ordering=-created",
        status=200,
        content_type="application/json",
        json=project_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.workspace.project_list(workspace_suuid="1234-1234-1234-1234")
        + "?offset=0&limit=100&ordering=-created",
        status=200,
        content_type="application/json",
        json=project_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.project.project_detail("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=project_detail,
    )
    api_responses.add(
        "GET",
        url=askanna_url.project.project_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.project.project_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.package_list('1234-1234-1234-1234')}?limit=1&offset=1",
        status=200,
        content_type="application/json",
        json=package_list_limit,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.package_list('1234-1234-1234-1234')}?offset=999",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=askanna_url.project.package_list("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=package_list,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.package_list('7890-7890-7890-7890')}",
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.package_list('0987-0987-0987-0987')}",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    api_responses.add(
        "POST",
        url=askanna_url.project.project(),
        match=[
            json_params_matcher(
                {
                    "workspace": "1234-1234-1234-1234",
                    "name": "a new project",
                    "description": "description new project",
                    "visibility": "PUBLIC",
                }
            )
        ],
        status=201,
        content_type="application/json",
        json=project_new_detail,
    )
    api_responses.add(
        "POST",
        url=askanna_url.project.project(),
        match=[
            json_params_matcher(
                {
                    "workspace": "1234-1234-1234-1234",
                    "name": "new-project",
                    "description": "",
                    "visibility": "PRIVATE",
                }
            )
        ],
        status=201,
        content_type="application/json",
        json=project_new_detail,
    )
    api_responses.add(
        "POST",
        url=askanna_url.project.project(),
        match=[
            json_params_matcher(
                {
                    "workspace": "5678-5678-5678-5678",
                    "name": "new-project",
                    "description": None,
                    "visibility": "PRIVATE",
                }
            )
        ],
        status=201,
        content_type="application/json",
        json=project_new_detail,
    )
    api_responses.add(
        "POST",
        url=askanna_url.project.project(),
        match=[
            json_params_matcher(
                {
                    "workspace": "1234-1234-1234-1234",
                    "name": "project with error",
                    "description": "",
                    "visibility": "PRIVATE",
                }
            )
        ],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    project_detail.update({"name": "new name"})
    api_responses.add(
        "PATCH",
        url=askanna_url.project.project_detail("1234-1234-1234-1234"),
        match=[json_params_matcher({"name": "new name"})],
        status=200,
        content_type="application/json",
        json=project_detail,
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.project.project_detail("7890-7890-7890-7890"),
        match=[json_params_matcher({"description": "new description"})],
        status=404,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.project.project_detail("0987-0987-0987-0987"),
        match=[json_params_matcher({"name": "new name"})],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    api_responses.add(
        "DELETE",
        url=askanna_url.project.project_detail("1234-1234-1234-1234"),
        status=204,
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.project.project_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.project.project_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    return api_responses
