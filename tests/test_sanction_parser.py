

import re


import re

from asyncpg import AssertError


def test_parse_text():
    text = 'от 10000 до 20000 (в рублях)'
    result = re.match(r"^(?P<min>от\s*(?P<min_val>\d+))|\s*(?P<max>до\s*(?P<max_val>\d+))|\s*(?P<measure>...+)$", text)
    assert result 
    assert result.groupdict()['min']
    assert result.groupdict()['min_val']
    assert result.groupdict()['max']
    assert result.groupdict()['max_val']
    assert result.groupdict()['measure']




