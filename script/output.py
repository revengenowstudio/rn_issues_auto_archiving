import time
import shutil
import sys
from pathlib import Path
from typing import Generator, Iterable


COMMON_FILE_LIST = [
    Path("./rn_issues_auto_archiving"),
    Path("./image"),
    Path("./config"),
    Path("./手动运行归档流水线指南.md"),
    Path("./自动归档流水线使用指南.md"),
    Path("pyproject.toml"),
    Path("requirements.txt"),
    Path("develop-requirements.txt"),
    Path(".python-version"),
    Path("uv.lock"),
]
BLACK_LIST = [
    "__pycache__",
    "tests",
    "Unittest.yml",
    "README",
    "develop-requirements.txt",
]
GITLAB_FILE_LIST = [Path("./.gitlab-ci.yml"), Path("./.gitlab")]
GITHUB_FILE_LIST = [Path("./.github")]

ARG_ALL_ISSUE_PATH = "--all_issue_path"
ARG_INTERNAL_ISSUE_PATH = "--internal_issue_path"

REPLACE_FILE_CONTENT_LIST = [
    ("AutoArchiving.yml", "TARGET_BRANCH: main", "TARGET_BRANCH: master"),
    (".gitlab-ci.yml", "  - unittest\n", ""),
    (".gitlab-ci.yml", '  - local: "/.gitlab/workflows/Unittest.yml"\n', ""),
]

help_args_list = ["--help", "-h", "help", "h"]
help_message = """
--all_issue_path : 外部 issue 仓库本机绝对路径
--internal_issue_path : 外部 issue 仓库本机绝对路径
"""


def path_in_black_list(file_path: Path, black_list: Iterable[str]) -> bool:
    for black_path in black_list:
        if black_path in str(file_path.absolute()):
            return True
    return False


def replace_file_content(file_path: Path, old: str, new: str) -> None:
    print(f'替换文件 : "{str(file_path)}" 中的 "{old}" 为 "{new}"')
    raw_content = file_path.read_text(encoding="utf-8")
    raw_content = raw_content.replace(old, new)
    file_path.write_text(raw_content, encoding="utf-8")


def copy_files(
    file_path_list: Iterable[Path], target_path: Path, black_list: Iterable[str]
) -> None:
    for file_path in file_path_list:
        if file_path.is_dir():
            print(f'发现文件夹 : "{str(file_path)}"')
            if path_in_black_list(file_path, black_list):
                print(f'文件夹在黑名单中,跳过复制 : "{str(file_path)}"')
                continue
            copy_files(
                file_path.iterdir(), target_path.joinpath(file_path.name), black_list
            )
            continue

        if path_in_black_list(file_path, black_list):
            print(f'文件在黑名单中,跳过复制 : "{str(file_path)}"')
            continue
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src=file_path, dst=target_path, follow_symlinks=False)

        target_file_path = target_path.joinpath(file_path.name)
        for target_file_name, target_str, new_str in REPLACE_FILE_CONTENT_LIST:
            if file_path.name != target_file_name:
                continue
            replace_file_content(
                file_path=target_file_path, old=target_str, new=new_str
            )
        print(f'复制文件 : "{str(file_path)}" 到 "{str(target_path)}"')


def parse_args(args: list[str]) -> dict[str, str]:
    if len(args) == 0:
        return {}
    if len(args) == 1:
        return {args[0]: ""}
    if len(args) % 2 != 0:
        raise ValueError(f"参数格式错误,不能输入奇数个参数 : {args}")

    args_dict = {
        key.strip(): args[index * 2 + 1].strip()
        for index, key in enumerate(
            args[::2],
            0,
        )
    }
    return args_dict


def is_show_help(args: dict[str, str]) -> bool:
    for key in args.keys():
        if key.lower() in help_args_list:
            return True
    return False


def main(args: list[str]):
    args_dict = parse_args(args)
    all_issue_repo_path = None
    internal_issue_repo_path = None

    if is_show_help(args_dict):
        print(help_message)
        return

    if not args_dict:
        all_issue_repo_path = input("请输入外部 issue 仓库本机绝对路径 :")
        internal_issue_repo_path = input("请输入内部 issue 仓库本机绝对路径 :")
    else:
        all_issue_repo_path = args_dict.get(ARG_ALL_ISSUE_PATH)
        internal_issue_repo_path = args_dict.get(ARG_INTERNAL_ISSUE_PATH)

    if not all_issue_repo_path:
        raise KeyError("没有指定 --all_issue_path 参数")
    if not internal_issue_repo_path:
        raise KeyError("没有指定 --internal_issue_path 参数")

    all_issue_repo_path = Path(all_issue_repo_path)
    internal_issue_repo_path = Path(internal_issue_repo_path)

    if not all_issue_repo_path.exists():
        raise FileNotFoundError(f'找不到 "{str(all_issue_repo_path.absolute())}"')
    if not internal_issue_repo_path.exists():
        raise FileNotFoundError(f'找不到 "{str(internal_issue_repo_path.absolute())}"')

    start_time = time.time()
    print("开始复制文件到仓库目录中")

    print("开始复制通用文件")
    copy_files(
        COMMON_FILE_LIST,
        all_issue_repo_path,
        BLACK_LIST,
    )
    copy_files(
        COMMON_FILE_LIST,
        internal_issue_repo_path,
        BLACK_LIST,
    )
    print("开始复制 GitHub 专用文件")
    copy_files(
        GITHUB_FILE_LIST,
        all_issue_repo_path,
        BLACK_LIST,
    )
    print("开始复制 GitLab 专用文件")
    copy_files(
        GITLAB_FILE_LIST,
        internal_issue_repo_path,
        BLACK_LIST,
    )

    print(f"任务完成 , 耗时 : {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
