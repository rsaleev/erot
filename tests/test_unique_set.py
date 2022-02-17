import pytest

from dataclasses import dataclass

from typing import List, Deque, ChainMap, Any, Dict, Set

from collections import deque

def chainmap_unique(arr:List[Dict[str, Any]]):
    unique_keys:Set[str] = set([next(k for k in tuple(elem.keys())) for elem in arr])
    deque_arr:Deque = deque(arr)
    last_keys = []
    output = []
    container = []
    while deque_arr:
        key = next(k for k in tuple(deque_arr[0].keys()))
        if not key in last_keys:
            container.append(deque_arr[0])
            deque_arr.popleft()
            last_keys.append(key)
        else:
            if all([k in unique_keys for k in last_keys]):
                d = dict(ChainMap(*container))
                last_keys.clear()
                container.clear()
                output.append(d)
            else:
                continue
    else:
        d = dict(ChainMap(*container))
        last_keys.clear()
        container.clear()
        output.append(d)
    # assert result
    return output

def test_one():
    l = [{'a':1}, {'b':2}, {'c':6},  {'a':3}, {'b':4},{'c':8}]

    result = chainmap_unique(l)
    assert result == [{'c': 6, 'b': 2, 'a': 1}, {'c': 8, 'b': 4, 'a': 3}]

def test_two():
    l =  [{'a':1}, {'b':2}, {'c':6}, {'d':9}, {'a':3}, {'b':4},{'c':8}, {'d':10}]

    result = chainmap_unique(l)

    assert result == [{'d':9, 'c': 6, 'b': 2, 'a': 1}, {'d':10, 'c': 8, 'b': 4, 'a': 3}]
