import pytest
import os
import json
from unittest.mock import patch

from issue_processor.issue_data_source import (
    GithubIssueDataSource,
    GitlabIssueDataSource,
    issue_number_to_int,
)
from shared.exception import MissingIssueNumber, WebhookPayloadError
from shared.api_path import ApiPath
from shared.issue_state import parse_issue_state
from shared.env import Env
from shared.issue_info import IssueInfo


class TestIssueData:
    github_auto_ci_issue_data = {
        Env.CI_EVENT_TYPE: "issues",
        Env.ISSUE_REPOSITORY: "外部Issue",
        Env.ISSUE_NUMBER: "2",
        Env.ISSUE_TITLE: "test_title",
        Env.ISSUE_STATE: "open",
        Env.ISSUE_BODY: "test_body",
        Env.ISSUE_URL: "https://api.example.com/issue/2",
        Env.COMMENTS_URL: "https://api.example.com/issue/2/comments",
    }
    github_manual_ci_issue_data = {
        Env.CI_EVENT_TYPE: "workflow_dispatch",
        Env.ISSUE_REPOSITORY: "外部Issue",
        Env.MANUAL_ISSUE_NUMBER: "2",
        Env.MANUAL_ISSUE_TITLE: "test_title",
        Env.MANUAL_ISSUE_STATE: "open",
        Env.INTRODUCED_VERSION: "0.99.916",
        Env.ARCHIVE_VERSION: "0.99.918",
        Env.ISSUE_TYPE: "Bug修复",
        Env.MANUAL_ISSUE_URL: "https://api.example.com/issue/2",
        Env.MANUAL_COMMENTS_URL: "https://api.example.com/issue/2/comments",
    }
    gitlab_auto_ci_issue_data = {
        Env.CI_EVENT_TYPE: "trigger",
        Env.ISSUE_REPOSITORY: "内部Issue",
        Env.WEBHOOK_PAYLOAD: json.dumps(
            {
                "object_kind": "issue",
                "event_type": "issue",
                "user": {
                    "id": 5,
                    "name": "test_user",
                    "username": "test_user",
                    "avatar_url": "https://gitlab.example.com/uploads/-/system/user/avatar/5/avatar.png",
                    "email": "[REDACTED]",
                },
                "project": {
                    "id": 17,
                    "name": "rn_issues_auto_archiving",
                    "description": "",
                    "web_url": "https://gitlab.example.com/example-group/regular-developers/example-repository",
                    "avatar_url": None,
                    "git_ssh_url": "git@gitlab.example.com:example-group/regular-developers/example-repository.git",
                    "git_http_url": "https://gitlab.example.com/example-group/regular-developers/example-repository.git",
                    "namespace": "Regular Developers",
                    "visibility_level": 0,
                    "path_with_namespace": "example-group/regular-developers/example-repository",
                    "default_branch": "main",
                    "ci_config_path": None,
                    "homepage": "https://gitlab.example.com/example-group/regular-developers/example-repository",
                    "url": "git@gitlab.example.com:example-group/regular-developers/example-repository.git",
                    "ssh_url": "git@gitlab.example.com:example-group/regular-developers/example-repository.git",
                    "http_url": "https://gitlab.example.com/example-group/regular-developers/example-repository.git",
                },
                "object_attributes": {
                    "author_id": 5,
                    "closed_at": "2024-12-12 13:00:25 UTC",
                    "confidential": False,
                    "created_at": "2024-11-22 04:00:42 UTC",
                    "description": "【描述】如题  \n【反馈人】：test_user   \n【发现版本号】：0.99.954b9   \n【影响范围】：cncnet客户端   \n【产生原因】：当客户端更新列表中第一个更新服务器失效的时候，排在后面的更新服务器即使能使用也不能正常更新。",
                    "discussion_locked": None,
                    "due_date": None,
                    "id": 959,
                    "iid": 2,
                    "last_edited_at": "2024-11-22 05:14:56 UTC",
                    "last_edited_by_id": 5,
                    "milestone_id": None,
                    "moved_to_id": None,
                    "duplicated_to_id": None,
                    "project_id": 17,
                    "relative_position": 223668,
                    "state_id": 2,
                    "time_estimate": 0,
                    "title": "这是一个测试issue标题",
                    "updated_at": "2024-12-12 13:00:25 UTC",
                    "updated_by_id": 5,
                    "type": "Issue",
                    "url": "https://gitlab.example.com/example-group/regular-developers/example-repository/-/issues/2",
                    "total_time_spent": 0,
                    "time_change": 0,
                    "human_total_time_spent": None,
                    "human_time_change": None,
                    "human_time_estimate": None,
                    "assignee_ids": [],
                    "assignee_id": None,
                    "labels": [
                        {
                            "id": 45,
                            "title": "bug",
                            "color": "#dc143c",
                            "project_id": 17,
                            "created_at": "2024-11-08 03:00:32 UTC",
                            "updated_at": "2024-11-22 04:00:58 UTC",
                            "template": False,
                            "description": "",
                            "type": "ProjectLabel",
                            "group_id": None,
                        },
                        {
                            "id": 47,
                            "title": "resolved 已解决",
                            "color": "#6699cc",
                            "project_id": 17,
                            "created_at": "2024-11-08 11:16:04 UTC",
                            "updated_at": "2024-11-08 11:16:04 UTC",
                            "template": False,
                            "description": None,
                            "type": "ProjectLabel",
                            "group_id": None,
                        },
                    ],
                    "state": "closed",
                    "severity": "unknown",
                    "customer_relations_contacts": [],
                    "action": "close",
                },
                "labels": [
                    {
                        "id": 45,
                        "title": "bug",
                        "color": "#dc143c",
                        "project_id": 17,
                        "created_at": "2024-11-08 03:00:32 UTC",
                        "updated_at": "2024-11-22 04:00:58 UTC",
                        "template": False,
                        "description": "",
                        "type": "ProjectLabel",
                        "group_id": None,
                    },
                    {
                        "id": 47,
                        "title": "resolved 已解决",
                        "color": "#6699cc",
                        "project_id": 17,
                        "created_at": "2024-11-08 11:16:04 UTC",
                        "updated_at": "2024-11-08 11:16:04 UTC",
                        "template": False,
                        "description": None,
                        "type": "ProjectLabel",
                        "group_id": None,
                    },
                ],
                "changes": {
                    "closed_at": {
                        "previous": None,
                        "current": "2024-12-12 13:00:25 UTC",
                    },
                    "state_id": {"previous": 1, "current": 2},
                    "updated_at": {
                        "previous": "2024-12-12 13:00:12 UTC",
                        "current": "2024-12-12 13:00:25 UTC",
                    },
                },
                "repository": {
                    "name": "rn_issues_auto_archiving",
                    "url": "git@gitlab.example.com:example-group/regular-developers/example-repository.git",
                    "description": "",
                    "homepage": "https://gitlab.example.com/example-group/regular-developers/example-repository",
                },
            },
            ensure_ascii=False,
        ),
        Env.API_BASE_URL: "https://giltab.example.com/api/v4/projects/123456/",
    }
    gitlab_manual_ci_issue_data = {
        Env.CI_EVENT_TYPE: "web",
        Env.ISSUE_REPOSITORY: "内部Issue",
        Env.ISSUE_NUMBER: "2",
        Env.ISSUE_TITLE: "test_title",
        Env.ISSUE_STATE: "open",
        Env.INTRODUCED_VERSION: "0.99.916",
        Env.ARCHIVE_VERSION: "0.99.918",
        Env.ISSUE_TYPE: "Bug修复",
        Env.API_BASE_URL: "https://giltab.example.com/api/v4/projects/123456/",
    }


@pytest.mark.parametrize(
    "test_data,expected_result",
    [
        ("1", 1),
        ("2.", None),
        ("2.13", None),
        ("str", None),
        ("  ", None),
        ("#1", None),
    ],
)
def test_issue_number_to_int(test_data: str, expected_result: int | None):
    if expected_result is None:
        with pytest.raises(ValueError):
            issue_number_to_int(test_data)
    else:
        assert issue_number_to_int(test_data) == expected_result


class TestGithubIssueDataSource:
    @pytest.fixture()
    def github_issue_data_source(self):
        return GithubIssueDataSource()

    def test_load(self, github_issue_data_source: GithubIssueDataSource):
        # 自动触发流水线
        with patch.dict(os.environ, TestIssueData.github_auto_ci_issue_data):
            issue_info = IssueInfo()

            github_issue_data_source.load(issue_info)
            assert issue_info.ci_event_type == os.environ[Env.CI_EVENT_TYPE]
            assert issue_info.issue_repository == os.environ[Env.ISSUE_REPOSITORY]
            assert issue_info.issue_id == int(os.environ[Env.ISSUE_NUMBER])
            assert issue_info.issue_title == os.environ[Env.ISSUE_TITLE]
            assert issue_info.issue_state == parse_issue_state(
                os.environ[Env.ISSUE_STATE]
            )
            assert issue_info.issue_body == os.environ[Env.ISSUE_BODY]
            assert issue_info.links.issue_url == os.environ[Env.ISSUE_URL]
            assert issue_info.links.comment_url == os.environ[Env.COMMENTS_URL]

            del issue_info

        # 手动触发流水线
        with patch.dict(os.environ, TestIssueData.github_manual_ci_issue_data):
            issue_info = IssueInfo()

            github_issue_data_source.load(issue_info)
            assert issue_info.ci_event_type == os.environ[Env.CI_EVENT_TYPE]
            assert issue_info.issue_repository == os.environ[Env.ISSUE_REPOSITORY]
            assert issue_info.issue_id == issue_number_to_int(
                os.environ[Env.MANUAL_ISSUE_NUMBER]
            )
            assert issue_info.issue_title == os.environ[Env.MANUAL_ISSUE_TITLE].strip()
            assert issue_info.issue_state == parse_issue_state(
                os.environ[Env.MANUAL_ISSUE_STATE]
            )
            assert (
                issue_info.introduced_version
                == os.environ[Env.INTRODUCED_VERSION].strip()
            )
            assert issue_info.archive_version == os.environ[Env.ARCHIVE_VERSION].strip()
            assert issue_info.issue_type == os.environ[Env.ISSUE_TYPE]
            assert issue_info.links.issue_url == os.environ[Env.MANUAL_ISSUE_URL]
            assert issue_info.links.comment_url == os.environ[Env.MANUAL_COMMENTS_URL]

            del issue_info


class TestGitlabIssueDataSource:
    @pytest.fixture()
    def gitlab_issue_data_source(self):
        return GitlabIssueDataSource()

    def test_load(self, gitlab_issue_data_source: GithubIssueDataSource):
        # 自动触发流水线
        with patch.dict(os.environ, TestIssueData.gitlab_auto_ci_issue_data):
            issue_info = IssueInfo()

            gitlab_issue_data_source.load(issue_info)
            webhook_payload = json.loads(os.environ[Env.WEBHOOK_PAYLOAD])
            # webhook里是json，iid一定是int
            assert issue_info.issue_id == webhook_payload["object_attributes"]["iid"]
            assert (
                issue_info.issue_title == webhook_payload["object_attributes"]["title"]
            )
            assert issue_info.issue_state == parse_issue_state(
                webhook_payload["object_attributes"]["action"]
            )
            assert (
                issue_info.issue_body
                == webhook_payload["object_attributes"]["description"]
            )
            assert issue_info.issue_labels == [
                label_json["title"]
                for label_json in webhook_payload["object_attributes"]["labels"]
            ]

            del issue_info

        # 手动触发流水线
        with patch.dict(os.environ, TestIssueData.gitlab_manual_ci_issue_data):
            issue_info = IssueInfo()

            gitlab_issue_data_source.load(issue_info)
            assert issue_info.ci_event_type == os.environ[Env.CI_EVENT_TYPE]
            assert issue_info.issue_repository == os.environ[Env.ISSUE_REPOSITORY]
            assert issue_info.issue_id == (
                issue_id := issue_number_to_int(os.environ[Env.ISSUE_NUMBER])
            )
            assert issue_info.issue_title == os.environ[Env.ISSUE_TITLE].strip()
            assert issue_info.issue_state == parse_issue_state(
                os.environ[Env.ISSUE_STATE]
            )
            assert (
                issue_info.introduced_version
                == os.environ[Env.INTRODUCED_VERSION].strip()
            )
            assert issue_info.archive_version == os.environ[Env.ARCHIVE_VERSION].strip()
            assert issue_info.issue_type == os.environ[Env.ISSUE_TYPE].strip()
            assert issue_info.links.issue_url == (
                issue_url := GitlabIssueDataSource.build_issue_url(
                    issue_id, os.environ[Env.API_BASE_URL]
                )
            )
            assert issue_info.links.comment_url == issue_url + "/" + ApiPath.notes

            del issue_info

        without_webhook_json_data = TestIssueData.gitlab_auto_ci_issue_data.copy()
        # without_webhook_json_data.pop(Env.WEBHOOK_PAYLOAD)
        without_webhook_json_data[Env.WEBHOOK_PAYLOAD] = ""
        with patch.dict(os.environ, without_webhook_json_data):
            issue_info = IssueInfo()
            with pytest.raises(WebhookPayloadError):
                gitlab_issue_data_source.load(issue_info)
            del issue_info

        empty_issue_number_data = TestIssueData.gitlab_manual_ci_issue_data.copy()
        empty_issue_number_data[Env.ISSUE_NUMBER] = ""
        with patch.dict(os.environ, empty_issue_number_data):
            issue_info = IssueInfo()
            with pytest.raises(MissingIssueNumber):
                gitlab_issue_data_source.load(issue_info)
