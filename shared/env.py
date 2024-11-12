import os


class Env():

    # github action
    GITHUB_ACTIONS = "GITHUB_ACTIONS"
    ISSUE_NUMBER = "ISSUE_NUMBER"
    ISSUE_TITLE = "ISSUE_TITLE"
    ISSUE_STATE = "ISSUE_STATE"
    ISSUE_BODY = "ISSUE_BODY"
    ISSUE_URL = "ISSUE_URL"
    COMMENTS_URL = "COMMENTS_URL"

    # gitlab ci
    GITLAB_CI = "GITLAB_CI"

    # 两侧均可直接读取的环境变量
    # 或者是放仓库变量的
    TOKEN = "TOKEN"
    OUTPUT_PATH = "OUTPUT_PATH"
    ISSUE_REPOSITORY = "ISSUE_REPOSITORY"

def should_run_in_github_action() -> bool:
    return os.environ.get(Env.GITHUB_ACTIONS) == "true"


def should_run_in_gitlab_ci() -> bool:
    return os.environ.get(Env.GITLAB_CI) == "true"


def should_run_in_local() -> bool:
    return (not should_run_in_github_action()
            and not should_run_in_gitlab_ci())
