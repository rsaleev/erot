


def test_full_unpacking():
    l = [i for i in range(10)]
    single, *others = l
    assert single == l[0]
    assert others == l[1:]


def test_partial_unpacking():
    l = [1]
    single, *others = l
    assert single == l[0]
    assert not others