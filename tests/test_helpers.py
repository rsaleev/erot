from copy import deepcopy

from typing import Any, Dict, List, Union

import pytest


def python_arr_to_pg(arg:Any)->Union[str, Any]:
    if isinstance(arg, List):
        v = fr'{arg}'
        return v.replace('[', '{').replace(']', '}').replace("'", "")
    return arg

def test_prepare_pg_query():
    kwargs = {'a':1, 'b':['a', 'b', 'c']}
    query_data = deepcopy(kwargs)
    for k,v in  query_data.items():
        query_data[k] = python_arr_to_pg(v)
    return query_data
    