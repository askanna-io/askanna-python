from responses import RequestsMock

from askanna.config.api_url import askanna_url


def result_response(api_responses: RequestsMock) -> RequestsMock:
    run_suuid = "1234-1234-1234-1234"
    run_suuid_fail = "5678-5678-5678-5678"
    result_suuid = "abcd-abcd-abcd-abcd"
    chunk_uuid = "efgh-efgh-efgh-efgh"

    api_responses.add(
        "POST",
        url=askanna_url.run.result_upload(run_suuid),
        json={"suuid": result_suuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_chunk(run_suuid, result_suuid),
        json={"uuid": chunk_uuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_chunk_upload(run_suuid, result_suuid, chunk_uuid),
        status=200,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_finish_upload(run_suuid, result_suuid),
        status=200,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_upload(run_suuid_fail),
        json={"detail": "Not found."},
        status=404,
    )

    return api_responses
