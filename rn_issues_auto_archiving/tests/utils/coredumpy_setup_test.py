import os
from unittest.mock import patch

from shared.exception import ArchiveBaseError, ArchiveVersionError
from utils.coredumpy_setup import DUMP_DIRECTORY, patch_except_for_ci


class TestPatchExceptForCi:
    def test_does_not_patch_when_not_in_ci(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("utils.coredumpy_setup.coredumpy.patch_except") as patch_except:
                patch_except_for_ci()
                patch_except.assert_not_called()

    def test_patches_when_in_ci(self):
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "1"}, clear=True):
            with patch("utils.coredumpy_setup.coredumpy.patch_except") as patch_except:
                patch_except_for_ci()
                patch_except.assert_called_once_with(
                    directory=DUMP_DIRECTORY,
                    exclude=[ArchiveBaseError, KeyboardInterrupt],
                )

    def test_does_not_patch_when_ci_is_empty(self):
        with patch.dict(os.environ, {"CI": ""}, clear=True):
            with patch("utils.coredumpy_setup.coredumpy.patch_except") as patch_except:
                patch_except_for_ci()
                patch_except.assert_not_called()

    def test_exclude_covers_archive_base_error_subclasses(self):
        """归档失败抛出的都是 ArchiveBaseError 的子类（例如 ArchiveVersionError），
        而 coredumpy 用 isinstance 判断 exclude，
        所以只用基类就能把整个归档失败系列都排除掉，不会产生无意义的dump"""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "1"}, clear=True):
            with patch("utils.coredumpy_setup.coredumpy.patch_except") as patch_except:
                patch_except_for_ci()
                exclude = patch_except.call_args.kwargs["exclude"]
                assert issubclass(ArchiveVersionError, tuple(exclude))
