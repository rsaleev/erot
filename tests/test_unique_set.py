import pytest

from dataclasses import dataclass




def test_unique_value():

    @dataclass
    class Test:
        id:int 
        model:str
        
    l = []
    for i in range(10):
        l.append(Test(i, 'TestModel'))
    result, = tuple(set([t.model for t in l]))
    assert result == 'TestModel'