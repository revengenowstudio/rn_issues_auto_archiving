import os
import time

from issue_processor.git_service_client import (GitServiceClient,
                                                GithubClient,
                                                GitlabClient,
                                                )
from issue_processor.issue_data_source import (
    GithubIssueDataSource,
    GitlabIssueDataSource,
)
from auto_archiving.archive_document import ArchiveDocument
from shared.issue_info import IssueInfo
from shared.ci_event_type import CiEventType
from shared.json_config import (
    Config
)
from shared.config_data_source import (
    EnvConfigDataSource,
    JsonConfigDataSource
)
from shared.env import Env
from shared.log import Log
from shared.env import (should_run_in_github_action,
                        should_run_in_gitlab_ci,
                        should_run_in_local)
from shared.get_args import get_value_from_args
from shared.exception import *
from shared.config_manager import ConfigManager


def init_git_service_client(
    test_platform_type: str | None,
    config: Config
) -> GithubClient | GitlabClient | None:
    service_client: GithubClient | GitlabClient | None = None
    if test_platform_type is not None:
        print(Log.get_test_platform_type
              .format(test_platform_type=test_platform_type))
    if (test_platform_type == GithubClient.name
            or should_run_in_github_action()):
        service_client = GithubClient(
            token=config.token,
            output_path=config.output_path,
            ci_event_type=config.ci_event_type
        )
    elif (test_platform_type == GitlabClient.name
          or should_run_in_gitlab_ci()):
        service_client = GitlabClient(
            token=config.token,
            output_path=config.output_path,
            ci_event_type=config.ci_event_type
        )
    else:
        raise UnexpectedPlatform(
            Log.unexpected_platform_type
            .format(
                platform_type=test_platform_type
            ))
    return service_client


def main() -> None:
    start_time = time.time()

    if os.environ[Env.CI_EVENT_TYPE] in CiEventType.manual:
        print(Log.running_ci_by_manual)
    else:
        print(Log.running_ci_by_automated)

    if should_run_in_local():
        print(Log.non_platform_action_env)
        from dotenv import load_dotenv
        load_dotenv()

    test_platform_type = get_value_from_args(
        short_arg="-pt",
        long_arg="--platform-type",
    )
    config_path = get_value_from_args(
        short_arg="-c",
        long_arg="--config",
    )
    if config_path is None:
        print(Log.config_path_not_found)
        return

    config_manager = ConfigManager([
        EnvConfigDataSource(),
        JsonConfigDataSource(config_path)
    ])
    config = Config()

    try:
        config_manager.load_all(config)
    except Exception as exc:
        print(Log.parse_config_failed
              .format(exc=exc))
        raise

    if config.output_path is None:
        print(Log.config_path_not_found)
        return

    if not GitlabClient.should_issue_type_webhook():
        return

    platform = init_git_service_client(
        test_platform_type,
        config
    )
    if platform is None:
        return

    issue_info = IssueInfo()
    if isinstance(platform, GithubClient):
        GithubIssueDataSource().load(issue_info)
    elif isinstance(platform, GitlabClient):
        try:
            GitlabIssueDataSource().load(issue_info)
        except WebhookPayloadError:
            return
    else:
        raise UnexpectedPlatform(
            Log.unexpected_platform_type
            .format(
                platform_type=test_platform_type
            ))

    try:
        # gitlab的issue webhook是会相应issue reopen事件的
        # gitlab的reopen issue事件应该被跳过
        # 而手动触发的流水线有可能目标Issue是还没被closed的
        if (not platform.should_ci_running_in_manual
                and platform.should_issue_state_open(
                    issue_info.issue_state)):
            print(Log.issue_state_is_open)
            return

        if platform.should_issue_state_update(
            issue_info.issue_state
        ):
            print(Log.issue_state_is_update)
            return

        platform.fetch_missing_issue_info(issue_info)

        if platform.should_issue_type_auto_detect(
            issue_info.issue_type
        ):
            issue_info.issue_type = platform.get_issue_type_from_labels(
                issue_info.issue_labels,
                config.issue_type.label_map
            )

        # 自动触发流水线必须从描述中获取引入版本号
        # 手动触发流水线如果没有填引入版本号，
        # 那么还得从描述里获取引入版本号
        if not platform.should_introduced_version_input(
            issue_info.introduced_version
        ):
            issue_info.introduced_version = platform.get_introduced_version_from_description(
                issue_info.issue_type,
                issue_info.issue_body,
                config.introduced_version_reges,
                config.issue_type.need_introduced_version_issue_type
            )

        archive_version_list: list[str] = platform.get_archive_version(
            config.archived_version_reges_for_comments
        )

        running_in_manual = platform.should_ci_running_in_manual
        not_input_archive_version = not platform.should_archived_version_input(
            issue_info.archive_version
        )
        if ((running_in_manual and not_input_archive_version)
                or not running_in_manual):
            # 不是所有issue的状态都需要检查issue是否符合归档条件的
            # 所以 should_archive_issue 不能直接放到 if语句 外面
            # 原因详见 should_archive_issue 的注释
            not_archived_issue = not platform.should_archive_issue(
                issue_info.issue_type,
                config.issue_type.label_map,
                archive_version_list,
                issue_info.issue_labels,
                config.archive_necessary_labels
            )
            if not running_in_manual and not_archived_issue:
                print(Log.not_archive_issue)
                return
            elif ((running_in_manual and not_input_archive_version)
                  and not_archived_issue):
                raise MissingArchiveVersionAndArchiveLabel(
                    ErrorMessage.missing_labels_and_archive_version
                )

        issue_info.archive_version = platform.parse_archive_version(
            archive_version_list
        )

        issue_info.issue_title = platform.remove_type_in_issue_title(
            issue_info.issue_title,
            config.issue_type.type_keyword
        )

        if (platform.should_ci_running_in_manual
                and platform.should_issue_state_open(
                    issue_info.issue_state
                )):
            platform.close_issue(
                issue_info.links.issue_url
            )

        # 将issue内容写入归档文件
        archive_document = ArchiveDocument(
            os.environ[Env.ARCHIVED_DOCUMENT_PATH]
        )
        if (issue_info.ci_event_type in CiEventType.issue_event
            and archive_document.should_issue_archived(
                        issue_info.issue_id,
                        issue_info.issue_repository
                    )
            ):
            print(Log.issue_already_archived
                  .format(issue_id=issue_info.issue_id,
                          issue_repository=issue_info.issue_repository))
            return

        archive_document.archive_issue(
            rjust_character=config.archived_document.rjust_character,
            rjust_space_width=config.archived_document.rjust_space_width,
            table_separator=config.archived_document.table_separator,
            archive_template=config.archived_document.archive_template,
            issue_title_processing_rules=config.archived_document.issue_title_processing_rules,
            issue_id=issue_info.issue_id,
            issue_type=issue_info.issue_type,
            issue_title=issue_info.issue_title,
            issue_repository=issue_info.issue_repository,
            introduced_version=issue_info.introduced_version,
            archive_version=issue_info.archive_version,
            replace_mode=(
                issue_info.ci_event_type in CiEventType.manual
            )
        )
        
        # 为了后续推送文档和发送归档成功评论的脚本
        # 而将issue信息输出一个json文件
        issue_info.json_dump(
            config.output_path
        )

    except (
        ArchiveBaseError
    ) as exc:
        print(Log.archiving_condition_not_satisfied)
        platform.reopen_issue(
            issue_info.links.issue_url
        )
        platform.send_comment(
            issue_info.links.comment_url,
            str(exc)
        )
        raise
    finally:
        platform.close()
        try:
            archive_document.save()
            archive_document.close()
        except Exception:
            pass

        print(Log.time_used.format(
            time="{:.4f}".format(
                time.time() - start_time)
        ))

        print(Log.job_done)


if __name__ == "__main__":
    main()
