import os

from app_config import Config
from shared.data_source import DataSource
from shared.env import Env


class EnvConfigDataSource(DataSource):
    def load(self, config: Config) -> None:
        config.token = os.environ[Env.TOKEN]
        config.issue_output_path = os.environ[Env.ISSUE_OUTPUT_PATH]
        config.ci_event_type = os.environ[Env.CI_EVENT_TYPE]
        config.archived_document_path = os.environ[Env.ARCHIVED_DOCUMENT_PATH]
