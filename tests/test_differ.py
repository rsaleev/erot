import pytest
import dictdiffer

from collections import namedtuple



def test_diff_output():

    DiffObject = namedtuple('DiffObject', ['new', 'old'])
    output = []
    d1= {'id':1, 'value':'a'}
    d2 = {'id':1, 'value':'b'}
    result = dictdiffer.diff(d1, d2)
    for r in result:
        diff_type, diff_key, diff_values = r
        if diff_type == 'change':
            output.append(DiffObject(old={diff_key:diff_values[0]}, new={diff_key:diff_values[1]}))
    assert len(output) >0
    assert type(output[0]) is DiffObject

