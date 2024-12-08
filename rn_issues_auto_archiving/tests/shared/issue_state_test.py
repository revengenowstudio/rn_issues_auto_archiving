import pytest

from shared.issue_state import parse_issue_state


@pytest.mark.parametrize("input,output", [
    ("open", "open"),
    ("OPEN", "open"),
    ("reopen", "open"),
    ("close", "closed"),
    ("CLOSE", "closed"),
    ("CLOSED", "closed"),
    ("update", "update"),
    ("", ""),
    ("xxx", "xxx"),
    ("openxxx", "openxxx"),
    ("closexxx", "closexxx"),
])
def test_parse_issue_state(input: str, output: str):
    assert parse_issue_state(input) == output
