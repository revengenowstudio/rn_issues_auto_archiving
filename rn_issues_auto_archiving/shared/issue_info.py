from typing import TypedDict, Any
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import json

from json_dumps import json_dumps


AUTO_ISSUE_TYPE = "自动判断"


class LinksJson(TypedDict):
    issue_url: str
    reopen_http_method: str
    reopen_body: dict[str, str]
    comment_url: str


class IssueInfoJson(TypedDict):
    issue_id: int
    issue_type: str
    issue_title: str
    issue_state: str
    '''值只可能为 open 或 closed'''
    issue_body: str
    issue_labels: list[str]
    introduced_version: str
    archive_version: str
    ci_event_type: str
    platform_type: str
    http_header: dict[str, str]
    links: LinksJson


@dataclass()
class IssueInfo():
    @dataclass()
    class Links():
        issue_url: str = str()
        comment_url: str = str()

    issue_id: int = -1
    issue_type: str = AUTO_ISSUE_TYPE
    issue_title: str = str()
    issue_state: str = str()
    '''值只可能为 open 或 closed'''
    issue_body: str = str()
    issue_labels: list[str] = []
    introduced_version: str = str()
    archive_version: str = str()
    ci_event_type: str = str()
    platform_type: str = str()
    issue_repository: str = str()
    http_header: dict[str, str] = {}
    reopen_http_method: str = str()
    reopen_body: dict[str, str] = {}
    links: Links = Links()

    @staticmethod
    def remove_sensitive_info(issue_info: dict[str, Any]
                              ) -> dict[str, Any]:
        '''移除issue_info的敏感信息，函数不会修改传入的字典'''
        result = issue_info.copy()
        result.pop("http_header")
        return result

    def to_print_string(self) -> str:
        return json_dumps(
            IssueInfo.remove_sensitive_info(
                asdict(self)
            )
        )

    def print(self) -> None:
        print(
            self.to_print_string()
        )

    def to_dict(self) -> IssueInfoJson:
        return IssueInfoJson(**asdict(self))

    def json_dump(self, json_path: str) -> None:
        json.dump(
            self.to_dict(),
            Path(json_path).open("w", encoding="utf-8"),
            indent=4,
            ensure_ascii=False
        )

    def json_load(self, json_path: str) -> None:
        json_data: IssueInfoJson = json.loads(
            Path(json_path).read_text(encoding="utf-8")
        )
        links = json_data.get("links")
        replace(self, **json_data)
        replace(self.links, **links)

