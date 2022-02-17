import pytest

import json

@pytest.fixture(scope="module")
def arr():
    return [1, None, 2, 3,None]

@pytest.fixture(scope="module")
def pg_arr():
    return '{25000,25000,27000,27000}'

def test_to_pg_array(arr):
    output = [x for x in arr if not x is None]
    assert len(output) == 3
    print(output)

def test_to_python_value(pg_arr):
    table = pg_arr.maketrans({'{': '', '}': '', '"': ''})
    output = [elem for elem in pg_arr.translate(table).split(',')]
    print(output)
    assert output
    assert all([isinstance(elem, str) for elem in output]