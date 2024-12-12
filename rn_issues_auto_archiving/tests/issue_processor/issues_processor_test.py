import pytest
from unittest.mock import patch, MagicMock

from issue_processor.issues_processor import IssueProcessor
from issue_processor.git_service_client import (
    GithubClient, GitlabClient)
from shared.issue_info import IssueInfo
from shared.json_config import Config


@pytest.fixture()
def config():
    return Config()


@pytest.fixture()
def github_issue_info():
    return IssueInfo()


@pytest.fixture()
def gitlab_issue_info():
    return IssueInfo()


@pytest.fixture()
def github_platform():
    return GithubClient("token")


@pytest.fixture()
def gitlab_platform():
    return GitlabClient("token")


class TestIssueProcessor():

    def test_init_config(self):
        config_manager = MagicMock()
        config_manager.load_all.return_value = None
        assert isinstance(
            IssueProcessor.init_config(config_manager), Config)
        config_manager.load_all.assert_called()
        
        error_message = "test error"
        config_manager.load_all.side_effect = Exception(error_message)
        with pytest.raises(
            Exception,
            match=error_message
        ):
            IssueProcessor.init_config(config_manager)
            
    def test_init_git_service_client(self):
        # TODO 没写完
        pass
