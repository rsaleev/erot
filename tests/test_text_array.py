import pytest

import json

from copy import deepcopy

@pytest.fixture(scope="module")
def arr():
    return [1, None, 2, 3,None]

@pytest.fixture(scope="module")
def pg_arr():
    return '{25000,25000,27000,27000}'


@pytest.fixture(scope="module")
def py_arr_text():
    return {'ids':['a:aa', 'b:bb', 'v:vv']}

@pytest.fixture(scope="module")
def py_arr_int():
    return {'ids':[1,2,3]}


def test_to_pg_array(arr):
    output = [x for x in arr if not x is None]
    assert len(output) == 3
    print(output)

def test_to_python_value(pg_arr):
    table = pg_arr.maketrans({'{': '', '}': '', '"': ''})
    output = [elem for elem in pg_arr.translate(table).split(',')]
    assert output
    assert all([isinstance(elem, str) for elem in output])

def test_str_arr_to_pg_types(py_arr_text):
    mapping = deepcopy(py_arr_text)
    for k,v in mapping.items():
        if v and isinstance(v, list):
            if all(v):
                v = json.dumps(v)
                mapping[k] = v.replace('[', '{').replace(']', '}').replace('"','')
            else:
                mapping[k] = 'NULL'
    assert mapping == {'ids': '{a:aa, b:bb, v:vv}'}

def test_int_arr_to_pg_types(py_arr_int):
    mapping = deepcopy(py_arr_int)
    for k,v in mapping.items():
        if v and isinstance(v, list):
            v = json.dumps(v)
            mapping[k] = v.replace('[', '{').replace(']', '}')
    assert mapping == {'ids': '{1, 2, 3}'}