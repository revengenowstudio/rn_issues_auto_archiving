import os
import json

payload: dict[str, dict] = json.loads(
    (os.environ.get("WEBHOOK_PAYLOAD"))
)


if (temp := payload.get("object_attributes")) is not None:
    issue_id = temp.get("iid")
    print(issue_id)

