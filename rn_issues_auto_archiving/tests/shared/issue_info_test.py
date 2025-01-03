import pytest
import json
from pathlib import Path

from shared.issue_info import CommentJson, IssueInfoJson, IssueInfo
from shared.exception import *


class TestData():
    full_issue_info_dict = {
        "issue_id": 1,
        "issue_type": "设定调整",
        "issue_title": "test_issue，这是issue标题",
        "issue_state": "closed",
        "issue_body": "这是一个测试issue描述",
        "issue_labels": ["hello"],
        "issue_comments": [{
            "author": "test_user",
            "body": "test_body",
        }],
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
        "archived_success": False,
        "links": {
            "issue_url": "https://example.com/api/v4/projects/xx/issues/1",
            "issue_web_url": "https://example.com/xx/xx/issues/1",
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
        "issue_comments": [],
        "introduced_version": "",
        "archive_version": "",
        "ci_event_type": "",
        "platform_type": "",
        "issue_repository": "",
        "http_header": {},
        "reopen_http_method": "",
        "reopen_body": {},
        "archived_success": False,
        "links": {
            "issue_url": "",
            "issue_web_url": "",
            "comment_url": ""
        }
    }
    issue_body_with_introduced_version = "【发现版本号】：0.99.918\n"
    empty_issue_body = ""


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (TestData.full_issue_info_dict,
        TestData.full_issue_info_dict.copy()),
    (TestData.default_issue_info_dict,
        TestData.default_issue_info_dict.copy())
])
def test_remove_sensitive_info(
        issue_info_dict: IssueInfoJson,
        expected_result: dict
):
    expected_result.pop("http_header")
    assert (IssueInfo.remove_sensitive_info(
        dict(issue_info_dict))
        == expected_result)

# print_string只是输出一个json格式化的字符串罢了，应该没必要测试
# @pytest.mark.parametrize("issue_info_dict,expected_result", [
#     (TestData.default_issue_info_dict,
#         TestData.default_issue_info_dict),
#     (TestData.full_issue_info_dict,
#         TestData.full_issue_info_dict)
# ])
# def test_to_print_string(
#     issue_info_dict: IssueInfoJson,
#     expected_result: dict
# ):
#     issue_info = IssueInfo()
#     issue_info.from_dict(issue_info_dict)
#     assert (issue_info.to_print_string() ==
#             json.dumps(
#                 IssueInfo.remove_sensitive_info(expected_result),
#         indent=4,
#         ensure_ascii=False))


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (TestData.default_issue_info_dict,
        TestData.default_issue_info_dict),
    (TestData.full_issue_info_dict,
        TestData.full_issue_info_dict)
])
def test_to_dict(
    issue_info_dict: IssueInfoJson,
    expected_result: dict
):
    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    assert issue_info.to_dict() == expected_result


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (TestData.default_issue_info_dict,
        TestData.default_issue_info_dict),
    (TestData.full_issue_info_dict,
        TestData.full_issue_info_dict)
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
    (TestData.default_issue_info_dict,
        TestData.default_issue_info_dict),
    (TestData.full_issue_info_dict,
        TestData.full_issue_info_dict)
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
    (TestData.default_issue_info_dict,
        TestData.default_issue_info_dict),
    (TestData.full_issue_info_dict,
        TestData.full_issue_info_dict)
])
def test_from_dict(
    issue_info_dict: IssueInfoJson,
    expected_result: IssueInfoJson
):

    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    assert issue_info.to_dict() == expected_result


@pytest.mark.parametrize("issue_info_dict,expected_result", [
    (TestData.default_issue_info_dict,
        TestData.default_issue_info_dict),
    (TestData.full_issue_info_dict,
        TestData.full_issue_info_dict)
])
def test_update(
    issue_info_dict: IssueInfoJson,
    expected_result: IssueInfoJson
):

    issue_info = IssueInfo()
    issue_info.from_dict(issue_info_dict)
    issue_info.update(issue_title="test")
    expected_result["issue_title"] = "test"
    assert issue_info.to_dict() == expected_result

    issue_info.update(links=IssueInfo.Links(
        issue_url="https://example.com",
        issue_web_url="https://example.com/1",
        comment_url="https://example.com/2"
    ))
    expected_result["links"] = {
        "issue_url": "https://example.com",
        "issue_web_url": "https://example.com/1",
        "comment_url": "https://example.com/2"
    }
    assert issue_info.to_dict() == expected_result


@pytest.mark.parametrize("issue_body,with_introduced_version,issue_type,expected_version", [

    (TestData.issue_body_with_introduced_version,
        True, "Bug修复", "0.99.918"),  # 描述里有归档版本号
    (TestData.issue_body_with_introduced_version,
     True, "设定调整", "0.99.918"),  # 描述里有归档版本号
    (TestData.issue_body_with_introduced_version,
     True, "设定引入", "0.99.918"),  # 描述里有归档版本号
    (TestData.empty_issue_body, False, "Bug修复", ""),  # 描述里没有归档版本号
    (TestData.empty_issue_body, False, "设定调整", ""),  # 描述里没有归档版本号
    (TestData.empty_issue_body, False, "设定引入", ""),  # 描述里没有归档版本号
])
def test_get_introduced_version_from_description(
    issue_body: str,
    with_introduced_version: bool,
    issue_type: str,
    expected_version: str
):
    issue_info = IssueInfo()
    issue_info.update(
        issue_body=issue_body,
        issue_type=issue_type
    )

    introduced_version_reges = [
        "[【\\[]发现版本号[】\\]][：\\:]([^\\s\\r\\n【]+)"
    ]
    need_introduced_version_issue_type = [
        "Bug修复"
    ]

    if (issue_type in need_introduced_version_issue_type
            and not with_introduced_version):
        with pytest.raises(
            IntroducedVersionError,
            match=ErrorMessage.missing_introduced_version
        ):
            issue_info.get_introduced_version_from_description(
                introduced_version_reges,
                need_introduced_version_issue_type
            )

    if (issue_type in need_introduced_version_issue_type
            and with_introduced_version):
        introduced_version = issue_info.get_introduced_version_from_description(
            introduced_version_reges,
            need_introduced_version_issue_type
        )
        assert introduced_version == expected_version

        with pytest.raises(
            IntroducedVersionError
        ):
            issue_info.update(
                issue_body=issue_body * 2
            )
            issue_info.get_introduced_version_from_description(
                introduced_version_reges,
                need_introduced_version_issue_type
            )
            issue_info.update(
                issue_body=issue_body
            )
    if (issue_type not in need_introduced_version_issue_type):
        introduced_version = issue_info.get_introduced_version_from_description(
            introduced_version_reges,
            need_introduced_version_issue_type
        )
        assert introduced_version == expected_version


@pytest.mark.parametrize("comments,include_archive_version_number,expected_version,", [
    ([
        {
            "body": "0.99.918测试通过"
        },
        {
            "body": ""
        }
    ], 1, "0.99.918"),
    ([
        {
            "body": "0.99.918测试通过"
        },
        {
            "body": "已验证，版本号：0.99.918"
        }
    ], 2, "0.99.918"),
    ([
        {
            "body": ""
        },
        {
            "body": ""
        }
    ], 0, ""),
])
def test_get_archive_version_from_comments(
    comments: list[CommentJson],
    include_archive_version_number: int,
    expected_version: str
):

    issue_info = IssueInfo()
    issue_info.update(
        issue_comments=[
            IssueInfo.Comment(
                author="test",
                body=comment_dict["body"]
            )
            for comment_dict in comments
        ]
    )
    archive_version_reges_for_comments = [
        "(\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})测试通过",
        "已验证[,，]版本号[:：](\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})"
    ]
    if include_archive_version_number >= 2:
        with pytest.raises(
            ArchiveVersionError
        ):
            issue_info.get_archive_version_from_comments(
                archive_version_reges_for_comments
            )

    else:
        assert expected_version == issue_info.get_archive_version_from_comments(
            archive_version_reges_for_comments
        )


@pytest.mark.parametrize("labels,issue_type_label_number,expected_type", [
    ([""], 0,  ""),
    (["bug"], 1,  "Bug修复"),
    (["bug", "enhancement 优化或建议"], 2, "")
])
def test_get_issue_type_from_labels(
    labels: list[CommentJson],
    issue_type_label_number: int,
    expected_type: str
):

    issue_info = IssueInfo()
    issue_info.update(
        issue_labels=labels
    )
    label_map = {
        "bug": "Bug修复",
        "enhancement 优化或建议": "设定调整",
        "task 任务": "设定引入"
    }
    if (issue_type_label_number >= 2
            or issue_type_label_number == 0):
        with pytest.raises(
            IssueTypeError
        ):
            issue_info.get_issue_type_from_labels(
                label_map
            )
    else:
        assert expected_type == issue_info.get_issue_type_from_labels(
            label_map
        )


comments_without_archived_version = [
    {
        "body": ""
    },
    {
        "body": ""
    }
]
comments_with_single_archived_version = [
    {
        "body": "0.99.918测试通过"
    },
    {
        "body": ""
    }
]
comments_with_double_archived_version = [
    {
        "body": "0.99.918测试通过"
    },
    {
        "body": "已验证，版本号：0.99.918"
    }
]


@pytest.mark.parametrize(
    "labels,comments,archive_version_number,expected_result",
    [
        ([""], comments_without_archived_version, 0, False),
        ([""], comments_with_single_archived_version, 1, False),
        # ([""], comments_with_double_archived_version,2, False),
        (["resolved 已解决"], comments_without_archived_version, 0, False),
        (["resolved 已解决"], comments_with_single_archived_version, 1, True),
        # (["resolved 已解决"], comments_with_double_archived_version,2, False),
    ])
def test_should_archive_issue(
    labels: list[CommentJson],
    comments: list[CommentJson],
    archive_version_number: int,
    expected_result: bool
):

    issue_info = IssueInfo()
    issue_info.update(
        issue_comments=[
            IssueInfo.Comment(
                author="test",
                body=comment_dict["body"]
            )
            for comment_dict in comments
        ],
        issue_labels=labels
    )
    archive_necessary_labels = [
        "resolved 已解决"
    ]
    archive_version_reges_for_comments = [
        "(\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})测试通过",
        "已验证[,，]版本号[:：](\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})"
    ]

    # 不是归档对象：缺少归档评论，缺少归档所需标签
    # 是归档对象，不满足归档条件：有归档评论，缺少归档所需标签
    # 是归档对象，不满足归档条件：缺少归档评论，有归档所需标签
    # 是归档对象，满足归档条件：有归档评论，有归档所需标签
    [i for i in [body if "0.99.918" in body else ""
                 for body in [comment_dict["body"]
                              for comment_dict in comments]] if i.strip()
     ]

    if ("resolved 已解决" not in labels
            and archive_version_number == 1):
        with pytest.raises(
            ArchiveLabelError
        ):
            issue_info.should_archive_issue(
                archive_version_reges_for_comments,
                archive_necessary_labels
            )

    elif ("resolved 已解决" in labels
            and archive_version_number == 0):
        with pytest.raises(
            ArchiveVersionError
        ):
            issue_info.should_archive_issue(
                archive_version_reges_for_comments,
                archive_necessary_labels
            )

    if (("resolved 已解决" not in labels
            and archive_version_number == 0)
        or (
            "resolved 已解决" in labels
            and archive_version_number == 1
    )):
        assert expected_result == issue_info.should_archive_issue(
            archive_version_reges_for_comments,
            archive_necessary_labels
        )


@pytest.mark.parametrize(
    "issue_title,expected_result",
    [
        ("#建议反馈#建议能坦克碾压一些小型地图物件和路灯",
            "建议能坦克碾压一些小型地图物件和路灯"),
        ("建议能坦克碾压一些小型地图物件和路灯",
            "建议能坦克碾压一些小型地图物件和路灯"),
    ])
def test_remove_issue_type_in_issue_title(
    issue_title: str,
    expected_result: str
):
    issue_info = IssueInfo()
    issue_info.update(
        issue_title=issue_title
    )
    type_keyword = {
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
        "#工具需求#": "设定调整"
    }
    assert expected_result == issue_info.remove_issue_type_in_issue_title(
        type_keyword
    )


def test_set_archived_success():
    issue_info = IssueInfo()
    issue_info.set_archived_success()
    assert issue_info.archived_success is True


def test_should_archived_success():
    issue_info = IssueInfo()
    assert issue_info.archived_success is False
    issue_info.archived_success = True
    assert issue_info.archived_success is True


def test_should_skip_archived_process():
    issue_info = IssueInfo()
    reges = ["跳过归档流程", "test_regex"]

    assert issue_info.should_skip_archived_process(
        reges
    ) is False

    issue_info.issue_comments = [
        IssueInfo.Comment(
            author="test",
            body="跳过归档流程"
        ),
        IssueInfo.Comment(
            author="test",
            body="qewqio\n\nsdjio跳过归档流程\n\n\n\1e13123"
        ),
    ]
    assert issue_info.should_skip_archived_process(
        reges
    ) is True

    issue_info.issue_comments = [
        IssueInfo.Comment(
            author="test",
            body="test_regex"
        ),
        IssueInfo.Comment(
            author="test",
            body="qewqiojisdtest_regexdsadas1e13123"
        ),
    ]
    assert issue_info.should_skip_archived_process(
        reges
    ) is True
