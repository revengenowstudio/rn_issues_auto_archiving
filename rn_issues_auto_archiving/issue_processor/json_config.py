from dataclasses import dataclass
from typing import TypedDict



class ConfigJson(TypedDict):
    class IssueType(TypedDict):
        type_keyword: dict[str, str]
        need_introduced_version_issue_type: list[str]
        label_map: dict[str, str]

    version_regex: str
    introduced_version_reges: list[str]
    issue_type: IssueType
    archived_version_reges_for_comments: list[str]
    archive_necessary_labels: list[str]

@dataclass
class Config():
    @dataclass
    class IssueType():
        type_keyword: dict[str, str] = {}
        need_introduced_version_issue_type: list[str] = []
        label_map: dict[str, str] = {}

    # 从env读取
    token: str = str()
    output_path: str = str()

    # 从命令行参数读取
    config_path: str = str()
    test_platform_type: str | None = None

    # 从配置文件json读取
    archive_necessary_labels: list[str] = []
    archived_version_reges_for_comments: list[str] = []
    version_regex: str = str()
    issue_type: IssueType = IssueType()
    introduced_version_reges: list[str]

