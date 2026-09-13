import time
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SourcePath:
    """源路径包装。

    delete_source_dir_not_exist_files:
        仅当 path 是文件夹时生效。为 True 时，目标目录会做镜像同步：
        源里不存在的文件/文件夹会被从目标中删除。为 False 时只做覆盖复制。
    """

    path: Path
    delete_source_dir_not_exist_files: bool = False


COMMON_FILE_LIST = [
    SourcePath(
        Path("./rn_issues_auto_archiving"), delete_source_dir_not_exist_files=True
    ),
    SourcePath(Path("./image"), delete_source_dir_not_exist_files=True),
    SourcePath(Path("./手动运行归档流水线指南.md")),
    SourcePath(Path("./自动归档流水线使用指南.md")),
    SourcePath(Path("pyproject.toml")),
    SourcePath(Path("requirements.txt")),
    SourcePath(Path("develop-requirements.txt")),
    SourcePath(Path(".python-version")),
    SourcePath(Path("uv.lock")),
    # SourcePath(Path("./rn_issues_auto_archiving/README.md")),
]
BLACK_LIST = [
    "__pycache__",
    "tests",
    "Unittest.yml",
    "README",
    "develop-requirements.txt",
]
GITLAB_FILE_LIST = [
    SourcePath(Path("./.gitlab-ci.yml")),
    SourcePath(Path("./.gitlab")),
]
GITHUB_FILE_LIST = [SourcePath(Path("./.github"))]

ARG_ALL_ISSUE_PATH = "--all_issue_path"
ARG_INTERNAL_ISSUE_PATH = "--internal_issue_path"

REPLACE_FILE_CONTENT_LIST = [
    # ("AutoArchiving.yml", "TARGET_BRANCH: main", "TARGET_BRANCH: master"),
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


def _apply_replacements(target_file_path: Path) -> None:
    """把 REPLACE_FILE_CONTENT_LIST 里配置的替换应用到目标文件。"""
    for target_file_name, target_str, new_str in REPLACE_FILE_CONTENT_LIST:
        if target_file_path.name != target_file_name:
            continue
        replace_file_content(file_path=target_file_path, old=target_str, new=new_str)


def _sync_dir(
    src: Path,
    dst: Path,
    black_list: Iterable[str],
    *,
    delete_extra: bool,
) -> None:
    """把 src 目录同步到 dst。

    delete_extra=True  : 目标中源里不存在的文件/文件夹会被删除（镜像同步）。
    delete_extra=False : 只做覆盖复制，目标中多余的内容保留。
    """
    dst.mkdir(parents=True, exist_ok=True)

    # 1. 收集源里"应该存在"的相对路径（过黑名单）
    src_rel_paths: set[Path] = set()
    for p in src.rglob("*"):
        if path_in_black_list(p, black_list):
            continue
        src_rel_paths.add(p.relative_to(src))

    # 2. 若开启镜像同步，删除目标里多余的项（从深到浅，先删文件再删空目录）
    if delete_extra:
        for p in sorted(dst.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            rel = p.relative_to(dst)
            if rel in src_rel_paths:
                continue
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
            print(f'删除目标中多余的文件/文件夹 : "{str(p)}"')

    # 3. 复制/覆盖源里存在的项
    for rel in src_rel_paths:
        source = src / rel
        target = dst / rel
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src=source, dst=target, follow_symlinks=False)
            _apply_replacements(target)


def copy_files(
    source_list: Iterable[SourcePath],
    target_path: Path,
    black_list: Iterable[str],
) -> None:
    for source in source_list:
        file_path = source.path

        if path_in_black_list(file_path, black_list):
            kind = "文件夹" if file_path.is_dir() else "文件"
            print(f'{kind}在黑名单中,跳过复制 : "{str(file_path)}"')
            continue

        target_file_path = target_path.joinpath(file_path.name)

        if file_path.is_dir():
            print(f'发现文件夹 : "{str(file_path)}"')
            _sync_dir(
                src=file_path,
                dst=target_file_path,
                black_list=black_list,
                delete_extra=source.delete_source_dir_not_exist_files,
            )
            action = "同步" if source.delete_source_dir_not_exist_files else "复制"
            print(f'{action}文件夹 : "{str(file_path)}" 到 "{str(target_path)}"')
            continue

        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src=file_path, dst=target_path, follow_symlinks=False)
        _apply_replacements(target_file_path)
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
        for index, key in enumerate(args[::2], 0)
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
    copy_files(COMMON_FILE_LIST, all_issue_repo_path, BLACK_LIST)
    copy_files(COMMON_FILE_LIST, internal_issue_repo_path, BLACK_LIST)
    print("开始复制 GitHub 专用文件")
    copy_files(GITHUB_FILE_LIST, all_issue_repo_path, BLACK_LIST)
    print("开始复制 GitLab 专用文件")
    copy_files(GITLAB_FILE_LIST, internal_issue_repo_path, BLACK_LIST)

    print(f"任务完成 , 耗时 : {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
