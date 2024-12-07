import pytest
import json
from pathlib import Path

from shared.issue_info import IssueInfoJson, IssueInfo


full_issue_info_dict = {
    "issue_id": 1,
    "issue_type": "设定调整",
    "issue_title": "test_issue，这是issue标题",
    "issue_state": "closed",
    "issue_body": "这是一个测试issue描述",
    "issue_labels": ["hello"],
    "introduced_version": "原版YR",
    "archive_version": "0.99.922",
    "ci_event_type": "trigger",
    "platform_type": "gitlab",
    "issue_repository": "外部Issue",
    "http_header": {
        "Authorization": "Bearer 12321312saddaed",
        "Content-Type": "application/json"
    },
    "reopen_http_method": "PUT",
    "reopen_body": {
        "state_event": "reopen"
    },
    "links": {
        "issue_url": "https://example.com/api/v4/projects/xx/issues/1",
        "comment_url": "https://example.com/api/v4/projects/xx/issues/1/notes"
    }
}

default_issue_info_dict = {
    "issue_id": -1,
    "issue_type": "自动判断",
    "issue_title": "",
    "issue_state": "",
    "issue_body": "",
    "issue_labels": [],
    "introduced_version": "",
    "archive_version": "",
    "ci_event_type": "",
    "platform_type": "",
    "issue_repository": "",
    "http_header": {},
    "reopen_http_method": "",
    "reopen_body": {},
    "links": {
        "issue_url": "",
        "comment_url": ""
    }
}


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (full_issue_info_dict,
     full_issue_info_dict.copy()),
    (default_issue_info_dict,
     default_issue_info_dict.copy())
])
def test_remove_sensitive_info(
        issue_info_dict: IssueInfoJson,
        expected_result: dict
):
    expected_result.pop("http_header")
    assert (IssueInfo.remove_sensitive_info(
        dict(issue_info_dict))
        == expected_result)


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (default_issue_info_dict,
     default_issue_info_dict),
    (full_issue_info_dict,
     full_issue_info_dict)
])
def test_to_print_string(
    issue_info_dict: IssueInfoJson,
    expected_result: dict
):
    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    assert (issue_info.to_print_string() ==
            json.dumps(
                IssueInfo.remove_sensitive_info(expected_result),
        indent=4,
        ensure_ascii=False))


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (default_issue_info_dict,
     default_issue_info_dict),
    (full_issue_info_dict,
     full_issue_info_dict)
])
def test_to_dict(
    issue_info_dict: IssueInfoJson,
    expected_result: dict
):
    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    assert issue_info.to_dict() == expected_result


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (default_issue_info_dict,
     default_issue_info_dict),
    (full_issue_info_dict,
     full_issue_info_dict)
])
def test_json_dump(
    issue_info_dict: IssueInfoJson,
    expected_result: dict
):
    dump_json_name = "issue_info_test.json"
    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    try:
        issue_info.json_dump(dump_json_name)
        actual_result = json.loads(Path(dump_json_name).read_text(
            encoding="utf-8"
        ))
        assert actual_result == expected_result
    finally:
        Path(dump_json_name).unlink()

@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (default_issue_info_dict,
     default_issue_info_dict),
    (full_issue_info_dict,
     full_issue_info_dict)
])
def test_json_load(
    issue_info_dict: IssueInfoJson,
    expected_result: IssueInfoJson
):
    dump_json_name = "issue_info_test.json"
    try:
        Path(dump_json_name).write_text(
            json.dumps(issue_info_dict, indent=4, ensure_ascii=False), 
            encoding="utf-8"
        )
        issue_info = IssueInfo()
        issue_info.json_load(dump_json_name)
        expected_issue_info = IssueInfo()
        expected_issue_info.from_dict(expected_result)
        assert issue_info == expected_issue_info
    finally:
        Path(dump_json_name).unlink()
        
@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (default_issue_info_dict,
     default_issue_info_dict),
    (full_issue_info_dict,
     full_issue_info_dict)
])
def test_from_dict(
    issue_info_dict: IssueInfoJson,
    expected_result: IssueInfoJson
):

    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    assert issue_info.to_dict() == expected_result

