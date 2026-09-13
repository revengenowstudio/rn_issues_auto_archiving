import os
from unittest.mock import patch

import pytest

from utils.env import get_env, must_get_env


class TestGetEnv:
    def test_missing_key_returns_default(self):
        with patch.dict(os.environ, {}, clear=True):
            assert get_env("NOT_EXIST_KEY") is None
            assert get_env("NOT_EXIST_KEY", str, "fallback") == "fallback"

    def test_empty_or_blank_value_returns_default(self):
        with patch.dict(os.environ, {"KEY": "", "BLANK": "   "}, clear=True):
            assert get_env("KEY") is None
            assert get_env("BLANK", str, "fallback") == "fallback"

    def test_returns_str_value(self):
        with patch.dict(os.environ, {"KEY": "value"}, clear=True):
            assert get_env("KEY") == "value"

    def test_strips_surrounding_whitespace(self):
        with patch.dict(os.environ, {"KEY": "  value  "}, clear=True):
            assert get_env("KEY") == "value"

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("123", 123),
            ("0", 0),
            ("-7", -7),
        ],
    )
    def test_convert_to_int(self, raw: str, expected: int):
        with patch.dict(os.environ, {"KEY": raw}, clear=True):
            assert get_env("KEY", int) == expected

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("y", True),
            ("on", True),
            ("false", False),
            ("0", False),
            ("no", False),
        ],
    )
    def test_convert_to_bool(self, raw: str, expected: bool):
        with patch.dict(os.environ, {"KEY": raw}, clear=True):
            assert get_env("KEY", bool, False) is expected

    def test_blank_bool_falls_back_to_default(self):
        with patch.dict(os.environ, {"KEY": ""}, clear=True):
            assert get_env("KEY", bool, False) is False

    def test_convert_failed_raises_value_error(self):
        with patch.dict(os.environ, {"KEY": "abc"}, clear=True):
            with pytest.raises(ValueError, match="abc"):
                get_env("KEY", int)


class TestMustGetEnv:
    def test_returns_str_value(self):
        with patch.dict(os.environ, {"KEY": "value"}, clear=True):
            assert must_get_env("KEY") == "value"

    def test_returns_converted_value(self):
        with patch.dict(os.environ, {"KEY": "42"}, clear=True):
            assert must_get_env("KEY", int) == 42

    def test_zero_is_not_treated_as_missing(self):
        with patch.dict(os.environ, {"KEY": "0"}, clear=True):
            assert must_get_env("KEY", int) == 0

    def test_missing_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="NOT_EXIST_KEY"):
                must_get_env("NOT_EXIST_KEY")

    def test_empty_value_raises(self):
        with patch.dict(os.environ, {"KEY": "   "}, clear=True):
            with pytest.raises(ValueError, match="KEY"):
                must_get_env("KEY")

    def test_convert_failed_raises_value_error(self):
        with patch.dict(os.environ, {"KEY": "abc"}, clear=True):
            with pytest.raises(ValueError, match="abc"):
                must_get_env("KEY", int)
