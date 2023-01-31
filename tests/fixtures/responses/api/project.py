from responses import RequestsMock, matchers

from askanna.config.api_url import askanna_url


def project_response(
    api_responses: RequestsMock,
    project_list,
    project_list_limit,
    project_detail,
    project_new_detail,
) -> RequestsMock:
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.project_list()}?page_size=1&cursor=123",
        status=200,
        content_type="application/json",
        json=project_list_limit,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.project_list()}?cursor=999",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.project.project_list()}?page_size=100&order_by=workspace.name,name",
        status=200,
        content_type="application/json",
        json=project_list,
    )
    api_responses.add(
        "GET",
        url=(
            f"{askanna_url.project.project_list()}?workspace_suuid=1234-1234-1234-1234&page_size=100&"
            "order_by=workspace.name,name"
        ),
        status=200,
        content_type="application/json",
        json=project_list,
    )
    api_responses.add(
        "GET",
        url=(
            f"{askanna_url.project.project_list()}?workspace_suuid=7890-7890-7890-7890&page_size=100&"
            "order_by=workspace.name,name"
        ),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=(
            f"{askanna_url.project.project_list()}?workspace_suuid=5678-5678-5678-5678&page_size=100&"
            "order_by=workspace.name,name"
        ),
        status=200,
        content_type="application/json",
        json={"count": 0, "next": None, "previous": None, "results": []},
    )
    api_responses.add(
        "GET",
        url=(
            f"{askanna_url.project.project_list()}?workspace_suuid=3456-3456-3456-3456&page_size=100&"
            "order_by=workspace.name,name"
        ),
        status=200,
        content_type="application/json",
        json={"count": 1000, "next": None, "previous": None, "results": [project_detail]},
    )
    api_responses.add(
        "GET",
        url=askanna_url.project.project_list(),
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
        url=askanna_url.project.project_detail("4321-4321-4321-4321"),
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
        "POST",
        url=askanna_url.project.project(),
        match=[
            matchers.json_params_matcher(
                {
                    "workspace_suuid": "1234-1234-1234-1234",
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
            matchers.json_params_matcher(
                {
                    "workspace_suuid": "1234-1234-1234-1234",
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
            matchers.json_params_matcher(
                {
                    "workspace_suuid": "5678-5678-5678-5678",
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
            matchers.json_params_matcher(
                {
                    "workspace_suuid": "1234-1234-1234-1234",
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
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=200,
        content_type="application/json",
        json=project_detail,
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.project.project_detail("7890-7890-7890-7890"),
        match=[matchers.json_params_matcher({"description": "new description"})],
        status=404,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.project.project_detail("0987-0987-0987-0987"),
        match=[matchers.json_params_matcher({"name": "new name"})],
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
        url=askanna_url.project.project_detail("4321-4321-4321-4321"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
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
