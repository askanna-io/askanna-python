from responses import RequestsMock, matchers

from askanna.config.api_url import askanna_url


def job_response(
    api_responses: RequestsMock,
    job_list,
    job_list_limit,
    job_list_duplicate_job_name,
    job_detail,
    job_with_schedule_detail,
    job_run_request,
) -> RequestsMock:
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?page_size=1&cursor=123",
        status=200,
        content_type="application/json",
        json=job_list_limit,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?cursor=999",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?page_size=100&order_by=project.name,name",
        status=200,
        content_type="application/json",
        json=job_list,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?project_suuid=1234-1234-1234-1234",
        status=200,
        content_type="application/json",
        json=job_list,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?workspace_suuid=4321-4321-4321-4321",
        status=200,
        content_type="application/json",
        json=job_list,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?page_size=100&search=a+job",
        status=200,
        content_type="application/json",
        json=job_list,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?project_suuid=abcd-abcd-abcd-abcd&page_size=100&search=a+job",
        status=200,
        content_type="application/json",
        json=job_list_duplicate_job_name,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?page_size=100&order_by=project.name,name&project_suuid=5678-5678-5678-5678",
        status=200,
        content_type="application/json",
        json={"count": 0, "next": None, "previous": None, "results": []},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?page_size=100&order_by=project.name,name&project_suuid=3456-3456-3456-3456",
        status=200,
        content_type="application/json",
        json={"count": 1000, "next": None, "previous": None, "results": [job_detail]},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}?page_size=100&order_by=project.name,name&project_suuid=7890-7890-7890-7890",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.job.job_list()}",
        status=200,
        content_type="application/json",
        json=job_list,
    )

    api_responses.add(
        "GET",
        url=askanna_url.job.job_detail("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=job_detail,
    )
    api_responses.add(
        "GET",
        url=askanna_url.job.job_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.job.job_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=askanna_url.job.job_detail("9876-9876-9876-9876"),
        status=200,
        content_type="application/json",
        json=job_detail,
    )
    api_responses.add(
        "GET",
        url=askanna_url.job.job_detail("5678-5678-5678-5678"),
        status=200,
        content_type="application/json",
        json=job_with_schedule_detail,
    )

    api_responses.add(
        "POST",
        url=askanna_url.job.run_request("1234-1234-1234-1234"),
        status=201,
        content_type="application/json",
        json=job_run_request,
    )
    api_responses.add(
        "POST",
        url=askanna_url.job.run_request("7890-7890-7890-7890"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    job_detail.update({"name": "new name"})
    api_responses.add(
        "PATCH",
        url=askanna_url.job.job_detail("1234-1234-1234-1234"),
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=200,
        content_type="application/json",
        json=job_detail,
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.job.job_detail("7890-7890-7890-7890"),
        match=[matchers.json_params_matcher({"description": "new description"})],
        status=404,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.job.job_detail("0987-0987-0987-0987"),
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    api_responses.add(
        "DELETE",
        url=askanna_url.job.job_detail("1234-1234-1234-1234"),
        status=204,
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.job.job_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.job.job_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.job.job_detail("9876-9876-9876-9876"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    return api_responses
