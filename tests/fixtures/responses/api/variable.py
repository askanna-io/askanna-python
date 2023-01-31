from responses import RequestsMock, matchers

from askanna.config.api_url import askanna_url


def variable_response(
    api_responses: RequestsMock,
    variable_list,
    variable_list_limit,
    variable_detail,
) -> RequestsMock:
    api_responses.add(
        "GET",
        url=f"{askanna_url.variable.variable_list()}?page_size=1&cursor=123",
        status=200,
        content_type="application/json",
        json=variable_list_limit,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.variable.variable_list()}?cursor=999",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.variable.variable_list()}?page_size=100&order_by=name",
        status=200,
        content_type="application/json",
        json=variable_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.variable.variable_list(),
        status=200,
        content_type="application/json",
        json=variable_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.variable.variable_detail("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=variable_detail,
    )
    api_responses.add(
        "GET",
        url=askanna_url.variable.variable_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.variable.variable_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    variable_new_detail = variable_detail.copy()
    variable_new_detail.update(
        suuid="4321-4321-4321-4321", name="a new variable", value="new variable value", is_masked=False
    )
    api_responses.add(
        "POST",
        url=askanna_url.variable.variable(),
        match=[
            matchers.json_params_matcher(
                {
                    "project_suuid": "1234-1234-1234-1234",
                    "name": "a new variable",
                    "value": "new variable value",
                    "is_masked": False,
                }
            )
        ],
        status=201,
        content_type="application/json",
        json=variable_new_detail,
    )
    api_responses.add(
        "POST",
        url=askanna_url.variable.variable(),
        match=[
            matchers.json_params_matcher(
                {
                    "project_suuid": "1234-1234-1234-1234",
                    "name": "variable with error",
                    "value": "value",
                    "is_masked": True,
                },
            )
        ],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    variable_detail.update({"name": "new name"})
    api_responses.add(
        "PATCH",
        url=askanna_url.variable.variable_detail("1234-1234-1234-1234"),
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=200,
        content_type="application/json",
        json=variable_detail,
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.variable.variable_detail("7890-7890-7890-7890"),
        match=[matchers.json_params_matcher({"value": "new value"})],
        status=404,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.variable.variable_detail("0987-0987-0987-0987"),
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    api_responses.add(
        "DELETE",
        url=askanna_url.variable.variable_detail("1234-1234-1234-1234"),
        status=204,
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.variable.variable_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.variable.variable_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    return api_responses
