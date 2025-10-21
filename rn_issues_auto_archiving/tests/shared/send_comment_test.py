from http import HTTPStatus
from unittest.mock import patch, MagicMock

from shared.send_comment import send_comment


@patch("httpx.request")
def test_send_comment(mock_request):
    args_dict = {
        "http_header": {},
        "comment_url": "https://example.com",
        "message": "test message",
    }
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK  # 200
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    send_comment(**args_dict)
