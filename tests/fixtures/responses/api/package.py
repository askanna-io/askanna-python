from typing import List

from responses import RequestsMock, matchers

from askanna.config.api_url import askanna_url


def package_response(
    api_responses: RequestsMock,
    package_zip_file: bytes,
    package_list_limit: dict,
    package_list_limit_empty: dict,
    package_list: List[dict],
) -> RequestsMock:
    url_package_zip = "https://cdn/files/packages/test.zip"

    # GET package list, files and download
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list() + "?project_suuid=1234-1234-1234-1234",
        status=200,
        content_type="application/json",
        json=package_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list() + "?page_size=1&project_suuid=abcd-abcd-abcd-abcd",
        status=200,
        content_type="application/json",
        json=package_list_limit_empty,
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list() + "?page_size=1",
        status=200,
        content_type="application/json",
        json=package_list_limit,
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list() + "?cursor=999",
        status=404,
        content_type="application/json",
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list() + "?cursor=999&page_size=1",
        status=500,
        content_type="application/json",
        json={"error": "Internal Server Error"},
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list() + "?page_size=100",
        status=200,
        content_type="application/json",
        json=package_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_list(),
        status=200,
        content_type="application/json",
        json=package_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_download("1234-1234-1234-1234"),
        status=200,
        content_type="application/json",
        json={
            "action": "redirect",
            "target": url_package_zip,
        },
    )
    api_responses.add(
        "HEAD",
        url=url_package_zip,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(package_zip_file)),
        },
        content_type="application/zip",
        status=200,
    )
    api_responses.add(
        "GET",
        url=url_package_zip,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(package_zip_file)),
        },
        match=[
            matchers.json_params_matcher({"Range": f"bytes=0-{len(package_zip_file)}"}),
            matchers.request_kwargs_matcher({"stream": True}),
        ],
        content_type="application/zip",
        status=206,
        body=package_zip_file,
    )
    api_responses.add(
        "GET",
        url=url_package_zip,
        content_type="application/zip",
        status=200,
        body=package_zip_file,
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_download("wxyz-wxyz-wxyz-wxyz"),
        status=404,
        json={"detail": "Not found."},
    )
    api_responses.add(
        "GET",
        url=askanna_url.package.package_download("zyxw-zyxw-zyxw-zyxw"),
        status=500,
        json={"error": "Internal Server Error"},
    )

    # POST new package and upload
    package_suuid = "abcd-abcd-abcd-abcd"
    chunk_uuid = "efgh-efgh-efgh-efgh"

    api_responses.add(
        "POST",
        url=askanna_url.package.package(),
        json={"suuid": package_suuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.package.package_chunk(package_suuid),
        json={"uuid": chunk_uuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.package.package_chunk_upload(package_suuid, chunk_uuid),
        status=200,
    )
    api_responses.add(
        "POST",
        url=askanna_url.package.package_finish_upload(package_suuid),
        status=200,
    )

    return api_responses
