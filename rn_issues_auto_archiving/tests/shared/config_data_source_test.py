import os
import json
from unittest.mock import patch
from typing import TypeAlias, Any
from pathlib import Path

import pytest

from shared.json_config import Config, ConfigJson
from shared.config_data_source import (
    EnvConfigDataSource,
    JsonConfigDataSource,
    apply_place_holder
)
from shared.env import Env

TestConfigDict: TypeAlias = dict[str, str | dict[str, str]]


@pytest.mark.parametrize(
    "config_dict,expected_dict",
    [
        (
            {"version_regex": "(\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})",
             "archive_version_reges_for_comments": [
                 "{version_regex}测试通过",
                 "已验证[,，]版本号[:：]{version_regex}"
             ]},
            {"version_regex": "(\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})",
                "archive_version_reges_for_comments": [
                    "(\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})测试通过",
                    "已验证[,，]版本号[:：](\\d\\.\\d{2}\\.\\d{3}[a-zA-Z]?\\d{0,2})"
                ]}
        ),
    ]
)
def test_apply_place_holder(
    config_dict: TestConfigDict,
    expected_dict: TestConfigDict
):
    assert (apply_place_holder(config_dict, config_dict)
            == expected_dict)


class TestEnvConfigDataSource():
    @pytest.mark.parametrize(
        "env_dict", [
            {
                Env.TOKEN: "token",
                Env.ISSUE_OUTPUT_PATH: "issue_output_path",
                Env.CI_EVENT_TYPE: "ci_event_type",
                Env.ARCHIVED_DOCUMENT_PATH: "archived_document_path",
            },
        ]
    )
    def test_load(self, env_dict: dict[str, str]):
        with patch.dict(os.environ, env_dict):
            config = Config()
            env_config_data_source = EnvConfigDataSource()
            env_config_data_source.load(config)
            assert config.token == env_dict[Env.TOKEN]
            assert config.issue_output_path == env_dict[Env.ISSUE_OUTPUT_PATH]
            assert config.ci_event_type == env_dict[Env.CI_EVENT_TYPE]
            assert config.archived_document_path == env_dict[Env.ARCHIVED_DOCUMENT_PATH]


class TestJsonConfigDataSource():
    @pytest.mark.parametrize(
        "json_data", [
            {
                "archive_necessary_labels": [
                    "resolved 已解决"
                ],
                "issue_type": {
                    "type_keyword": {
                        "#Bug#": "Bug修复"
                    }
                },
                "archived_document": {
                    "issue_title_processing_rules": {
                        "Bug修复": {
                            "add_prefix": "修复了",
                            "add_suffix": "的Bug",
                            "remove_keyword": []
                        }
                    }
                }
            },
        ]
    )
    def test_load(self,
                  tmp_path: Path,
                  json_data: dict[
                      str,
                      Any]
                  ):
        sub_dir = tmp_path / "sub"
        sub_dir.mkdir()
        json_path = sub_dir / "test.json"
        json_path.write_text(json.dumps(
            json_data,
            indent=4,
            ensure_ascii=False
        ), encoding="utf-8")
        config = Config()
        json_config_data_source = JsonConfigDataSource(str(json_path))
        json_config_data_source.load(config)

        assert config.archive_necessary_labels == json_data[
            "archive_necessary_labels"]
        assert config.issue_type.type_keyword == json_data[
            "issue_type"]["type_keyword"]
        assert config.archived_document.issue_title_processing_rules == json_data[
            "archived_document"]["issue_title_processing_rules"]
