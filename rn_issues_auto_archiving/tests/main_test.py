# import pytest
# from unittest.mock import patch,MagicMock

# from main import main
# from issue_processor.git_service_client import (
#     GitlabClient,
# )
# from issue_processor.issues_processor import IssueProcessor
# from auto_archiving.archive_document import ArchiveDocument
# from shared.config_manager import ConfigManager
# from shared.config_data_source import EnvConfigDataSource, JsonConfigDataSource
# from shared.ci_event_type import CiEventType
# from shared.env import Env
# from shared.log import Log
# from shared.env import should_run_in_local
# from shared.get_args import get_value_from_args
# from shared.exception import *

# @patch("shared.get_args.get_value_from_args")
# @patch("shared.env.should_run_in_local")
# @patch("issue_processor.issues_processor.IssueProcessor")
# def test_main(
#     mock_issues_processor:MagicMock,
#     should_run_in_local:MagicMock,
#     get_value_from_args:MagicMock,
# ):
#     get_value_from_args.side_effect = [None,None]
#     main()
