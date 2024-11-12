import os
import sys
import json
import time
from pathlib import Path

import httpx
from exceptiongroup import ExceptionGroup

from json_config import Config
from archive_document import ArchiveDocument
from failed_record import FailedRecord
from src.shared.issue_info import (IssueInfo, IssueInfoJson)
from src.shared.log import Log
from src.shared.env import Env, should_run_in_github_action
from src.shared.exception import ErrorMessage,IssueInfoMissing

sys.path.append(os.getcwd())


def load_local_env() -> None:
    print(Log.non_github_action_env)
    from dotenv import load_dotenv
    load_dotenv()


def get_config_path_from_args(args: list[str]) -> str:
    path = None
    if ((long_str := "--config") in args):
        path = args[args.index(long_str) + 1]
    if ((short_str := "-c") in args != -1):
        path = args[args.index(short_str) + 1]
    return path


def get_failed_record_path_from_args(args: list[str]) -> str:
    path = None
    if ((long_str := "--failed-record") in args):
        path = args[args.index(long_str) + 1]
    if ((short_str := "-fr") in args != -1):
        path = args[args.index(short_str) + 1]
    return path


def reopen_issue(
    http_header: dict[str, str],
    reopen_url: str,
    reopen_http_method: str,
    reopen_body: dict[str, str]
) -> None:

    print(Log.reopen_issue_request)
    response = httpx.request(
        method=reopen_http_method,
        url=reopen_url,
        headers=http_header,
        json=reopen_body
    )
    response.raise_for_status()
    print(Log.reopen_issue_request_success)


def send_comment(
        comment_url: str,
        headers: str,
        error_message: str

) -> None:
    print(Log.sending_something
          .format(
              something=Log.issue_comment
          ))
    response = httpx.request(
        method="POST",
        url=comment_url,
        headers=headers,
        json={
            "body": error_message
        }
    )
    response.raise_for_status()
    print(Log.sending_something_success
          .format(
              something=Log.issue_comment
          ))


def main(args: list[str]):
    start_time = time.time()
    if not should_run_in_github_action():
        load_local_env()

    failed_record = FailedRecord(get_failed_record_path_from_args(args))
    output_path = os.environ[Env.OUTPUT_PATH]
    try:
        issue_info_json: IssueInfoJson = json.loads(
            Path(output_path
                 ).read_text(encoding="utf-8")
        )

        print(Log.print_issue_info
              .format(issue_info=json.dumps(
                  issue_info_json,
                  indent=4,
                  ensure_ascii=False
              )))

        issue_repository = os.environ[Env.ISSUE_REPOSITORY]

        issue_info = IssueInfo(
            reopen_info=IssueInfo.ReopenInfo(
                **issue_info_json.pop("reopen_info")
            ),
            **issue_info_json
        )

        config = Config(get_config_path_from_args(args))

        archive_document = ArchiveDocument(
            config.archive_document_path
        )

        for issue_id in failed_record.get_all_issue_id():
            if archive_document.should_issue_archived(
                issue_id
            ):
                failed_record.remove_record(issue_id)

        archive_document.archive_issue(
            rjust_character=config.rjust_character,
            rjust_space_width=config.rjust_space_width,
            table_separator=config.table_separator,
            archive_template=config.archive_template,
            issue_title_processing_rules=config.issue_title_processing_rules,
            issue_id=issue_info.issue_id,
            issue_type=issue_info.issue_type,
            issue_title=issue_info.issue_title,
            issue_repository=issue_repository,
            introduced_version=issue_info.introduced_version,
            archive_version=issue_info.archive_version
        )

        print(Log.time_used.format(
            time="{:.4f}".format(
                time.time() - start_time)
        ))
        print(Log.job_down)
    except Exception as exc:
        exceptions = [exc]
        print(ErrorMessage.archiving_failed.format(
            exc=str(exc)
        ))
        try:
            issue_info
        except NameError as exc_:
            raise IssueInfoMissing(
                ErrorMessage.load_issue_info_failed
                .format(
                    output_path=output_path,
                    exc=str(exc_)
                )
            )
        
        failed_record.add_record(
            issue_id=issue_info.issue_id,
            issue_title=issue_info.issue_title,
            issue_repository=issue_repository,
            reason=str(exc)
        )
        try:
            reopen_issue(
                http_header=issue_info.reopen_info.http_header,
                reopen_url=issue_info.reopen_info.reopen_url,
                reopen_http_method=issue_info.reopen_info.reopen_http_method,
                reopen_body=issue_info.reopen_info.reopen_body
            )
        except Exception as exc_:
            exceptions.append(exc_)
            print(ErrorMessage.reopen_issue_failed
                  .format(exc=str(exc_)
                          ))
        try:
            send_comment(
                headers=issue_info.reopen_info.http_header,
                comment_url=issue_info.reopen_info.comment_url,
                error_message=ErrorMessage.archiving_failed.format(
                    exc=str(exc)
                )
            )
        except Exception as exc_:
            exceptions.append(exc_)
            print(ErrorMessage.send_comment_failed
                  .format(exc=str(exc_)
                          ))

        raise ExceptionGroup(exceptions)
    finally:
        if archive_document is not None:
            archive_document.save()
            archive_document.close()
        failed_record.save()


if __name__ == "__main__":
    main(sys.argv)
