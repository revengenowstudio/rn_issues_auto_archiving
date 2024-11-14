import os
import json
from pathlib import Path

payload: dict[str, dict] = json.loads(
    Path("./webhook.json").read_text()
)


if (temp := payload.get("object_attributes")) is not None:
    issue_id = temp.get("iid")
    print(issue_id)

