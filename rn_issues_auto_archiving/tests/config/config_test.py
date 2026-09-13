import re

from app_config import Config, config


class TestConfigSingleton:
    def test_is_config_instance(self):
        assert isinstance(config, Config)

    def test_version_regex_matches_version_number(self):
        version_regex = re.compile(config.version_regex)
        assert version_regex.search("0.99.918")
        assert version_regex.search("0.99.918c10")
        assert version_regex.search("修复了0.99.928的Bug")
        assert version_regex.search("abc") is None

    def test_archive_version_reges_placeholder_is_expanded(self):
        for regex in config.archive_version_reges_for_comments:
            assert "{version_regex}" not in regex

    def test_archive_version_reges_matches_comment(self):
        version_regex = re.compile(config.archive_version_reges_for_comments[0])
        assert version_regex.search("0.99.918 测试通过")

    def test_raw_archive_version_reges_restores_placeholder(self):
        raw_reges = config.raw_archive_version_reges_for_comments
        assert len(raw_reges) == len(config.archive_version_reges_for_comments)
        assert all("{version_regex}" in regex for regex in raw_reges)

    def test_introduced_version_reges_matches_description(self):
        introduced_version_reges = [
            re.compile(regex) for regex in config.introduced_version_reges
        ]
        description = "【发现版本号】：0.99.918"
        assert any(regex.search(description) for regex in introduced_version_reges)

    def test_issue_type(self):
        assert config.issue_type.label_map["bug"] == "Bug修复"
        assert config.issue_type.need_introduced_version_issue_type == ["Bug修复"]

    def test_archive_necessary_labels(self):
        assert config.archive_necessary_labels == ["resolved 已解决"]

    def test_archived_document(self):
        archived_document = config.archived_document
        assert archived_document.rjust_space_width == 60
        assert archived_document.table_separator == "|"
        assert (
            archived_document.issue_title_processing_rules["Bug修复"]["add_prefix"]
            == "修复了"
        )
