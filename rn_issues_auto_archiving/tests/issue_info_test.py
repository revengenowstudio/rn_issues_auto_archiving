import pytest

from shared.issue_info import IssueInfoJson


@pytest.mark.parametrize("issue_info,expected_result", [
    ({
        "issue_id": 1,
        "issue_type": "设定调整",
        "issue_title": "test_issue，这是issue标题",
        "issue_state": "closed",
        "introduced_version": "原版YR",
        "archive_version": "0.99.922",
        "ci_event_type": "trigger",
        "platform_type": "gitlab",
        "reopen_info": {
            "http_header": {
                "Authorization": "Bearer 12321312saddaed",
                "Content-Type": "application/json"
            },
            "reopen_url": "https://example.com/api/v4/projects/xx/issues/1",
            "reopen_http_method": "PUT",
            "reopen_body": {
                "state_event": "reopen"
            },
            "comment_url": "https://example.com/api/v4/projects/xx/issues/1/notes"
        }
    },
    {
        "issue_id": 1,
        "issue_type": "设定调整",
        "issue_title": "test_issue，这是issue标题",
        "issue_state": "closed",
        "introduced_version": "原版YR",
        "archive_version": "0.99.922",
        "ci_event_type": "trigger",
        "platform_type": "gitlab",
    })
])
def test_remove_sensitive_info(
        issue_info: IssueInfoJson,
        expected_result: dict):

    assert (IssueInfoJson.remove_sensitive_info(issue_info)
            == expected_result)
