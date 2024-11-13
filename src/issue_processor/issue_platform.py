import os
import re
import json
from dataclasses import dataclass
from abc import abstractmethod, ABC

import httpx

from src.shared.log import Log
from src.shared.env import Env
from src.shared.exception import *
from src.shared.issue_info import IssueInfoJson

ISSUE_STATE_MAP = {
    "closed": "closed",
    "close": "closed",
    "open": "open",
    "opened": "open",
    "reopen": "open",
}
'''将issue_state转换成只有两种状态，
open或closed'''


class IssueState():
    open = "open"
    closed = "closed"


@dataclass()
class Urls():
    issues_url: str
    comments_url: str

    class ApiPath():
        base = "api/v4"
        projects = "projects"
        notes = "notes"


@dataclass()
class Comment():
    author: str
    body: str


@dataclass()
class Issue():
    id: int
    title: str
    state: str
    body: str
    labels: list[str]


@dataclass()
class PlatformEnvironments():
    token: str
    issue_number: int
    issue_title: str
    issue_state: str
    issue_body: str
    issue_url: str
    comments_url: str


class Platform(ABC):

    @abstractmethod
    def create_http_header(self, token: str) -> dict[str, str]:
        pass

    @abstractmethod
    def _get_labels_from_platform(self) -> list[str]:
        pass

    @abstractmethod
    def _get_comments_from_platform(
        self,
        http: httpx.Client,
        url: str,
    ) -> list[Comment]:
        pass

    @abstractmethod
    def reopen_issue(self) -> None:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def _read_platform_environments(self) -> None:
        pass

    @property
    @abstractmethod
    def reopen_issue_method(self) -> str:
        pass

    @property
    @abstractmethod
    def reopen_issue_body(self) -> dict[str, str]:
        pass

    def __init__(self):
        self._token: str
        self._issue: Issue
        self._urls: Urls
        self._comments: list[Comment]
        self._output_path: str
        self._http_client: httpx.Client

    def _parse_issue_state(self) -> None:
        self._issue.state = ISSUE_STATE_MAP[self._issue.state]

    def get_introduced_version(self,
                               introduced_version_reges: list[str]
                               ) -> list[str]:
        print(Log.getting_something_from
              .format(another=Log.issue_description, something=Log.introduced_version))
        result: list[str] = []
        for regex in introduced_version_reges:
            result.extend(
                re.findall(
                    regex,
                    self._issue.body
                )
            )
        result = [item.strip() for item in result]
        return result

    def get_labels(self) -> list[str]:
        return self._issue.labels

    def get_archive_version(
        self,
        comment_reges: list[str]
    ) -> list[str]:
        print(Log.getting_something_from
              .format(another=Log.issue_comment, something=Log.archive_version))
        result: list[str] = []
        for comment in self._comments:
            for comment_regex in comment_reges:
                if len(archive_version := re.findall(
                        comment_regex, comment.body)) > 0:
                    result.extend(archive_version)

        return result

    def send_comment(self, comment_body: str) -> None:
        ''' api结构详见：\n
        Github ： https://docs.github.com/zh/rest/issues/comments?apiVersion=2022-11-28#create-an-issue-comment \n
        Gitlab ： https://docs.gitlab.com/ee/api/notes.html#create-new-issue-note \n
        两边API创建评论所需的参数都是一致的
        '''
        print(Log.sending_something.format(
            something=Log.announcement_comment))
        response = self._http_client.post(
            url=self._urls.comments_url,
            json={
                "body": comment_body
            }
        )
        response.raise_for_status()
        print(Log.sending_something_success
              .format(something=Log.announcement_comment))

    def should_archive_issue(
        self,
        archive_version: list[str],
        issue_labels: list[str],
        target_labels: list[str],
        comment_reges: list[str],

    ) -> bool:

        if should_not_match_archive_version := (
                len(archive_version) == 0):
            print(Log.archive_version_not_found)
        else:
            print(Log.archive_version_found)

        # issue所挂标签必须匹配所有白名单标签
        if should_label_not_in_target := (
                set(issue_labels) & set(target_labels)
                != set(target_labels)):
            print(Log.target_labels_not_found)
        else:
            print(Log.target_labels_found)

        # 未匹配到归档关键字应则不进行归档流程
        # 因为这有可能是用户自行关闭的issue或者无需归档的issue

        if all([should_label_not_in_target, should_not_match_archive_version]):
            return False

        if should_label_not_in_target:
            raise ArchiveLabelError(
                ErrorMessage.missing_archive_labels
                .format(labels=target_labels)
            )

        if should_not_match_archive_version:
            raise ArchiveVersionError(
                ErrorMessage.missing_archive_version
            )

        return True

    def get_issue_type_from_title(
        self,
        type_keyword: dict[str, str]
    ) -> str:
        print(Log.getting_something_from
              .format(another=Log.issue_title, something=Log.issue_type))
        for keyword, type in type_keyword.items():
            if keyword in self._issue.title:
                print(Log.getting_something_from_success
                      .format(another=Log.issue_title,
                              something=Log.issue_type))
                return type

        print(Log.issue_type_not_found)
        raise IssueTypeError(
            ErrorMessage.missing_issue_type_from_title
            .format(issue_type=list(type_keyword.keys()))
        )

    def get_issue_type_from_labels(
            self,
            label_map: dict[str, str]
    ) -> str:
        print(Log.getting_something_from
              .format(another=Log.issue_label, something=Log.issue_type))
        for label_name, type in label_map.items():
            if label_name in self._issue.labels:
                print(Log.getting_something_from_success
                      .format(another=Log.issue_label,
                              something=Log.issue_type))
                return type

        print(Log.issue_type_not_found)
        raise IssueTypeError(
            ErrorMessage.missing_issue_type_from_label
            .format(issue_type=list(label_map.keys()))
        )

    def remove_type_in_issue_title(
            self,
            type_keyword: dict[str, str]
    ) -> None:
        title = self._issue.title
        # 这里不打算考虑issue标题中
        # 匹配多个issue类型关键字的情况
        # 因为这种情况下脚本完全无法判断
        # issue的真实类型是什么
        for key in type_keyword.keys():
            if key in title:
                self._issue.title = title.replace(
                    key, '').strip()
                break

    def parse_archive_version(
        self,
        archive_version: list[str]
    ) -> str:
        if len(archive_version) >= 2:
            print(Log.too_many_archive_version)
            raise ArchiveVersionError(
                ErrorMessage.too_many_archive_version
                .format(versions=[i for i in archive_version])
            )
        print(Log.getting_something_from_success
              .format(another=Log.issue_comment, something=Log.archive_version))
        return archive_version[0]

    def issue_content_to_json(
        self,
        introduced_version: str,
        archive_version: str,
        issue_type: str
    ) -> None:
        json_path = self._output_path
        issue_json = IssueInfoJson(
            issue_id=self._issue.id,
            issue_type=issue_type,
            issue_title=self._issue.title,
            issue_state=self._issue.state,
            archive_version=archive_version,
            introduced_version=introduced_version,
            reopen_info=IssueInfoJson.ReopenInfo(
                http_header=self.create_http_header(self._token),
                reopen_url=self._urls.issues_url,
                reopen_http_method=self.reopen_issue_method,
                reopen_body=self.reopen_issue_body,
                comment_url=self._urls.comments_url,
            )
        )

        

        print(Log.print_issue_json
              .format(issue_json=json.dumps(
                  IssueInfoJson.remove_sensitive_info(issue_json),
                  ensure_ascii=False,
                  indent=4
              )))
        print(Log.save_issue_content_to_file
              .format(output_path=json_path))

        with open(json_path,
                  "w",
                  encoding="utf-8") as file:
            json.dump(
                issue_json,
                file,
                ensure_ascii=False,
                indent=4
            )
        print(Log.save_issue_content_to_file_success
              .format(output_path=json_path))

    def parse_introduced_version(
        self,
        introduced_version: list[str],
        need_introduced_version_issue_type: bool
    ) -> str:

        if len(introduced_version) == 0:
            if not need_introduced_version_issue_type:
                print(Log.introduced_version_not_found)
                return str()

            if need_introduced_version_issue_type:
                print(Log.introduced_version_not_found)
                raise IntroducedVersionError(
                    ErrorMessage.missing_introduced_version
                )

        elif len(introduced_version) >= 2:
            print(Log.too_many_introduced_version)
            raise IntroducedVersionError(
                ErrorMessage.too_many_introduced_version
                .format(versions=[i for i in introduced_version])
            )
        print(Log.getting_something_from_success
              .format(another=Log.issue_description, something=Log.introduced_version))
        return introduced_version[0]


class Github(Platform):

    @property
    def reopen_issue_method(self) -> str:
        return "PATCH"

    @property
    def reopen_issue_body(self) -> dict[str, str]:
        return {
            "state": "open"
        }

    def _read_platform_environments(self) -> None:
        print(Log.loading_something.format(something=Log.env))
        self._token = os.environ[Env.TOKEN]
        self._output_path = os.environ[Env.OUTPUT_PATH]
        self._issue = Issue(
            int(os.environ[Env.ISSUE_NUMBER]),
            os.environ[Env.ISSUE_TITLE],
            os.environ[Env.ISSUE_STATE],
            os.environ[Env.ISSUE_BODY],
            labels=[]
        )
        self._urls = Urls(
            os.environ[Env.ISSUE_URL],
            os.environ[Env.COMMENTS_URL],
        )
        print(Log.loading_something_success
              .format(something=Log.env))

    def create_http_header(self, token: str) -> dict[str, str]:
        ''' 所需http header结构详见：
        https://docs.github.com/zh/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28#example-request-using-query-parameters'''
        return {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json"
        }

    def _get_labels_from_platform(self) -> list[str]:
        ''' 所需http header结构详见：
        https://docs.github.com/zh/rest/issues/issues?apiVersion=2022-11-28#get-an-issue'''
        print(Log.getting_something.
              format(something=Log.issue_label))
        response = self._http_client.get(url=self._urls.issues_url)
        response.raise_for_status()
        print(Log.getting_something_success.
              format(something=Log.issue_label))
        return [label["name"]
                for label in response.json()["labels"]]

    def __init__(self):
        super().__init__()
        self._read_platform_environments()
        self._parse_issue_state()
        self._http_client = httpx.Client(
            headers=self.create_http_header(self._token)
        )
        self._issue.labels = self._get_labels_from_platform(

        )
        self._comments = self._get_comments_from_platform(
            self._http_client,
            self._urls.comments_url
        )

    def _get_comments_from_platform(
        self,
        http: httpx.Client,
        url: str,
    ) -> list[Comment]:
        ''' api结构详见：
        https://docs.github.com/zh/rest/issues/comments?apiVersion=2022-11-28#create-an-issue-comment'''
        print(Log.getting_something.format(something=Log.issue_comment))
        response = http.get(url=url)
        response.raise_for_status()
        print(Log.getting_something_success.
              format(something=Log.issue_comment))
        raw_json: list[dict[str, str]] = response.json()
        return [Comment(author=comment["user"]["login"],
                        body=comment["body"])
                for comment in raw_json]

    def reopen_issue(self) -> None:
        ''' api结构详见：
        https://docs.github.com/zh/rest/issues/issues?apiVersion=2022-11-28#update-an-issue'''
        url = self._urls.issues_url
        print(Log.reopen_issue
              .format(issue_number=self._issue.id))
        response = self._http_client.request(
            method=self.reopen_issue_method,
            url=url,
            json=self.reopen_issue_body
        )
        response.raise_for_status()
        print(Log.reopen_issue_success
              .format(issue_number=self._issue.id)
              )

    def close(self):
        self._http_client.close()


class Gitlab(Platform):

    @property
    def reopen_issue_method(self) -> str:
        return "PUT"

    @property
    def reopen_issue_body(self) -> dict[str, str]:
        return {
            "state_event": "reopen"
        }

    def create_http_header(self, token: str) -> dict[str, str]:
        ''' 所需http header结构详见：
        https://docs.gitlab.com/ee/api/rest/index.html#request-payload'''
        return {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }

    def issue_web_url_to_issue_api_url(self,
                                       web_url: str,
                                       project_id: int) -> str:
        project_name_index = -4
        owner_name_index = 3

        # api样例：https://{gitlab_host}/api/v4/projects/{project_id}/issues/{issues_id}
        # web_url样例：https://{gitlab_host}/｛owner｝/{project_name}/-/issues/{issues_id}

        # ['https:', '', '{gitlab_host}', '｛owner｝', '{project_name}', '-', 'issues', '1']

        url_split = web_url.split("/")
        url_split.pop(project_name_index)  # 删掉project_name
        url_split.pop(owner_name_index)  # 删掉project_name
        url_split.remove('-')

        # ['https:', '', '{gitlab_host}', 'issues', '1']

        url_split.insert(3, Urls.ApiPath.base)
        url_split.insert(4, Urls.ApiPath.projects)
        url_split.insert(5, str(project_id))

        # ['https:', '', '{gitlab_host}', 'api/v4', 'projects', '｛project_id｝', 'issues', '1']

        return '/'.join(url_split)

    def _get_labels_from_platform(self) -> list[str]:
        # ''' 所需http header结构详见：
        # https://docs.gitlab.com/ee/api/issues.html#single-issue'''
        # gitlab webhook的payload携带了label了
        print(Log.getting_something.
              format(something=Log.issue_label))
        print(Log.getting_something_success.
              format(something=Log.issue_label))
        return self._issue.labels

    def _read_platform_environments(self) -> None:
        print(Log.loading_something.format(something=Log.env))

        try:
            webhook_payload = json.loads(
                os.environ[Env.WEBHOOK_PAYLOAD])
            self._token = os.environ[Env.TOKEN]
        except Exception:
            print(Log.webhook_payload_not_found)
            raise WebhookPayloadError()

        self._issue = Issue(
            id=int(webhook_payload["object_attributes"]["iid"]),
            title=webhook_payload["object_attributes"]["title"],
            state=webhook_payload["object_attributes"]["action"],
            body=webhook_payload["object_attributes"]["description"],
            labels=[
                label_json["title"]
                for label_json in
                webhook_payload["object_attributes"]["labels"]]
        )

        project_id: int = webhook_payload["object_attributes"]["project_id"]
        issue_web_url: int = webhook_payload["object_attributes"]["url"]

        issues_url = self.issue_web_url_to_issue_api_url(
            issue_web_url, project_id
        )
        self._urls = Urls(
            issues_url=issues_url,
            comments_url=issues_url + '/' + Urls.ApiPath.notes,
        )

        print(Log.loading_something_success
              .format(something=Log.env))

    def __init__(self):
        super().__init__()
        self._read_platform_environments()
        self._parse_issue_state()
        self._http_client = httpx.Client(
            headers=self.create_http_header(self._token)
        )
        self._issue.labels = self._get_labels_from_platform()
        self._comments = self._get_comments_from_platform(
            self._http_client,
            self._urls.comments_url
        )

    def should_issue_state_open(self) -> bool:
        return self._issue.state == IssueState.open

    def _get_comments_from_platform(
        self,
        http: httpx.Client,
        url: str,
    ) -> list[Comment]:
        ''' api结构详见：
        https://docs.gitlab.com/ee/api/notes.html#list-project-issue-notes'''
        print(Log.getting_something.format(something=Log.issue_comment))
        response = http.get(url=url)
        response.raise_for_status()
        print(Log.getting_something_success.
              format(something=Log.issue_comment))
        raw_json: list[dict[str, str]] = response.json()
        return [Comment(author=comment["author"]["username"],
                        body=comment["body"])
                for comment in raw_json]

    def reopen_issue(self) -> None:
        ''' api结构详见：
        https://docs.gitlab.com/ee/api/issues.html#edit-an-issue'''
        url = self._urls.issues_url
        print(Log.reopen_issue
              .format(issue_number=self._issue.id))
        response = self._http_client.request(
            method=self.reopen_issue_method,
            url=url,
            json=self.reopen_issue_body
        )
        response.raise_for_status()
        print(Log.reopen_issue_success
              .format(issue_number=self._issue.id)
              )

    def close(self):
        self._http_client.close()
