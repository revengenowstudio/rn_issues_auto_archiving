import httpx

from shared.log import Log


def reopen_issue(
    http_header: dict[str, str],
    reopen_url: str,
    reopen_http_method: str,
    reopen_body: dict[str, str]
) -> None:
    '''api结构详见：
        https://docs.gitlab.com/ee/api/issues.html#edit-an-issue'''
    print(Log.reopen_issue_request)
    response = httpx.request(
        method=reopen_http_method,
        url=reopen_url,
        headers=http_header,
        json=reopen_body
    )
    response.raise_for_status()
    print(Log.reopen_issue_request_success)
