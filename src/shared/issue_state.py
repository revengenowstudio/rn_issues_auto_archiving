ISSUE_STATE_MAP = {
    "closed": "closed",
    "close": "closed",
    "open": "open",
    "opened": "open",
    "reopen": "open",
}
'''将issue_state转换成只有两种状态，
open或closed'''

class IssueState():
    closed = "closed"
    open = "open"

def parse_issue_state(state: str) -> str:
    return ISSUE_STATE_MAP[state]