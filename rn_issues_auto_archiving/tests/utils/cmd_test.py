import sys

import pytest

from utils.cmd import CommandFailed, cmd_run


class TestCmdRun:
    def test_returns_stdout(self):
        assert cmd_run([sys.executable, "-c", "print('hello')"]) == "hello"

    def test_strips_stdout(self):
        assert cmd_run([sys.executable, "-c", "print('  padded  ')"]) == "padded"

    def test_empty_stdout_returns_empty_str(self):
        assert cmd_run([sys.executable, "-c", "pass"]) == ""

    def test_raises_on_non_zero_return_code(self):
        with pytest.raises(CommandFailed, match="3"):
            cmd_run([sys.executable, "-c", "import sys; sys.exit(3)"])

    def test_error_message_contains_cmd_and_stderr(self):
        with pytest.raises(CommandFailed) as exc_info:
            cmd_run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.stderr.write('boom'); sys.exit(1)",
                ]
            )
        message = str(exc_info.value)
        assert "boom" in message
        assert sys.executable in message

    def test_raises_when_command_not_found(self):
        with pytest.raises(CommandFailed, match="definitely-not-a-real-command-xyz"):
            cmd_run(["definitely-not-a-real-command-xyz"])
