import json
import sys
import sys
import pathlib


# 获取要检查的文件列表
files = pathlib.Path(".").glob("**/*.json")
# print(list(files))
# 遍历每个文件，尝试解析 JSON
for file in files:
    if file.parent.name == ".vscode":
        continue
    try:
        with open(file, 'r',encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        print(f'"{file.absolute()}" json格式不正确，原因是：{e}')
        sys.exit(1)
    

# 如果所有文件都通过检查，继续提交
sys.exit(0)