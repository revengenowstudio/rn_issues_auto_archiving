import pytest
import sys

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
    sys.argv.extend([short_arg,value])    
    assert get_value_from_args(short_arg, long_arg) == value
    sys.argv.remove(short_arg)
    sys.argv.remove(value)

    sys.argv.extend([long_arg,value])    
    assert get_value_from_args(short_arg, long_arg) == value
    sys.argv.remove(long_arg)
    sys.argv.remove(value)
    
    assert get_value_from_args(short_arg, long_arg) == None
