import json
import sys
from pathlib import Path

# 本脚本会被直接执行（sys.path[0] 是 utils/ 目录），
# 需要把包目录加入 sys.path 才能 import 项目内的模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.env import Env
from utils.env import must_get_env

if __name__ == "__main__":
    payload: dict[str, dict] = json.loads(
        Path(must_get_env(Env.WEBHOOK_OUTPUT_PATH)).read_text()
    )

    if (temp := payload.get("object_attributes")) is not None:
        issue_id = temp.get("iid")
        print(issue_id)
