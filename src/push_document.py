

import os
import json
from pathlib import Path

import httpx

from shared.env import Env
from shared.exception import ErrorMessage
from auto_archiving.send_comment import send_comment
from auto_archiving.reopen_issue import reopen_issue
from issue_processor.issue_platform import Gitlab


class Log():
    pushing_document = '''正在提交归档文档'''
    pushing_document_success = '''提交归档文档成功'''
    push_document_failed = '''提交归档文档失败，错误信息：{exc}'''


def get_issue_id_from_webhook(webhook_path: str) -> int:
    payload: dict[str, dict] = json.loads(
        Path(webhook_path).read_text(encoding="utf-8")
    )
    return payload["object_attributes"]["iid"]


def push_document(
    http_header: dict[str, str],
    gitlab_host: str,
    project_id: int,
    file_path: str,
    file_content: str,
    branch_name: str,
    author_email: str,
    author_name: str,
    commit_message: str
) -> None:
    ''' 更新仓库内文件的文档：
    https://docs.gitlab.com/ee/api/repository_files.html#update-existing-file-in-repository 
    '''
    print(Log.pushing_document)
    response = httpx.put(
        headers=http_header,
        url=f'https://{gitlab_host}/api/v4/projects/{project_id}/repository/files/{file_path}',
        json={
            "branch": branch_name,
            "author_email": author_email,
            "author_name": author_name,
            "content": file_content,
            "commit_message": commit_message
        }
    )
    response.raise_for_status()

    print(Log.pushing_document_success)


def main():
    archived_document_path = os.environ[Env.ARCHIVED_DOCUMENT_PATH]
    issue_id = get_issue_id_from_webhook(
        os.environ[Env.WEBHOOK_OUTPUT_PATH])
    gitlab_host = os.environ[Env.GITLAB_HOST]
    project_id = int(os.environ[Env.PROJECT_ID])
    token = os.environ[Env.TOKEN]
    http_header = Gitlab.create_http_header(token)

    try:
        push_document(
            http_header,
            gitlab_host,
            project_id,
            archived_document_path,
            Path(archived_document_path).read_text("utf-8"),
            os.environ["branch"],
            os.environ["author_email"],
            os.environ["author_name"],
            os.environ["commit_message"].format(
                issue_id=issue_id
            )
        )
    except Exception as exc:
        print(Log.push_document_failed
              .format(exc=str(exc)))
        base_url = f"https://{gitlab_host}/api/v4/projects/{project_id}/issues/{issue_id}"
        reopen_issue(
            http_header=http_header,
            reopen_url=base_url,
            reopen_http_method="PUT",
            reopen_body={
                "state_event": "reopen"
            }
        )
        send_comment(
            http_header=http_header,
            comment_url=f'{base_url}/notes',
            message=ErrorMessage.push_document_failed
            .format(exc=str(exc))
        )
        raise


if __name__ == "__main__":
    main()
