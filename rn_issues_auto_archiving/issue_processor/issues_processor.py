

from git_service_client import GitServiceClient
from shared.issue_state import IssueState
from shared.exception import ErrorMessage, MissingArchiveVersionAndArchiveLabel
from shared.issue_info import AUTO_ISSUE_TYPE, IssueInfo
from shared.json_config import Config
from shared.log import Log


class IssueProcessor():
    def __init__(
        self,
        issue_info: IssueInfo,
        config: Config,
        platform: GitServiceClient
    ) -> None:
        self._issue_info = issue_info
        self._config = config
        self._platform = platform

    def not_archived_object(self) -> bool:
        # gitlab的issue webhook是会响应issue reopen事件的
        # gitlab的reopen issue事件应该被跳过
        # 而手动触发的流水线有可能目标Issue是还没被closed的
        if (not self._platform.should_ci_running_in_manual
                and (self._issue_info.issue_state
                     == IssueState.open)
            ):
            print(Log.issue_state_is_open)
            return True

        # gitlab的issue webhook还会响应issue update事件
        if (self._issue_info.issue_state
                == IssueState.update):
            print(Log.issue_state_is_update)
            return True

        running_in_manual = self._platform.should_ci_running_in_manual
        not_input_archive_version = (
            self._issue_info.archive_version == "")
        if ((running_in_manual and not_input_archive_version)
                or not running_in_manual):
            not_archived_issue = not self._platform.should_archive_issue(
                self._issue_info.issue_type,
                self._config.issue_type.label_map,
                self._platform.get_archive_version(
                    self._config.archived_version_reges_for_comments
                ),
                self._issue_info.issue_labels,
                self._config.archive_necessary_labels
            )
            if not running_in_manual and not_archived_issue:
                print(Log.not_archive_issue)
                return True
            elif ((running_in_manual and not_input_archive_version)
                  and not_archived_issue):
                raise MissingArchiveVersionAndArchiveLabel(
                    ErrorMessage.missing_labels_and_archive_version
                )

        return False

    def match_issue_type(self) -> None:
        if self._issue_info.issue_type == AUTO_ISSUE_TYPE:
            self._issue_info.issue_type = self._platform.get_issue_type_from_labels(
                self._issue_info.issue_labels,
                self._config.issue_type.label_map
            )

    def match_introduced_version(self) -> None:
        # 自动触发流水线必须从描述中获取引入版本号
        # 手动触发流水线如果没有填引入版本号，
        # 那么还得从描述里获取引入版本号
        if self._issue_info.introduced_version == "":
            self._issue_info.update(
                introduced_version=self._platform.get_introduced_version_from_description(
                    self._issue_info.issue_type,
                    self._issue_info.issue_body,
                    self._config.introduced_version_reges,
                    self._config.issue_type.need_introduced_version_issue_type
                )
            )

    def match_archive_version(self) -> None:
        self._issue_info.update(
            archive_version=self._platform.parse_archive_version(
                self._platform.get_archive_version(
                    self._config.archived_version_reges_for_comments
                )
            )
        )

    def parse_issue_title(self) -> None:
        self._issue_info.update(
            issue_title=self._platform.remove_issue_type_in_issue_title(
                self._issue_info.issue_title,
                self._config.issue_type.type_keyword
            )
        )

    def close_issue(self) -> None:
        if (self._platform.should_ci_running_in_manual
                and (self._issue_info.issue_state
                     == IssueState.open)
            ):
            self._platform.close_issue(
                self._issue_info.links.issue_url
            )
