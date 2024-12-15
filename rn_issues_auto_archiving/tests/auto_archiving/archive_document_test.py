import pytest
from unittest.mock import patch, MagicMock
from io import TextIOWrapper
from pathlib import Path

from auto_archiving.archive_document import ArchiveDocument


class TestArchiveDocument():

    @pytest.fixture(scope="function")
    def archive_document(self):
        return ArchiveDocument()

    @patch("builtins.open")
    def test_file_load(
        self,
        mock_open: MagicMock,
        archive_document: ArchiveDocument
    ):
        test_filename = "test_filename"
        mock_file = MagicMock(spec=TextIOWrapper)
        mock_open.return_value.__enter__.return_value = mock_file
        archive_document.file_load(test_filename)
        mock_open.assert_called_once_with(
            test_filename,
            'r',
            encoding="utf-8"
        )

    @patch("builtins.open")
    def test_should_issue_record_exists(
        self,
        mock_open: MagicMock,
        archive_document: ArchiveDocument
    ):
        test_lines_set = {   # 这个函数会特意匹配]，所以末尾有个]
            "外部Issue#123]",
            "内部Issue#123]",
            "外部Issue#12]",
        }
        test_filename = "test_filename"
        mock_file = MagicMock(spec=TextIOWrapper)
        mock_file.readlines.return_value = list(test_lines_set)
        mock_open.return_value.__enter__.return_value = mock_file
        archive_document.file_load(test_filename)

        assert archive_document.should_issue_record_exists(
            "外部Issue", 123
        )
        assert archive_document.should_issue_record_exists(
            "外部Issue", 1234
        ) is False

    @patch("builtins.open")
    def test_archive_issue(
        self,
        mock_open: MagicMock,
        archive_document: ArchiveDocument
    ):
        archive_rules = {
            "rjust_space_width": 0,
            "rjust_character": " ",
            "table_separator": "|",
            "archive_template": "|{table_id}|({issue_type}){issue_title}{rjust_space}[{issue_repository}#{issue_id}]{issue_url_parents} |{introduced_version}|{archive_version}|",
            "fill_issue_url_by_repository_type": [
                "外部Issue"
            ],
            "issue_title_processing_rules": {
                "Bug修复": {
                    "add_prefix": "修复了",
                    "add_suffix": "的Bug",
                    "remove_keyword": []
                }
            },
        }
        test_lines = [
            line + '\n'
            for line in [
                "# RN历史修改归档",
                "(本页面不包含宣发业务历史)",
                "",
                "|序号|描述(优化)(数据调整)(Bug修复)(设定引入)(设定调整)                                             |引入版本号|归档版本号|",
                "|----|-------------------------------------------------------------------------------------------|---------|----------|",
                "|1|(Bug修复)修复了这是issues标题的Bug  [外部Issue#1] |0.99.914a9|0.99.966|",
            ]]
        test_issue_data = {
            "issue_id": 2,
            "issue_type": "Bug修复",
            "issue_title": "测试标题",
            "issue_repository": "外部Issue",
            "issue_url": "https://api.example.com/issues/2",
            "introduced_version": "0.99.914",
            "archive_version": "0.99.915",
        }
        not_replaced_result = "|2|(Bug修复)修复了测试标题的Bug[外部Issue#2](https://api.example.com/issues/2) |0.99.914|0.99.915|\n"
        replaced_result = "|1|(Bug修复)修复了测试标题的Bug[外部Issue#1](https://api.example.com/issues/2) |0.99.914|0.99.915|\n"
        
        test_issue_data_no_url = {
            "issue_id": 3,
            "issue_type": "Bug修复",
            "issue_title": "测试标题",
            "issue_repository": "内部Issue",
            "issue_url": "https://api.example.com/issues/3",
            "introduced_version": "0.99.914",
            "archive_version": "0.99.915",
        }
        not_replaced_result_no_url = "|2|(Bug修复)修复了测试标题的Bug[内部Issue#3] |0.99.914|0.99.915|\n"

        test_filename = "test_filename"
        mock_file = MagicMock(spec=TextIOWrapper)
        mock_file.readlines.return_value = test_lines
        mock_open.return_value.__enter__.return_value = mock_file
        archive_document.file_load(test_filename)

        # 非替换模式，直接 __add_line
        # 替换模式，检索issue_id是否已经存在，
        # 若咩有在lines里找到issue_id，则 __add_line
        # 若找到，则 __replace_line
        archive_document.archive_issue(
            replace_mode=False,
            **test_issue_data,
            **archive_rules
        )
        assert archive_document.show_new_line()[0] == not_replaced_result

        test_issue_data["issue_id"] = 1
        archive_document.archive_issue(
            replace_mode=True,
            **test_issue_data,
            **archive_rules
        )
        assert (archive_document.show_lines()[-1]
                == replaced_result)
        test_issue_data["issue_id"] = 2

        archive_document.archive_issue(
            replace_mode=True,
            **test_issue_data,
            **archive_rules
        )
        assert (archive_document.show_new_line()[-1]
                == not_replaced_result)
        
        archive_document.archive_issue(
            replace_mode=True,
            **test_issue_data_no_url,
            **archive_rules
        )
        assert (archive_document.show_new_line()[-1]
                == not_replaced_result_no_url)

    def test_save(
        self,
        archive_document: ArchiveDocument,
        tmp_path: Path
    ):
        test_lines = ["123", "5555", "", ""]

        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        test_file = test_dir / "test.md"
        test_file.write_text(
            "\n".join(test_lines),
            encoding="utf-8"
        )
        archive_document.file_load(str(test_file))
        archive_document.save()

        assert (test_file.read_text(
            encoding="utf-8").split("\n") == test_lines)
        test_file.unlink(missing_ok=True)

        test_file.write_text(
            "\n".join(test_lines),
            encoding="utf-8"
        )
        archive_document.add_new_line("6666")
        archive_document.file_load(str(test_file))
        archive_document.save()

        expected_lines = [
            "123",
            "5555",
            "6666",
            ""
        ]
        assert (test_file.read_text(
            encoding="utf-8").split("\n") == expected_lines)
