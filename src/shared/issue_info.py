from typing import TypedDict
from dataclasses import dataclass


class IssueInfoJson(TypedDict):
    class ReopenInfo(TypedDict):
        http_header: dict[str, str]
        reopen_url: str
        reopen_http_method: str
        reopen_body: dict[str, str]
        comment_url: str

    issue_id: int
    issue_type: str
    issue_title: str
    issue_state: str
    '''值只可能为 open 或 closed'''
    introduced_version: str
    archive_version: str
    reopen_info: ReopenInfo


@dataclass()
class IssueInfo():
    @dataclass()
    class ReopenInfo():
        http_header: dict[str, str]
        reopen_url: str
        reopen_http_method: str
        reopen_body: dict[str, str]
        comment_url: str

    issue_id: int
    issue_type: str
    issue_title: str
    issue_state: str
    '''值只可能为 open 或 closed'''
    introduced_version: str
    archive_version: str
    reopen_info: ReopenInfo


class ReopenIssueIssueInfoJson(TypedDict):
    '''归档流程失败时触发的issue reopen流水线payload'''
    reopen_issue_id: int
    reason: str
