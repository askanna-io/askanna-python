from responses import RequestsMock
from responses.matchers import json_params_matcher

from askanna.config.api_url import askanna_url


def workspace_response(
    api_responses: RequestsMock, workspace_list, workspace_list_limit, workspace_detail, workspace_new_detail
) -> RequestsMock:

    api_responses.add(
        "GET",
        url=f"{askanna_url.workspace.workspace_list()}?offset=1&limit=1&ordering=-created",
        status=200,
        content_type="application/json",
        json=workspace_list_limit,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.workspace.workspace_list()}?offset=999&limit=100&ordering=-created",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.workspace.workspace_list()}?offset=0&limit=100&ordering=-created",
        status=200,
        content_type="application/json",
        json=workspace_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.workspace.workspace_detail("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=workspace_detail,
    )
    api_responses.add(
        "GET",
        url=askanna_url.workspace.workspace_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.workspace.workspace_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "POST",
        url=askanna_url.workspace.workspace(),
        match=[
            json_params_matcher(
                {"name": "a new workspace", "description": "description new workspace", "visibility": "PUBLIC"}
            )
        ],
        status=201,
        content_type="application/json",
        json=workspace_new_detail,
    )
    api_responses.add(
        "POST",
        url=askanna_url.workspace.workspace(),
        match=[json_params_matcher({"name": "workspace with error", "description": "", "visibility": "PRIVATE"})],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    workspace_detail.update({"name": "new name"})
    api_responses.add(
        "PATCH",
        url=askanna_url.workspace.workspace_detail("1234-1234-1234-1234"),
        match=[json_params_matcher({"name": "new name"})],
        status=200,
        content_type="application/json",
        json=workspace_detail,
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.workspace.workspace_detail("7890-7890-7890-7890"),
        match=[json_params_matcher({"description": "new description"})],
        status=404,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.workspace.workspace_detail("0987-0987-0987-0987"),
        match=[json_params_matcher({"name": "new name"})],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    api_responses.add(
        "DELETE",
        url=askanna_url.workspace.workspace_detail("1234-1234-1234-1234"),
        status=204,
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.workspace.workspace_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.workspace.workspace_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    return api_responses
