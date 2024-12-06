import os

from shared.env import (
    should_run_in_github_action,
    should_run_in_gitlab_ci,
    should_run_in_local
)

def test_should_run_in_github_action():
    os.environ["GITHUB_ACTIONS"] = "true"
    assert should_run_in_github_action() is True
    del os.environ["GITHUB_ACTIONS"]

def test_should_run_in_gitlab_ci():
    os.environ["GITLAB_CI"] = "true"
    assert should_run_in_gitlab_ci() is True
    del os.environ["GITLAB_CI"]

def test_should_run_in_local():
    assert should_run_in_local() is True