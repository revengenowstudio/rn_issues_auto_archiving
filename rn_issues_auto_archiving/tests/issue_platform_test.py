import os

import pytest
from issue_processor.issue_platform import Github, Gitlab, Platform
from shared.env import Env


class TestPlatform():
    @staticmethod
    def test_issue_number_to_int():
        assert Platform.issue_number_to_int(
            "123") == 123
        with pytest.raises(ValueError):
            Platform.issue_number_to_int("abc")


@pytest.fixture(scope="class")
def setup_github_environment():
    os.environ[Env.TOKEN] = ""
    os.environ[Env.ISSUE_OUTPUT_PATH] = ""
    os.environ[Env.CI_EVENT_TYPE] = ""
    os.environ[Env.MANUAL_ISSUE_NUMBER] = ""
    os.environ[Env.MANUAL_ISSUE_TITLE] = ""
    os.environ[Env.MANUAL_ISSUE_STATE] = ""
    os.environ[Env.INTRODUCED_VERSION] = ""
    os.environ[Env.ARCHIVE_VERSION] = ""
    os.environ[Env.ISSUE_TYPE] = ""
    os.environ[Env.MANUAL_ISSUE_URL] = ""
    os.environ[Env.MANUAL_COMMENTS_URL] = ""
    os.environ[Env.ISSUE_NUMBER] = ""
    os.environ[Env.ISSUE_TITLE] = ""
    os.environ[Env.ISSUE_STATE] = ""
    os.environ[Env.ISSUE_BODY] = ""
    os.environ[Env.ISSUE_URL] = ""
    os.environ[Env.COMMENTS_URL] = ""


@pytest.mark.usefixtures("setup_github_environment")
class TestGithub():
    @pytest.fixture(autouse=True)
    def setup(self, calculator):
        self.calculator = calculator
        self.resource = "initialized resource"
        print("Resource initialized")

    def teardown(self):
        print("Resource cleaned up")
        del self.resource


def setup_gitlab_environment():
    os.environ[Env.TOKEN]
    os.environ[Env.CI_EVENT_TYPE]
    os.environ[Env.ISSUE_OUTPUT_PATH]
    os.environ.get(Env.ISSUE_NUMBER, "")
    os.environ.get(Env.ISSUE_TITLE, "").strip(),
    os.environ[Env.ISSUE_STATE]),
        os.environ.get(
    os.environ.get(Env.ISSUE_TYPE,
                   os.environ[Env.API_BASE_URL]
                   os.environ[Env.WEBHOOK_PAYLOAD]
                   os.environ[Env.API_BASE_URL]}


@pytest.mark.usefixtures("setup_gitlab_environment")
class TestGitlab():
