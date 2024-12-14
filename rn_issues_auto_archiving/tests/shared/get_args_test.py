import pytest
from unittest.mock import patch

from shared.get_args import get_value_from_args


@pytest.mark.parametrize(
    "short_arg,long_arg,value", [
        ("-o", "--open", "这是中文"),
        ("-O", "--OPEN", "this is value"),

    ])
def test_get_value_from_args(
    short_arg: str,
    long_arg: str,
    value: str
):
    with patch("sys.argv", [short_arg, value]):
        assert get_value_from_args(short_arg, long_arg) == value
    with patch("sys.argv", [long_arg, value]):
        assert get_value_from_args(short_arg, long_arg) == value
    assert get_value_from_args(short_arg, long_arg) == None
