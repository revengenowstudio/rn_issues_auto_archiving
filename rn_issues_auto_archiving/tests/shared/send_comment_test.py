from http import HTTPStatus
from unittest.mock import patch, MagicMock

from shared.send_comment import format_comment, send_comment


@patch("httpx.request")
def test_send_comment(mock_request):
    args_dict = {
        "http_header": {},
        "comment_url": "https://example.com",
        "message": "test message",
        "prefix": "【归档脚本消息】",
    }
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK  # 200
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    send_comment(**args_dict)


class TestFormatComment:
    def test_adds_prefix_and_space(self):
        assert format_comment("msg", "【归档脚本消息】") == "【归档脚本消息】 msg"

    def test_empty_prefix_keeps_message_without_space(self):
        assert format_comment("msg", "") == "msg"
