from responses import RequestsMock

from askanna.config.api_url import askanna_url


def run_response(api_responses: RequestsMock, run_manifest, run_payload) -> RequestsMock:
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

    return api_responses
