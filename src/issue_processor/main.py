import os
import sys


from issue_platform import Platform, Github, Gitlab
from json_config import Config
from src.shared.log import Log
from src.shared.exception import *
from src.shared.env import (should_run_in_github_action,
                            should_run_in_gitlab_ci,
                            should_run_in_local)

sys.path.append(os.getcwd())

# TODO
# 虽然配置文件里有black list的配置项，但是由于暂时用不到
# 所以并没有实现黑名单的功能


def Exit():
    print(Log.job_done)
    exit(0)


def get_config_path_from_args(args: list[str]) -> str:
    path = None
    if ("--config" in args):
        path = args[args.index("--config") + 1]
    if ("-c" in args != -1):
        path = args[args.index("-c") + 1]
    return path


def get_test_platform_type_from_args(args: list[str]) -> str:
    result = None
    if ("--platform-type" in args):
        result = args[args.index("--platform-type") + 1]
    if ("-pt" in args != -1):
        result = args[args.index("-pt") + 1]
    return result


def main(args: list[str]) -> None:
    config = Config(get_config_path_from_args(args))
    platform: Platform

    if should_run_in_local():
        print(Log.non_platform_action_env)
        from dotenv import load_dotenv
        load_dotenv()

    test_platform_type = get_test_platform_type_from_args(args)
    if test_platform_type is None:
        if should_run_in_github_action():
            platform = Github()
        elif should_run_in_gitlab_ci():
            platform = Gitlab()
        # 这里特意没写else，如果本地手动执行脚本的时候
        # 没有添加--platform-type或-pt参数
        # 就会跑到这里的else语句了
        # 且不需要else已经足够判断生产环境了
    else:
        print(Log.get_test_platform_type
              .format(test_platform_type=test_platform_type))
        if test_platform_type == "github":
            platform = Github()
        elif test_platform_type == "gitlab":
            try:
                platform = Gitlab()
            except WebhookPayloadError:
                Exit()
        else:
            print(Log.unexpected_platform_type
                  .format(
                      platform_type=test_platform_type
                  ))

    try:
        if (isinstance(platform, Gitlab)
                and platform.should_issue_state_open()):
            print(Log.issue_state_is_open)
            Exit()

        archive_version = platform.get_archive_version(
            config.white_list.comments)

        if not platform.should_archive_issue(
            archive_version,
            platform.get_labels(),
            config.white_list.labels,
            config.white_list.comments,
        ):
            print(Log.not_archive_issue)
            Exit()

        issue_type = platform.get_issue_type_from_labels(
            config.issue_type.label_map
        )

        platform.remove_type_in_issue_title(
            config.issue_type.type_keyword
        )

        introduced_version = platform.get_introduced_version(
            config.introduced_version_reges
        )

        platform.issue_content_to_json(
            platform.parse_introduced_version(
                introduced_version,
                issue_type in config.issue_type
                                    .need_introduced_version_issue_type
            ),
            platform.parse_archive_version(
                archive_version
            ),
            issue_type
        )

    except (
        ArchiveBaseError
    ) as exc:
        print(Log.archiving_condition_not_satisfied)
        platform.reopen_issue()
        platform.send_comment(str(exc))
        raise
    finally:
        platform.close()


if __name__ == "__main__":
    main(sys.argv)
