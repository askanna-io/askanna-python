from responses import RequestsMock, matchers

from askanna.config.api_url import askanna_url


def artifact_response(
    api_responses: RequestsMock,
    run_artifact_file: bytes,
    run_artifact_list: list,
    run_artifact_list_not_found: list,
) -> RequestsMock:
    run_suuid = "1234-1234-1234-1234"
    run_suuid_not_found_artifact = "5678-5678-5678-5678"
    run_suuid_with_finish_fail = "7890-7890-7890-7890"

    artifact_suuid = "abcd-abcd-abcd-abcd"
    artifact_suuid_not_found = "wxyz-wxyz-wxyz-wxyz"
    artifact_suuid_fail = "zyxw-zyxw-zyxw-zyxw"

    chunk_uuid = "efgh-efgh-efgh-efgh"

    url_artifact_zip = "https://cdn/files/artifact/test.zip"

    # Get artifact
    api_responses.add(
        "GET",
        url=askanna_url.run.artifact_list(run_suuid),
        status=200,
        json=run_artifact_list,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.artifact_download(run_suuid, artifact_suuid),
        status=200,
        content_type="application/json",
        json={
            "action": "redirect",
            "target": url_artifact_zip,
        },
    )
    api_responses.add(
        "HEAD",
        url=url_artifact_zip,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(run_artifact_file)),
        },
        content_type="application/zip",
        status=200,
    )
    api_responses.add(
        "GET",
        url=url_artifact_zip,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(run_artifact_file)),
        },
        match=[
            matchers.json_params_matcher({"Range": f"bytes=0-{len(run_artifact_file)}"}),
            matchers.request_kwargs_matcher({"stream": True}),
        ],
        content_type="application/zip",
        status=206,
        body=run_artifact_file,
    )
    api_responses.add(
        "GET",
        url=url_artifact_zip,
        content_type="application/zip",
        status=200,
        body=run_artifact_file,
    )

    # Get artifact not found
    api_responses.add(
        "GET",
        url=askanna_url.run.artifact_list(run_suuid_not_found_artifact),
        status=200,
        json=run_artifact_list_not_found,
    )
    api_responses.add(
        "GET",
        url=askanna_url.run.artifact_download(run_suuid_not_found_artifact, artifact_suuid_not_found),
        status=404,
        json={"detail": "Not found."},
    )

    # POST new artifact and upload
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_list(run_suuid),
        json={"suuid": artifact_suuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_chunk(run_suuid, artifact_suuid),
        json={"uuid": chunk_uuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_chunk_upload(run_suuid, artifact_suuid, chunk_uuid),
        status=200,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_finish_upload(run_suuid, artifact_suuid),
        status=200,
    )

    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_list(run_suuid_with_finish_fail),
        json={"suuid": artifact_suuid_fail},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_chunk(run_suuid_with_finish_fail, artifact_suuid_fail),
        json={"uuid": chunk_uuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_chunk_upload(run_suuid_with_finish_fail, artifact_suuid_fail, chunk_uuid),
        status=200,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_finish_upload(run_suuid_with_finish_fail, artifact_suuid_fail),
        status=500,
    )

    api_responses.add(
        "POST",
        url=askanna_url.run.artifact_list(run_suuid_not_found_artifact),
        status=500,
        json={"error": "Internal Server Error"},
    )

    return api_responses
