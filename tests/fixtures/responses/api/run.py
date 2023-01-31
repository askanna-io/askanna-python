from responses import RequestsMock, matchers

from askanna.config.api_url import askanna_url


def run_response(
    api_responses: RequestsMock,
    run_list,
    run_detail,
    run_detail_no_metric_no_variable,
    run_manifest,
    run_payload,
    run_status,
    run_log,
) -> RequestsMock:
    # Run list
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.run_list()}?page_size=100&order_by=job.name,name",
        status=200,
        content_type="application/json",
        json=run_list,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.run_list()}?page_size=100&order_by=job.name,name&project_suuid=5678-5678-5678-5678",
        status=200,
        content_type="application/json",
        json={"count": 0, "next": None, "previous": None, "results": []},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.run_list()}?page_size=100&order_by=job.name,name&project_suuid=3456-3456-3456-3456",
        status=200,
        content_type="application/json",
        json={"count": 1000, "next": None, "previous": None, "results": [run_detail]},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.run_list()}?page_size=100&order_by=job.name,name&project_suuid=7890-7890-7890-7890",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.run_list()}",
        status=200,
        content_type="application/json",
        json=run_list,
    )

    # Run detail
    api_responses.add(
        "GET",
        url=askanna_url.run.run_detail("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=run_detail,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.run_detail("4321-4321-4321-4321"),
        status=200,
        content_type="application/json",
        json=run_detail_no_metric_no_variable,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.run_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.run_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    detail_9876 = run_detail.copy()
    detail_9876.update({"suuid": "9876-9876-9876-9876"})
    api_responses.add(
        "GET",
        url=askanna_url.run.run_detail("9876-9876-9876-9876"),
        status=200,
        content_type="application/json",
        json=detail_9876,
    )

    # Run status
    api_responses.add(
        "GET",
        url=askanna_url.run.status("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=run_status,
    )

    # Run change info
    new_detail = run_detail.copy()
    new_detail.update({"name": "new name"})
    api_responses.add(
        "PATCH",
        url=askanna_url.run.run_detail("1234-1234-1234-1234"),
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=200,
        content_type="application/json",
        json=new_detail,
    )
    new_detail.update({"description": "new description"})
    api_responses.add(
        "PATCH",
        url=askanna_url.run.run_detail("1234-1234-1234-1234"),
        match=[matchers.json_params_matcher({"name": "new name", "description": "new description"})],
        status=200,
        content_type="application/json",
        json=new_detail,
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.run.run_detail("7890-7890-7890-7890"),
        match=[matchers.json_params_matcher({"description": "new description"})],
        status=404,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "PATCH",
        url=askanna_url.run.run_detail("0987-0987-0987-0987"),
        match=[matchers.json_params_matcher({"name": "new name"})],
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    # Run delete
    api_responses.add(
        "DELETE",
        url=askanna_url.run.run_detail("1234-1234-1234-1234"),
        status=204,
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.run.run_detail("7890-7890-7890-7890"),
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.run.run_detail("0987-0987-0987-0987"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "DELETE",
        url=askanna_url.run.run_detail("9876-9876-9876-9876"),
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    # Run payload
    api_responses.add(
        "HEAD",
        url=askanna_url.run.payload_download("1234-1234-1234-1234", "abcd-abcd-abcd-abcd"),
        headers={
            "Content-Length": str(len(run_payload)),
        },
        content_type="application/json",
        status=200,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.payload_download("1234-1234-1234-1234", "abcd-abcd-abcd-abcd"),
        status=200,
        content_type="application/json",
        json=run_payload,
    )
    api_responses.add(
        "HEAD",
        url=askanna_url.run.payload_download("1234-1234-1234-1234", "wxyz-wxyz-wxyz-wxyz"),
        headers={
            "Content-Length": "23",
        },
        content_type="application/json",
        status=404,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.payload_download("1234-1234-1234-1234", "wxyz-wxyz-wxyz-wxyz"),
        status=404,
        json={"detail": "Not found."},
    )
    api_responses.add(
        "HEAD",
        url=askanna_url.run.payload_download("1234-1234-1234-1234", "zyxw-zyxw-zyxw-zyxw"),
        headers={
            "Content-Length": "36",
        },
        content_type="application/json",
        status=500,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.payload_download("1234-1234-1234-1234", "zyxw-zyxw-zyxw-zyxw"),
        status=500,
        json={"error": "Internal Server Error"},
    )

    # Run manifest
    api_responses.add(
        "HEAD",
        url=f"{askanna_url.run.manifest('1234-1234-1234-1234')}",
        headers={
            "Content-Length": str(len(run_manifest)),
        },
        content_type="text/html",
        status=200,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.manifest('1234-1234-1234-1234')}",
        status=200,
        content_type="text/html",
        body=run_manifest,
    )
    api_responses.add(
        "HEAD",
        url=f"{askanna_url.run.manifest('wxyz-wxyz-wxyz-wxyz')}",
        headers={
            "Content-Length": "23",
        },
        content_type="application/json",
        status=404,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.manifest('wxyz-wxyz-wxyz-wxyz')}",
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "HEAD",
        url=f"{askanna_url.run.manifest('zyxw-zyxw-zyxw-zyxw')}",
        headers={
            "Content-Length": "36",
        },
        content_type="application/json",
        status=500,
    )
    api_responses.add(
        "GET",
        url=f"{askanna_url.run.manifest('zyxw-zyxw-zyxw-zyxw')}",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )

    # Run status
    api_responses.add(
        "GET",
        url=askanna_url.run.log("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json=run_log,
    )

    return api_responses
