import pytest
import os
from unittest.mock import patch

from shared.ci_event_type import CiEventType
from shared.env import Env


def test_should_ci_running_in_manual():

    for manual_event_type in CiEventType.manual:
        with patch.dict(os.environ, {Env.CI_EVENT_TYPE: manual_event_type}):
            assert CiEventType.should_ci_running_in_manual()
    for issue_event_type in CiEventType.issue_event:
        with patch.dict(os.environ, {Env.CI_EVENT_TYPE: issue_event_type}):
            assert CiEventType.should_ci_running_in_manual() is False


def test_should_ci_running_in_issue_event():
    for manual_event_type in CiEventType.manual:
        with patch.dict(os.environ, {Env.CI_EVENT_TYPE: manual_event_type}):
            assert CiEventType.should_ci_running_in_issue_event() is False
    for issue_event_type in CiEventType.issue_event:
        with patch.dict(os.environ, {Env.CI_EVENT_TYPE: issue_event_type}):
            assert CiEventType.should_ci_running_in_issue_event()
