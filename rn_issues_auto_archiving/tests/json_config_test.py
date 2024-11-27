import pytest

import issue_processor.json_config
import auto_archiving.json_config


def test_issue_processor_json_config():
    assert issue_processor.json_config.Config(
        "./config/issue_processor.json")


def test_auto_archiving_json_config():
    assert auto_archiving.json_config.Config(
        "./config/auto_archiving.json")


EXAMPLE_JSON1 = {
    "version_regex": "(version:\\d{3}[a-zA-Z])",
    "introduced_version_reges": [
        "introduced:\\d{3}[a-zA-Z]"
    ],
    "issue_type": {
        "label_map": {
            "bug": "Bug修复",
            "enhancement 优化或建议": "设定调整",
            "task 任务": "设定引入"
        }
    },
    "white_list": {
        "labels": [
            "resolved 已解决"
        ],
        "comments": [
            "{version_regex}测试通过",
            "已验证[,，]版本号[:：]{version_regex}"
        ]
    },
}

EXAMPLE_JSON1_EXPECTED = {
    "version_regex": "(version:\\d{3}[a-zA-Z])",
    "introduced_version_reges": [
        "introduced:\\d{3}[a-zA-Z]"
    ],
    "issue_type": {
        "label_map": {
            "bug": "Bug修复",
            "enhancement 优化或建议": "设定调整",
            "task 任务": "设定引入"
        }
    },
    "white_list": {
        "labels": [
            "resolved 已解决"
        ],
        "comments": [
            "(version:\\d{3}[a-zA-Z])测试通过",
            "已验证[,，]版本号[:：](version:\\d{3}[a-zA-Z])"
        ]
    },
}


@pytest.mark.parametrize(
    "obj,expected",
    [
        (EXAMPLE_JSON1, EXAMPLE_JSON1_EXPECTED)
    ]
)
def test_apply_place_holder(
    obj: dict,
    expected: dict
):
    issue_processor.json_config.apply_place_holder(obj, obj)
    assert obj == expected
