from responses import RequestsMock

from askanna.config.api_url import askanna_url


def auth_response(
    api_responses: RequestsMock,
    user_detail: dict,
) -> RequestsMock:
    api_responses.add(
        "GET",
        url=askanna_url.auth.user(),
        status=200,
        content_type="application/json",
        json=user_detail,
    )

    return api_responses
