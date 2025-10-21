import os
import pytest
from unittest.mock import patch, MagicMock

from issue_processor.issues_processor import IssueProcessor
from issue_processor.git_service_client import (
    GitServiceClient,
    GithubClient,
    GitlabClient,
)
from shared.env import Env
from shared.issue_state import IssueState
from shared.exception import MissingArchiveVersionAndArchiveLabel, UnexpectedPlatform
from shared.issue_info import AUTO_ISSUE_TYPE, IssueInfo
from shared.json_config import Config


class TestIssueProcessor:
    def test_init_config(self):
        config_manager = MagicMock()
        config_manager.load_all.return_value = None
        assert isinstance(IssueProcessor.init_config(config_manager), Config)
        config_manager.load_all.assert_called()

        error_message = "test error"
        config_manager.load_all.side_effect = Exception(error_message)
        with pytest.raises(Exception, match=error_message):
            IssueProcessor.init_config(config_manager)

    @pytest.mark.parametrize(
        "test_platform_type, expected_result",
        [
            (None, None),
            ("github", GithubClient),
            ("gitlab", GitlabClient),
        ],
    )
    def test_init_git_service_client_with_test_platform_type(
        self,
        test_platform_type: str | None,
        expected_result: type[GitServiceClient] | None,
    ):
        config = Config()
        with patch.dict(
            os.environ, {Env.GITHUB_ACTIONS: "false", Env.GITLAB_CI: "false"}
        ):
            if expected_result is None:
                with pytest.raises(UnexpectedPlatform):
                    IssueProcessor.init_git_service_client(test_platform_type, config)
            else:
                assert isinstance(
                    IssueProcessor.init_git_service_client(test_platform_type, config),
                    expected_result,
                )

    def test_init_git_service_client_with_env(
        self,
    ):
        config = Config()
        with patch(
            "issue_processor.issues_processor.should_run_in_github_action"
        ) as should_run_in_github_action:
            with patch(
                "issue_processor.issues_processor.should_run_in_gitlab_ci"
            ) as should_run_in_gitlab_ci:
                should_run_in_github_action.return_value = True
                should_run_in_gitlab_ci.return_value = False
                assert isinstance(
                    IssueProcessor.init_git_service_client(None, config), GithubClient
                )

                should_run_in_github_action.return_value = False
                should_run_in_gitlab_ci.return_value = True
                assert isinstance(
                    IssueProcessor.init_git_service_client(None, config), GitlabClient
                )

                should_run_in_github_action.return_value = False
                should_run_in_gitlab_ci.return_value = False
                with pytest.raises(UnexpectedPlatform):
                    IssueProcessor.init_git_service_client(None, config)

    @pytest.mark.parametrize(
        "platform_type,data_source_type",
        [
            (MagicMock(spec=GitServiceClient), None),
            (
                GithubClient("test"),
                "issue_processor.issue_data_source.GithubIssueDataSource.load",
            ),
            (
                GitlabClient("test"),
                "issue_processor.issue_data_source.GitlabIssueDataSource.load",
            ),
        ],
    )
    def test_init_issue_info(
        self,
        platform_type: GitServiceClient,
        data_source_type: str,
    ):
        if data_source_type is None:
            with pytest.raises(UnexpectedPlatform):
                IssueProcessor.init_issue_info(platform_type)
            return

        with patch(data_source_type) as data_source_obj:
            IssueProcessor.init_issue_info(platform_type)
            assert data_source_obj.called == True

    @pytest.mark.parametrize(
        "should_ci_running_in_issue_event,\
        should_ci_running_in_manual,\
        should_archive_issue,\
        issue_state,\
        archive_version,\
        expect_result",
        [
            # 以下测试数据分别为：
            # 是否自动运行流水线,是否手动运行流水线,是否为归档对象,issue_state,归档版本号,预期结果
            (
                False,
                True,
                False,
                IssueState.closed,
                "",
                MissingArchiveVersionAndArchiveLabel,
            ),
            (
                False,
                True,
                False,
                IssueState.open,
                "",
                MissingArchiveVersionAndArchiveLabel,
            ),
            (False, True, False, IssueState.closed, "0.99.918", False),
            (False, True, False, IssueState.open, "0.99.918", False),
            (False, True, True, IssueState.closed, "", False),
            (False, True, True, IssueState.open, "", False),
            (False, True, True, IssueState.closed, "0.99.918", False),
            (False, True, True, IssueState.open, "0.99.918", False),
            (True, False, False, IssueState.closed, "", True),
            (True, False, False, IssueState.open, "", True),
            (True, False, False, IssueState.closed, "0.99.918", True),
            (True, False, False, IssueState.open, "0.99.918", True),
            (True, False, True, IssueState.closed, "", False),
            (True, False, True, IssueState.open, "", True),
            (True, False, True, IssueState.closed, "0.99.918", False),
            (True, False, True, IssueState.open, "0.99.918", True),
            # IssueState 是 update 通通返回 True
            (False, True, False, IssueState.update, "", True),
            (False, True, False, IssueState.update, "0.99.918", True),
            (False, True, True, IssueState.update, "", True),
            (False, True, True, IssueState.update, "0.99.918", True),
            (True, False, False, IssueState.update, "", True),
            (True, False, False, IssueState.update, "0.99.918", True),
            (True, False, True, IssueState.update, "", True),
            (True, False, True, IssueState.update, "0.99.918", True),
        ],
    )
    def test_verify_not_archived_object(
        self,
        should_ci_running_in_issue_event: bool,
        should_ci_running_in_manual: bool,
        should_archive_issue: bool,
        issue_state: str,
        archive_version: str,
        expect_result: bool | type[Exception],
    ):
        issue_info = MagicMock()
        config = MagicMock()

        with patch(
            "shared.ci_event_type.CiEventType.should_ci_running_in_issue_event"
        ) as should_ci_running_in_issue_event_method:
            with patch(
                "shared.ci_event_type.CiEventType.should_ci_running_in_manual"
            ) as should_ci_running_in_manual_method:
                should_ci_running_in_issue_event_method.return_value = (
                    should_ci_running_in_issue_event
                )
                should_ci_running_in_manual_method.return_value = (
                    should_ci_running_in_manual
                )
                issue_info.should_archive_issue.return_value = should_archive_issue
                issue_info.issue_state = issue_state
                issue_info.archive_version = archive_version

                if not isinstance(expect_result, bool):
                    with pytest.raises(expect_result):
                        IssueProcessor.verify_not_archived_object(issue_info, config)
                else:
                    assert (
                        IssueProcessor.verify_not_archived_object(issue_info, config)
                        == expect_result
                    )

    def test_gather_info_from_issue(self):
        issue_info = MagicMock()
        config = MagicMock()

        test_data = "test_data"

        issue_info.get_issue_type_from_labels.return_value = test_data
        issue_info.get_introduced_version_from_description.return_value = test_data
        issue_info.get_archive_version_from_comments.return_value = test_data
        issue_info.issue_type = AUTO_ISSUE_TYPE
        issue_info.introduced_version = ""
        gather_info = IssueProcessor.gather_info_from_issue(issue_info, config)
        assert gather_info.issue_type == test_data
        assert gather_info.introduced_version == test_data
        assert gather_info.archive_version == test_data

        test_issue_type = "Bug修复"
        test_introduced_version = "0.99.918"
        issue_info.issue_type = test_issue_type
        issue_info.introduced_version = test_introduced_version
        gather_info = IssueProcessor.gather_info_from_issue(issue_info, config)
        assert gather_info.issue_type == test_issue_type
        assert gather_info.introduced_version == test_introduced_version
        assert gather_info.archive_version == test_data

    def test_update_issue_info_with_gather_info(self):
        gather_info = IssueProcessor.GatherInfo()
        issue_info = IssueInfo()
        gather_info.issue_type = "Bug修复"
        gather_info.introduced_version = "0.99.916"
        gather_info.archive_version = "0.99.918"
        IssueProcessor.update_issue_info_with_gather_info(issue_info, gather_info)
        assert issue_info.issue_type == gather_info.issue_type
        assert issue_info.introduced_version == gather_info.introduced_version
        assert issue_info.archive_version == gather_info.archive_version

    def test_parse_issue_info_for_archived(self):
        issue_info = MagicMock()
        issue_info.remove_issue_type_in_issue_title.return_value = "test_title"
        issue_info.update.return_value = None
        config = MagicMock()

        IssueProcessor.parse_issue_info_for_archived(issue_info, config)
        assert issue_info.remove_issue_type_in_issue_title.called
        assert issue_info.update.called

    def test_close_issue_if_not_closed(self):
        issue_info = MagicMock()
        with patch(
            "shared.ci_event_type.CiEventType.should_ci_running_in_manual"
        ) as should_ci_running_in_manual_method:
            should_ci_running_in_manual_method.return_value = True
            issue_info.issue_state = IssueState.open
            platform = MagicMock()
            platform.close_issue.return_value = None
            IssueProcessor.close_issue_if_not_closed(issue_info, platform)
            assert platform.close_issue.called
            del platform

            should_ci_running_in_manual_method.return_value = True
            issue_info.issue_state = IssueState.closed
            platform = MagicMock()
            platform.close_issue.return_value = None
            IssueProcessor.close_issue_if_not_closed(issue_info, platform)
            assert platform.close_issue.called is False
            del platform

            should_ci_running_in_manual_method.return_value = False
            platform = MagicMock()
            platform.close_issue.return_value = None
            IssueProcessor.close_issue_if_not_closed(issue_info, platform)
            assert platform.close_issue.called is False
            del platform

    def test_should_skip_archived_process(self):
        issue_info = MagicMock()
        issue_info.should_skip_archived_process.return_value = True
        reges = ["1", "2"]
        assert IssueProcessor().should_skip_archived_process(issue_info, reges) == True
        issue_info.should_skip_archived_process.return_value = False
        assert IssueProcessor().should_skip_archived_process(issue_info, []) == False
