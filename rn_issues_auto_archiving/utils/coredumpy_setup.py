import os

import coredumpy

from shared.log import Log
from shared.exception import ArchiveBaseError

DUMP_DIRECTORY = "dumps"


def patch_except_for_ci() -> None:
    """在CI环境里启用coredumpy：\n
    出现未处理异常时会把崩溃现场dump到 dumps/ 目录，
    由流水线作为artifact上传，方便事后在本地用 coredumpy load 复现 \n
    本地运行不启用，避免每次报错都在工作区留下dump文件
    """
    if not os.environ.get("CI"):
        return
    coredumpy.patch_except(
        directory=DUMP_DIRECTORY, exclude=[ArchiveBaseError, KeyboardInterrupt]
    )
    print(Log.coredumpy_enabled.format(directory=DUMP_DIRECTORY))
