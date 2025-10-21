from http import HTTPStatus
from unittest.mock import patch, MagicMock

from shared.reopen_issue import reopen_issue


@patch("httpx.request")
def test_reopen_issue(mock_request):
    args_dict = {
        "http_header": {},
        "reopen_url": "https://example.com",
        "reopen_http_method": "POST",
        "reopen_body": {},
    }
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK  # 200
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    reopen_issue(**args_dict)
