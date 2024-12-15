import json
import os
import pytest
from http import HTTPStatus
from unittest.mock import patch, MagicMock

import httpx

from issue_processor.git_service_client import GitServiceClient, GithubClient, GitlabClient, Issue, get_issue_id_from_url
from shared.env import Env
from shared.issue_info import IssueInfo
from shared.log import Log


def test_get_issue_id_from_url():
    assert get_issue_id_from_url(
        "https://api.example.com/owner/repo/issues/123456"
    ) == 123456


class TestGitServiceClient():

    @pytest.fixture(scope="function")
    def git_service_client(self) -> GitServiceClient:
        client = GithubClient("test_token")
        client._http_client = MagicMock()
        return client

    @pytest.fixture(scope="function")
    def http_request_parameters(self) -> dict[str, str | int | dict]:
        return {
            "url": "https://example.com/api",
            "method": "GET",
            "params": "GET",
            "json_content": "GET",
            "retry_times": 4,
        }

    def test_successful_request(
        self,
        git_service_client: GitServiceClient,
        http_request_parameters,
    ):
        # 模拟成功的 HTTP 请求
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK  # 200
        mock_response.raise_for_status.return_value = None
        git_service_client._http_client.request.return_value = mock_response

        response = git_service_client.http_request(
            **http_request_parameters
        )

        # 验证请求成功返回
        assert response == mock_response

    def test_404_not_found(
            self,
            git_service_client: GitServiceClient,
            http_request_parameters,
    ):
        # 模拟 404 Not Found 错误
        error_message = "Not Found"
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND  # 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            error_message, request=MagicMock(), response=mock_response)
        git_service_client._http_client.request.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError,
                           match=error_message):
            git_service_client.http_request(
                **http_request_parameters
            )

    def test_http_status_error(
            self,
            git_service_client: GitServiceClient,
            http_request_parameters,
    ):
        # 模拟其他 HTTP 错误
        error_message = "Bad Request"
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST  # 400
        mock_response.json.return_value = {'error': error_message}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response)
        git_service_client._http_client.request.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError,
                           match=error_message) as context:
            git_service_client.http_request(
                **http_request_parameters
            )

        # 验证日志输出
        context.match(error_message)

    def test_retry_on_exception(
            self,
            git_service_client: GitServiceClient,
            http_request_parameters,
    ):
        # 模拟未知异常并测试重试机制
        # 验证最后一次请求成功返回
        error_message = "Network error"
        mock_response_list = [
            Exception(error_message)] * (http_request_parameters["retry_times"] - 1)
        mock_response_list.append(MagicMock(status_code=HTTPStatus.OK))
        git_service_client._http_client.request.side_effect = mock_response_list

        response = git_service_client.http_request(
            **http_request_parameters
        )

        assert (git_service_client._http_client.request.call_count
                == http_request_parameters["retry_times"])
        assert response.status_code == HTTPStatus.OK

    def test_max_retries_exceeded(
            self,
            git_service_client: GitServiceClient,
            http_request_parameters,
    ):
        # 模拟未知异常并测试重试次数用完后抛出异常
        error_message = "Network error"
        git_service_client._http_client.request.side_effect = [
            Exception(error_message)] * http_request_parameters["retry_times"]

        with pytest.raises(Exception,
                           match=error_message):
            git_service_client.http_request(
                **http_request_parameters
            )

        # 验证抛出的异常是最后一次引发的异常
        assert (git_service_client._http_client.request.call_count
                == http_request_parameters["retry_times"])

    def test_enrich_missing_issue_info(
        self,
        git_service_client: GitServiceClient,
    ):
        test_issue_comments = [IssueInfo.Comment(body="test_comment")] * 2
        test_issue_labels = ["test_label"] * 2
        test_issue_state = "test_state"
        test_issue_title = "test_title"
        test_issue_body = "test_body"
        test_issue_web_url = "test_url"
        return_issue = Issue(
            id=123456,
            title=test_issue_title,
            state=test_issue_state,
            body=test_issue_body,
            labels=test_issue_labels,
            issue_web_url=test_issue_web_url
        )
        issue_info = MagicMock()

        with patch("shared.ci_event_type.CiEventType.should_ci_running_in_manual") as should_ci_running_in_manual:
            with patch.object(git_service_client, "_get_comments_from_platform") as _get_comments_from_platform:
                with patch.object(git_service_client, "_get_issue_info_from_platform") as _get_issue_info_from_platform:
                    should_ci_running_in_manual.return_value = False
                    _get_comments_from_platform.return_value = test_issue_comments
                    _get_issue_info_from_platform.return_value = return_issue
                    git_service_client.enrich_missing_issue_info(issue_info)
                    assert issue_info.issue_comments == test_issue_comments
                    assert issue_info.issue_labels == test_issue_labels
                    assert issue_info.links.issue_web_url == test_issue_web_url

                    should_ci_running_in_manual.return_value = True
                    issue_info.issue_title = ""
                    issue_info.issue_body = ""
                    git_service_client.enrich_missing_issue_info(issue_info)
                    assert issue_info.issue_state == test_issue_state
                    assert issue_info.issue_title == test_issue_title
                    assert issue_info.issue_body == test_issue_body

                    should_ci_running_in_manual.return_value = True
                    test_data = "test_data"
                    issue_info.issue_title = test_data
                    issue_info.issue_body = test_data
                    git_service_client.enrich_missing_issue_info(issue_info)
                    assert issue_info.issue_state == test_issue_state
                    assert issue_info.issue_title == test_data
                    assert issue_info.issue_body == test_data

    def test_send_comment(
        self,
        git_service_client: GitServiceClient,
    ):
        with patch.object(
            git_service_client, "http_request"
        ) as http_request:
            http_request.return_value = None
            git_service_client.send_comment(
                comment_url="https://example.com",
                comment_body="test_comment"
            )
            assert http_request.call_count == 1

    class TestGithubClient():

        @pytest.fixture(scope="function")
        def github_client(self):
            client = GithubClient(token="test_token")
            client._http_client = MagicMock()
            return client

        def test_create_http_header(
            self,
            github_client: GithubClient
        ):
            assert github_client.create_http_header("test_token") == {
                "Authorization": f"Bearer {github_client._token}",
                "Accept": "application/vnd.github+json"
            }

        def test__get_comments_from_platform(
            self,
            github_client: GithubClient
        ):
            comment_json = [
                {
                    "user": {
                        "login": "test_user"
                    },
                    "body": "test_comment"
                }
            ] * 2
            mock_response = MagicMock()
            mock_response.json.return_value = comment_json
            mock_empty_response = MagicMock()
            mock_empty_response.json.return_value = []
            with patch.object(
                github_client,
                "http_request"
            ) as http_request:
                test_response_list = [mock_response] * 2
                test_response_list.append(mock_empty_response)
                http_request.side_effect = test_response_list

                comments = github_client._get_comments_from_platform(
                    "https://example.com"
                )
                assert len(comments) == 4
                assert http_request.call_count == 3

        def test__get_issue_info_from_platform(
            self,
            github_client: GithubClient
        ):
            test_issue_data = {
                "id": 123,
                "title": "test_title",
                "state": "test_state",
                "body": "_test_body",
                "labels": [
                    {
                        "name": "test_label"
                    },
                    {
                        "name": "test_label2"
                    }
                ],
                "html_url": "test_url"
            }
            mock_response = MagicMock()
            mock_response.json.return_value = test_issue_data
            with patch.object(
                github_client,
                "http_request"
            ) as http_request:
                http_request.return_value = mock_response
                issue = github_client._get_issue_info_from_platform(
                    "https://example.com"
                )
                assert issue.id == test_issue_data["id"]
                assert issue.title == test_issue_data["title"]
                assert issue.state == test_issue_data["state"]
                assert issue.body == test_issue_data["body"]
                assert len(issue.labels) == len(test_issue_data["labels"])
                assert issue.issue_web_url == test_issue_data["html_url"]

        def test_reopen_issue(
            self,
            github_client: GithubClient
        ):
            with patch.object(
                github_client,
                "http_request"
            ) as http_request:
                http_request.return_value = None
                github_client.reopen_issue(
                    "https://api.example.com/owner/repo/issues/123"
                )
                assert http_request.call_count == 1

        def test_close_issue(
            self,
            github_client: GithubClient
        ):
            with patch.object(
                github_client,
                "http_request"
            ) as http_request:
                http_request.return_value = None
                github_client.close_issue(
                    "https://api.example.com/owner/repo/issues/123"
                )
                assert http_request.call_count == 1

    class TestGitlabClient():
        @pytest.fixture(scope="function")
        def gitlab_client(self):
            client = GitlabClient(token="test_token")
            client._http_client = MagicMock()
            return client

        def test_should_issue_type_webhook(self):
            with patch.dict(
                os.environ,
                {
                    Env.WEBHOOK_PAYLOAD: json.dumps({
                        "event_name": "issue"
                    }, ensure_ascii=False)
                }
            )as environ:
                assert GitlabClient.should_issue_type_webhook()

                environ[Env.WEBHOOK_PAYLOAD] = json.dumps({
                    "event_name": "trigger"
                }, ensure_ascii=False)
                assert GitlabClient.should_issue_type_webhook() is False

                environ.pop(Env.WEBHOOK_PAYLOAD)
                assert GitlabClient.should_issue_type_webhook()

        def test_create_http_header(
            self,
            gitlab_client: GitlabClient
        ):
            assert gitlab_client.create_http_header("test_token") == {
                "Authorization": f"Bearer {gitlab_client._token}",
                "Content-Type": "application/json"
            }

        def test__get_comments_from_platform(
            self,
            gitlab_client: GitlabClient
        ):
            comment_json = [
                {
                    "author": {
                        "username": "test_user"
                    },
                    "body": "test_comment"
                }
            ] * 2
            mock_response = MagicMock()
            mock_response.json.return_value = comment_json
            mock_empty_response = MagicMock()
            mock_empty_response.json.return_value = []
            with patch.object(
                gitlab_client,
                "http_request"
            ) as http_request:
                test_response_list = [mock_response] * 2
                test_response_list.append(mock_empty_response)
                http_request.side_effect = test_response_list

                comments = gitlab_client._get_comments_from_platform(
                    "https://example.com"
                )
                assert len(comments) == 4
                assert http_request.call_count == 3

        def test__get_issue_info_from_platform(
            self,
            gitlab_client: GitlabClient
        ):
            test_issue_data = {
                "iid": 123,
                "title": "test_title",
                "state": "closed",
                "description": "_test_body",
                "labels": [
                    "test_label",
                    "test_label2"
                ],
                "web_url": "test_url"
            }
            mock_response = MagicMock()
            mock_response.json.return_value = test_issue_data
            with patch.object(
                gitlab_client,
                "http_request"
            ) as http_request:
                http_request.return_value = mock_response
                issue = gitlab_client._get_issue_info_from_platform(
                    "https://example.com"
                )
                assert issue.id == test_issue_data["iid"]
                assert issue.title == test_issue_data["title"]
                assert issue.state == test_issue_data["state"]
                assert issue.body == test_issue_data["description"]
                assert len(issue.labels) == len(test_issue_data["labels"])
                assert issue.issue_web_url == test_issue_data["web_url"]

        def test_reopen_issue(
            self,
            gitlab_client: GitlabClient
        ):
            with patch.object(
                gitlab_client,
                "http_request"
            ) as http_request:
                http_request.return_value = None
                gitlab_client.reopen_issue(
                    "https://api.example.com/owner/repo/issues/123"
                )
                assert http_request.call_count == 1

        def test_close_issue(
            self,
            gitlab_client: GitlabClient
        ):
            with patch.object(
                gitlab_client,
                "http_request"
            ) as http_request:
                http_request.return_value = None
                gitlab_client.close_issue(
                    "https://api.example.com/owner/repo/issues/123"
                )
                assert http_request.call_count == 1
