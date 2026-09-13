import os
from unittest.mock import patch

import pytest

from app_config import Config
from shared.config_data_source import EnvConfigDataSource
from shared.env import Env


class TestEnvConfigDataSource:
    @pytest.mark.parametrize(
        "env_dict",
        [
            {
                Env.TOKEN: "token",
                Env.ISSUE_OUTPUT_PATH: "issue_output_path",
                Env.CI_EVENT_TYPE: "ci_event_type",
                Env.ARCHIVED_DOCUMENT_PATH: "archived_document_path",
            },
        ],
    )
    def test_load(self, env_dict: dict[str, str]):
        with patch.dict(os.environ, env_dict):
            config = Config()
            env_config_data_source = EnvConfigDataSource()
            env_config_data_source.load(config)
            assert config.token == env_dict[Env.TOKEN]
            assert config.issue_output_path == env_dict[Env.ISSUE_OUTPUT_PATH]
            assert config.ci_event_type == env_dict[Env.CI_EVENT_TYPE]
            assert config.archived_document_path == env_dict[Env.ARCHIVED_DOCUMENT_PATH]
