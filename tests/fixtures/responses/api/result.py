from responses import RequestsMock

from askanna.config.api_url import askanna_url


def result_response(api_responses: RequestsMock) -> RequestsMock:
    run_suuid = "1234-1234-1234-1234"
    run_suuid_fail = "5678-5678-5678-5678"
    run_suuid_finish_fail = "7890-7890-7890-7890"

    result_suuid = "abcd-abcd-abcd-abcd"
    result_suuid_fail = "zyxw-zyxw-zyxw-zyxw"

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
        url=askanna_url.run.result_upload(run_suuid_finish_fail),
        json={"suuid": result_suuid_fail},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_chunk(run_suuid_finish_fail, result_suuid_fail),
        json={"uuid": chunk_uuid},
        status=201,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_chunk_upload(run_suuid_finish_fail, result_suuid_fail, chunk_uuid),
        status=200,
    )
    api_responses.add(
        "POST",
        url=askanna_url.run.result_finish_upload(run_suuid_finish_fail, result_suuid_fail),
        status=500,
    )

    api_responses.add(
        "POST",
        url=askanna_url.run.result_upload(run_suuid_fail),
        json={"detail": "Not found."},
        status=404,
    )

    return api_responses
