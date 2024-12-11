
# class TestPlatform():
#     @staticmethod
#     def test_issue_number_to_int():
#         assert GitServiceClient.issue_number_to_int(
#             "123") == 123
#         with pytest.raises(ValueError):
#             GitServiceClient.issue_number_to_int("abc")


# github_auto_archiving_env_dict = {
#     "TOKEN": "fake_token",
#     "ISSUE_OUTPUT_PATH": "fake_output_path",
#     "CI_EVENT_TYPE": "fake_event_type",
#     "ISSUE_NUMBER": "123",
#     "ISSUE_TITLE": "fake_issue_title",
#     "ISSUE_STATE": "fake_issue_state",
#     "ISSUE_BODY": "fake_issue_body",
#     "ISSUE_URL": "fake_issue_url",
#     "COMMENTS_URL": "fake_comments_url"
# }


# github_manual_archiving_env_dict = {
#     "TOKEN": "fake_token",
#     "ISSUE_OUTPUT_PATH": "fake_output_path",
#     "CI_EVENT_TYPE": "fake_event_type",
#     "MANUAL_ISSUE_NUMBER": "321",
#     "MANUAL_ISSUE_TITLE": "fake_manual_issue_title",
#     "MANUAL_ISSUE_STATE": "fake_manual_issue_state",
#     "INTRODUCED_VERSION": "fake_introduced_version",
#     "ARCHIVE_VERSION": "fake_archive_version",
#     "ISSUE_TYPE": "fake_issue_type",
#     "MANUAL_ISSUE_URL": "fake_manual_issue_url",
#     "MANUAL_COMMENTS_URL": "fake_manual_comments_url"
# }

# gitlab_auto_archiving_env_dict = {
#     "TOKEN": "fake_token",
#     "CI_EVENT_TYPE": "fake_ci_event_type",
#     "ISSUE_OUTPUT_PATH": "fake_issue_output_path",
#     "API_BASE_URL": "fake_api_base_url",
#     "WEBHOOK_PAYLOAD": "fake_webhook_payload",
# }
# gitlab_manual_archiving_env_dict = {
#     "TOKEN": "fake_token",
#     "CI_EVENT_TYPE": "fake_ci_event_type",
#     "ISSUE_OUTPUT_PATH": "fake_issue_output_path",
#     "API_BASE_URL": "fake_api_base_url",
#     "ISSUE_NUMBER": "fake_issue_number",
#     "ISSUE_TITLE": "fake_issue_title",
#     "ISSUE_STATE": "fake_issue_state",
#     "INTRODUCED_VERSION": "fake_introduced_version",
#     "ARCHIVE_VERSION": "fake_archive_version",
#     "ISSUE_TYPE": "fake_issue_type",

# }


# @pytest.fixture(scope="class")
# def setup_github_auto_archiving_environment():
#     with patch.dict(os.environ, github_auto_archiving_env_dict):
#         yield
#     # os.environ[Env.TOKEN] = ""
#     # os.environ[Env.ISSUE_OUTPUT_PATH] = ""
#     # os.environ[Env.CI_EVENT_TYPE] = ""
#     # os.environ[Env.ISSUE_NUMBER] = ""
#     # os.environ[Env.ISSUE_TITLE] = ""
#     # os.environ[Env.ISSUE_STATE] = ""
#     # os.environ[Env.ISSUE_BODY] = ""
#     # os.environ[Env.ISSUE_URL] = ""
#     # os.environ[Env.COMMENTS_URL] = ""


# @pytest.fixture(scope="class")
# def setup_github_manual_archiving_environment():
#     with patch.dict(os.environ, github_manual_archiving_env_dict):
#         yield
#     # os.environ[Env.TOKEN] = ""
#     # os.environ[Env.ISSUE_OUTPUT_PATH] = ""
#     # os.environ[Env.CI_EVENT_TYPE] = ""
#     # os.environ[Env.MANUAL_ISSUE_NUMBER] = ""
#     # os.environ[Env.MANUAL_ISSUE_TITLE] = ""
#     # os.environ[Env.MANUAL_ISSUE_STATE] = ""
#     # os.environ[Env.INTRODUCED_VERSION] = ""
#     # os.environ[Env.ARCHIVE_VERSION] = ""
#     # os.environ[Env.ISSUE_TYPE] = ""
#     # os.environ[Env.MANUAL_ISSUE_URL] = ""
#     # os.environ[Env.MANUAL_COMMENTS_URL] = ""


# def test_github_init_issue_info(
#         github: GithubClient,
#         env_dict: dict[str, str],
#         manual: bool = False
# ):
#     assert github._token == env_dict["TOKEN"]
#     assert github._output_path == env_dict["ISSUE_OUTPUT_PATH"]
#     assert github._ci_event_type == env_dict["CI_EVENT_TYPE"]
#     assert github._issue.id == int(
#         env_dict["ISSUE_NUMBER"])
#     assert github._issue.title == env_dict["ISSUE_TITLE"]
#     assert github._issue.state == parse_issue_state(env_dict["ISSUE_STATE"])
#     assert github._issue.labels == []
#     if manual:
#         assert github._issue.issue_type == env_dict["ISSUE_TYPE"]
#         assert github._issue.introduced_version == env_dict["INTRODUCED_VERSION"]
#         assert github._issue.archive_version == env_dict["ARCHIVE_VERSION"]
#         assert github._urls.issue_url == env_dict["MANUAL_ISSUE_URL"]
#         assert github._urls.comments_url == env_dict["MANUAL_COMMENTS_URL"]
#     else:
#         assert github._issue.issue_type == AUTO_ISSUE_TYPE
#         assert github._issue.body == env_dict["ISSUE_BODY"]
#         assert github._urls.issue_url == env_dict["ISSUE_URL"]
#         assert github._urls.comments_url == env_dict["COMMENTS_URL"]
# def test_gitlab_init_issue_info(
#         gitlab: GitlabClient,
#         env_dict: dict[str, str],
#         manual: bool = False
# ):
#     assert gitlab._token == env_dict["TOKEN"]
#     assert gitlab._output_path == env_dict["ISSUE_OUTPUT_PATH"]
#     assert github._ci_event_type == env_dict["CI_EVENT_TYPE"]
#     assert gitlab._issue.id == int(
#         env_dict["ISSUE_NUMBER"])
#     assert gitlab._issue.title == env_dict["ISSUE_TITLE"]
#     assert gitlab._issue.state == parse_issue_state(env_dict["ISSUE_STATE"])
#     assert gitlab._issue.labels == []
#     if manual:
#         assert gitlab._issue.issue_type == env_dict["ISSUE_TYPE"]
#         assert gitlab._issue.introduced_version == env_dict["INTRODUCED_VERSION"]
#         assert gitlab._issue.archive_version == env_dict["ARCHIVE_VERSION"]
#         assert gitlab._urls.issue_url == env_dict["MANUAL_ISSUE_URL"]
#         assert gitlab._urls.comments_url == env_dict["MANUAL_COMMENTS_URL"]
#     else:
#         assert gitlab._issue.issue_type == AUTO_ISSUE_TYPE
#         assert gitlab._issue.body == env_dict["ISSUE_BODY"]
#         assert gitlab._urls.issue_url == env_dict["ISSUE_URL"]
#         assert gitlab._urls.comments_url == env_dict["COMMENTS_URL"]


# @pytest.mark.parametrize(
#     "env_dict",
#     [
#         github_auto_archiving_env_dict,
#         github_manual_archiving_env_dict
#     ]
# )
# def test_github_read_platform_environments(
#     self,
#     env_dict: dict[str, str]
# ):
#     with patch.dict(os.environ, env_dict):
#         if env_dict.get("ISSUE_NUMBER") is None:
#             pytest.raises(ValueError)
#             return
#         test_platform_issue_info(GithubClient())


# @pytest.mark.usefixtures("setup_github_auto_archiving_environment")
# @pytest.fixture(scope="class")
# def github(self) -> GithubClient:
#     # self.github1 = GithubClient()
#     return GithubClient()

# # def setup_gitlab_environment():
# #     os.environ[Env.TOKEN]
# #     os.environ[Env.CI_EVENT_TYPE]
# #     os.environ[Env.ISSUE_OUTPUT_PATH]
# #     os.environ.get(Env.ISSUE_NUMBER, "")
# #     os.environ.get(Env.ISSUE_TITLE, "").strip(),
# #     os.environ[Env.ISSUE_STATE]),
# #         os.environ.get(
# #     os.environ.get(Env.ISSUE_TYPE,
# #                    os.environ[Env.API_BASE_URL]
# #                    os.environ[Env.WEBHOOK_PAYLOAD]
# #                    os.environ[Env.API_BASE_URL]}


# # @pytest.mark.usefixtures("setup_gitlab_environment")
# # class TestGitlab():
