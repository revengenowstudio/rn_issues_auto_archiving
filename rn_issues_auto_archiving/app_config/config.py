"""归档流水线的配置。

原配置来源为 ``config/auto_archiving.json``，现改为直接在本文件中定义，
文件底部构造一个全局单例 ``config`` 供各脚本 import 使用。

字段含义见同目录下的 README.md。
"""

from dataclasses import dataclass, field
from typing import TypedDict, TypeAlias

IssueTypeStr: TypeAlias = str


class ProcessingActionJson(TypedDict):
    add_prefix: str
    add_suffix: str
    remove_keyword: list[str]


@dataclass
class Config:
    @dataclass
    class IssueType:
        type_keyword: dict[str, str] = field(default_factory=dict)
        need_introduced_version_issue_type: list[str] = field(default_factory=list)
        label_map: dict[str, str] = field(default_factory=dict)

    @dataclass
    class ArchivedDocument:
        rjust_space_width: int = 0
        rjust_character: str = str()
        table_separator: str = str()
        archive_template: str = str()
        fill_issue_url_by_repository_type: list[str] = field(default_factory=list)
        action_name_to_repository_type_map: dict[str, str] = field(default_factory=dict)
        issue_title_processing_rules: dict[IssueTypeStr, ProcessingActionJson] = field(
            default_factory=dict
        )
        reopen_workflow_prefix_map: dict[str, str] = field(default_factory=dict)

    # 从env读取，由 EnvConfigDataSource 在运行时覆盖
    token: str = str()
    issue_output_path: str = str()
    ci_event_type: str = str()
    archived_document_path: str = str()

    # 以下为归档行为配置
    archive_necessary_labels: list[str] = field(default_factory=list)
    archive_version_reges_for_comments: list[str] = field(default_factory=list)
    archive_version_ignore_line_reges_for_comments: list[str] = field(
        default_factory=list
    )
    skip_archived_reges_for_comments: list[str] = field(default_factory=list)
    version_regex: str = str()
    issue_type: "Config.IssueType" = IssueType()
    introduced_version_reges: list[str] = field(default_factory=list)
    archived_document: ArchivedDocument = field(default_factory=ArchivedDocument)

    @property
    def raw_archive_version_reges_for_comments(self) -> list[str]:
        return [
            regex.replace(self.version_regex, "{version_regex}")
            for regex in self.archive_version_reges_for_comments
        ]


version_regex = r"(\d\.\d{2}\.\d{3}[a-zA-Z]?\d{0,2})"

config = Config(
    version_regex=version_regex,
    introduced_version_reges=[
        r"[【\[]发现版本号[】\]][：\:]([^\s\r\n【]+)",
    ],
    issue_type=Config.IssueType(
        type_keyword={
            "#Bug#": "Bug修复",
            "#BUG#": "Bug修复",
            "#bug#": "Bug修复",
            "#Bug修复#": "Bug修复",
            "#BUG修复#": "Bug修复",
            "#bug修复#": "Bug修复",
            "#BUG反馈#": "Bug修复",
            "#修复#": "Bug修复",
            "#建议反馈#": "设定调整",
            "#设定建议#": "设定调整",
            "#建议#": "设定调整",
            "#期望和反馈#": "设定调整",
            "#优化#": "设定调整",
            "#开发#": "设定引入",
            "#研发#": "设定引入",
            "#讨论#": "设定调整",
            "#功能增强#": "设定调整",
            "#功能需求#": "设定调整",
            "#功能性提议#": "设定调整",
            "#调整#": "设定调整",
            "#数据调整#": "设定调整",
            "#AI相关#": "设定调整",
            "#计划研讨#": "设定调整",
            "#工具需求#": "设定调整",
        },
        need_introduced_version_issue_type=[
            "Bug修复",
        ],
        label_map={
            "bug": "Bug修复",
            "enhancement 优化或建议": "设定调整",
            "task 任务": "设定引入",
        },
    ),
    archive_necessary_labels=[
        "resolved 已解决",
    ],
    archive_version_ignore_line_reges_for_comments=[
        r"^> ",
    ],
    # 引用了 version_regex，改动 version_regex 时这里的正则同步生效
    archive_version_reges_for_comments=[
        f"{version_regex} *测试通过",
        f"测试通过 *{version_regex}",
        f"{version_regex} *验证通过",
        f"验证通过 *{version_regex}",
        f"{version_regex} *已通过",
        f"{version_regex} *通过",
        f"{version_regex} *测试完成",
        f"{version_regex} *归档",
        f"^以{version_regex} *归档",
        f"^请以{version_regex} *归档",
        f"{version_regex} *自动归档",
    ],
    skip_archived_reges_for_comments=[
        "跳过归档流程",
        "不进行归档流程",
    ],
    archived_document=Config.ArchivedDocument(
        rjust_space_width=60,
        rjust_character=" ",
        table_separator="|",
        # 占位符由 ArchiveDocument.archive_issue 的 format 填充，不能改成 f-string
        archive_template="|{table_id}|({issue_type}){issue_title}{rjust_space}[{issue_repository}#{issue_id}]{issue_url_parents} |{introduced_version}|{archive_version}|",
        fill_issue_url_by_repository_type=[
            "外部Issue",
            "内部Issue",
        ],
        issue_title_processing_rules={
            "Bug修复": {
                "add_prefix": "修复了",
                "add_suffix": "的Bug",
                "remove_keyword": [],
            }
        },
    ),
)
