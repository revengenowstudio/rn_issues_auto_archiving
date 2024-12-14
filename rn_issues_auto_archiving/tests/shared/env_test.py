import os
from unittest.mock import patch

from shared.env import (
    should_run_in_github_action,
    should_run_in_gitlab_ci,
    should_run_in_local,
    Env
)


def test_should_run_in_github_action():
    with patch.dict(os.environ, {Env.GITHUB_ACTIONS: "true"}):
        assert should_run_in_github_action() is True


def test_should_run_in_gitlab_ci():
    with patch.dict(os.environ, {Env.GITLAB_CI: "true"}):
        assert should_run_in_gitlab_ci() is True


def test_should_run_in_local():
    with patch.dict(os.environ, {Env.GITHUB_ACTIONS: "true"}):
        assert should_run_in_local() is False
    with patch.dict(os.environ, {Env.GITLAB_CI: "true"}):
        assert should_run_in_local() is False
    with patch.dict(os.environ, {
            Env.GITLAB_CI: "false",
            Env.GITHUB_ACTIONS: "false"
    }):
        assert should_run_in_local() is True
