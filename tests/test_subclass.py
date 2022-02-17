import pytest


@pytest.fixture(autouse=True)
def set_up():
    class A:
        pass

    class B(A):
        pass

    return A, B


def test_subclass(set_up):
    A, B = set_up
    print('B',dir(B))